"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import configparser
import os
import time

import numpy as np
from mpi4py import MPI

from ...backend.file_handler import rmv_ext
from ...utils.units import V, mm
from ...backend.MCore import MCH, synchronize_processes
from .fenics_utils.FEMSimulation import FEMSimulation

from .FEM import FEM_model
from .fenics_utils.SimResult import save_sim_res_list
from .mesh_creator.NerveMshCreator import NerveMshCreator, ENT_DOM_offset, pi

# built in FENICS models
dir_path = os.environ["NRVPATH"] + "/_misc"
# material_library = os.listdir(dir_path+"/fenics_templates/")

###############
## Constants ##
###############
machine_config = configparser.ConfigParser()
config_fname = dir_path + "/NRV.ini"
machine_config.read(config_fname)

FENICS_Ncores = int(machine_config.get("FENICS", "FENICS_CPU"))
FENICS_Status = machine_config.get("FENICS", "FENICS_STATUS") == "True"

fem_verbose = True


class FENICS_model(FEM_model):
    """
    A class for FENICS Finite Element Models, inherits from FEM_model.
    """

    def __init__(
        self,
        fname=None,
        Ncore=None,
        handle_server=False,
        elem=None,
        comm="default",
        rank=0,
    ):
        """
        Creates a instance of a FENICS Finite Element Model object.

        Parameters
        ----------
        fname   : str
            path to the mesh file (.msh) file
        Ncore   : int
            number of FENICS cores for computation. If None is specified, this number is taken from the NRV2.ini configuration file. Byu default set to None
        handle_server   : bool
            if True, the instantiation creates the server, else a external server is used. Usefull for multiple cells sharing the same model
        """
        super().__init__(Ncore=Ncore)
        self.type = "FENICS"
        # Default paramerters
        self.L = 5000
        self.y_c = 0
        self.z_c = 0
        self.Outer_D = 5  # mm
        self.Nerve_D = 250  # um
        self.N_fascicle = 0
        self.fascicles = {}
        self.Perineurium_thickness = {}
        self.N_electrode = 0
        self.electrodes = {}
        self.Istim = 1e-3  # A
        self.jstims = []
        self.j_electrode = {}

        self.Outer_mat = "saline"
        self.Epineurium_mat = "epineurium"
        self.Endoneurium_mat = "endoneurium_ranck"
        self.Perineurium_mat = "perineurium"
        self.Electrodes_mat = 1  # "platinum"

        self.default_fascicle = {"D": 200, "y_c": 0, "z_c": 0, "res": 20}
        self.default_electrode = {
            "elec_type": "LIFE",
            "x_c": self.L / 2,
            "y_c": 0,
            "z_c": 0,
            "length": 1000,
            "D": 25,
            "res": 3,
        }

        # Mesh
        self.mesh_file = fname
        self.mesh = None
        self.elem = elem
        if elem is None:
            self.elem = ("Lagrange", 2)

        # FEM
        self.sim = None
        self.sim_res = []

        # Mcore attributes
        if self.Ncore is None:
            self.Ncore = FENICS_Ncores
        self.comm = None
        self.set_Ncore(self.Ncore)
        if comm != "default":
            self.comm = comm
        self.rank = rank

        # Status
        self.mesh_file_status = not self.mesh_file is None
        self.is_sim_ready = False
        self.is_meshed = False
        self.is_computed = False

        if not self.mesh_file_status:
            self.mesh = NerveMshCreator(
                Length=self.L,
                Outer_D=self.Outer_D,
                Nerve_D=self.Nerve_D,
                y_c=self.y_c,
                z_c=self.z_c,
            )

    def save(self, save=False, fname="Fenics_model.json", blacklist=[], **kwargs):
        """
        Save the changes to the model file. (Avoid for the overal weight of the package)
        """
        bl = [i for i in blacklist]
        bl += ["comm", "rank", "mesh", "sim", "sim_res"]
        return super().save(save=save, fname=fname, blacklist=bl, **kwargs)

    def save_results(self, save=False, fname="Fenics_model.json"):
        """
        Save the changes to the model file. (Avoid for the overal weight of the package)
        """
        if self.is_computed:
            save_sim_res_list(self.sim_res, fname)

        elif self.is_meshed:
            self.mesh_file = rmv_ext(fname)
            self.mesh.save(fname)

    def load(self, data="extracel_context.json", **kwargs):
        """
        Load all extracellular context properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing extracel_context information
        """
        bl = ["comm", "rank", "mesh", "sim", "sim_res"]
        super().load(data=data, blacklist=bl, **kwargs)
        param = self.get_parameters()
        self.load_from_parameters(**param)

    def load_from_parameters(self, **param):
        """ """
        self.reset_parameters()
        self.reshape_outerBox(param["Outer_D"])
        self.reshape_nerve(
            Nerve_D=param["Nerve_D"],
            Length=param["L"],
            y_c=param["y_c"],
            z_c=param["z_c"],
        )
        for id in param["fascicles"]:
            fasc = param["fascicles"][id]
            per_th = param["Perineurium_thickness"][id]
            self.reshape_fascicle(
                fasc["D"],
                y_c=fasc["y_c"],
                z_c=fasc["z_c"],
                ID=int(id),
                Perineurium_thickness=per_th,
                res=fasc["res"],
            )
        for id in param["electrodes"]:
            elec = param["electrodes"][id]
            self.add_electrode(
                elec_type=elec["type"], ID=int(id), res=elec["res"], **elec["kwargs"]
            )

    #############################
    ## Access model parameters ##
    #############################
    def set_Ncore(self, N):
        """
        Set the number of cores to use for the FEM

        Parameters
        ----------
        N       : int
            Number of cores to set
        """
        super().set_Ncore(N)
        if self.is_multi_proc:
            self.comm = MPI.COMM_WORLD
        else:
            self.comm = MPI.COMM_SELF

    def get_parameters(self):
        """
        Get the  all the parameters in the model as a python dictionary.

        Returns
        -------
        param    : dict
            all parameters as dictionnaries in a list, names a keys, with corresponding values
        """
        param = {}
        param["L"] = self.L
        param["y_c"] = self.y_c
        param["z_c"] = self.z_c
        param["Outer_D"] = self.Outer_D / mm
        param["Nerve_D"] = self.Nerve_D
        param["N_fascicle"] = self.N_fascicle
        param["fascicles"] = self.fascicles
        param["Perineurium_thickness"] = self.Perineurium_thickness
        param["N_electrode"] = self.N_electrode
        param["electrodes"] = self.electrodes
        param["Outer_mat"] = self.Outer_mat
        param["Epineurium_mat"] = self.Epineurium_mat
        param["Endoneurium_mat"] = self.Endoneurium_mat
        param["Perineurium_mat"] = self.Perineurium_mat
        param["Perineurium_mat"] = self.Perineurium_mat
        param["Istim"] = self.Istim
        return param

    def __update_parameters(self, bcast=False):
        """
        Internal use only: updates all the parameters from the mesh

        Parameters
        ----------
        bcast       : bool
            if true the parameters are updated on all process
        """
        if MCH.do_master_only_work():
            if bcast:
                self.__update_parameters(bcast=False)
                param = self.get_parameters()
            else:
                param = self.mesh.get_parameters()
        else:
            param = None
        if bcast:
            param = MCH.master_broadcasts_array_to_all(param)
        if MCH.do_master_only_work() ^ bcast:
            for key in param:
                self.__dict__[key] = param[key]

    def reset_parameters(self):
        """
        reset model parameters
        """
        self.L = 5000
        self.y_c = 0
        self.z_c = 0
        self.Outer_D = 5  # mm
        self.Nerve_D = 250  # um
        self.N_fascicle = 0
        self.fascicles = {}
        self.Perineurium_thickness = {}
        self.N_electrode = 0
        self.electrodes = {}
        self.Istim = 1e-3  # A
        self.jstims = []
        self.j_electrode = {}

        self.mesh_file_status = self.mesh_file is not None
        self.is_sim_ready = False
        self.is_meshed = False
        self.is_computed = False
        del self.mesh
        if not self.mesh_file_status:
            if MCH.do_master_only_work:
                self.mesh = NerveMshCreator(
                    Length=self.L,
                    Outer_D=self.Outer_D,
                    Nerve_D=self.Nerve_D,
                    y_c=self.y_c,
                    z_c=self.z_c,
                )
            else:
                self.mesh = None

    #####################
    ## customize model ##
    #####################
    def reshape_outerBox(self, Outer_D, res="default"):
        """
        Reshape the size of the FEM simulation outer box

        Parameters
        ----------
        outer_D : float
            FEM simulation outer box diameter, in mm, WARNING, this is the only parameter in mm !
        """
        if not self.mesh_file_status:
            self.mesh.reshape_outerBox(Outer_D=Outer_D, res=res)
            self.__update_parameters()

    def reshape_nerve(self, Nerve_D, Length, y_c=0, z_c=0, res="default"):
        """
        Reshape the nerve of the FEM simulation

        Parameters
        ----------
        Nerve_D                 : float
            Nerve diameter, in um
        Length                  : float
            Nerve length, in um
        y_c                     : float
            Nerve center y-coordinate in um, 0 by default
        z_c                     : float
            Nerve z-coordinate center in um, 0 by default
        Perineurium_thickness   :float
            Thickness of the Perineurium sheet surounding the fascicles in um, 5 by default
        """
        if not self.mesh_file_status:
            self.L = Length
            self.Nerve_D
            self.mesh.reshape_nerve(
                Nerve_D=Nerve_D, Length=Length, y_c=y_c, z_c=z_c, res=res
            )
            self.__update_parameters()

    def reshape_fascicle(
        self, Fascicle_D, y_c=0, z_c=0, ID=None, Perineurium_thickness=5, res="default"
    ):
        """
        Reshape a fascicle of the FEM simulation

        Parameters
        ----------
        Fascicle_D  : float
            Fascicle diameter, in um
        y_c         : float
            Fascicle center y-coodinate in um, 0 by default
        z_c         : float
            Fascicle center y-coodinate in um, 0 by default
        ID          : int
            If the simulation contains more than one fascicles, ID number of the fascicle to reshape as in FENICS
        """
        if not self.mesh_file_status:
            self.mesh.reshape_fascicle(Fascicle_D, y_c, z_c, ID, res)
            self.__update_parameters()
            if ID is None:
                if self.Perineurium_thickness == {}:
                    ID = 0
                else:  ## To check when not all ID are fixed
                    ID = max(self.Perineurium_thickness) + 1
            self.Perineurium_thickness[ID] = Perineurium_thickness

    def remove_fascicles(self, ID=None):
        """
        remove a fascicle of the FEM simulation

        Parameters
        ----------
        ID          : int, None
            ID number of the fascicle to remove, if None, remove all fascicles, by default None
        """
        if ID is None:
            self.fascicles = {}
            self.Perineurium_thickness = {}
            self.N_fascicle = 0
        elif ID in self.fascicles:
            del self.fascicles[ID]
            del self.Perineurium_thickness[ID]
            self.N_fascicle -= 1
        self.mesh.remove_fascicles(ID=ID)

    def add_electrode(self, elec_type, ID=None, res="default", **kwargs):
        """
        TO BE WRITTEN
        """
        if not self.mesh_file_status:
            self.mesh.add_electrode(elec_type=elec_type, ID=ID, res=res, **kwargs)

    ######################
    ## setup simulation ##
    ######################
    def setup_simulations(self, comm=None, rank=None):
        """
        TO BE WRITTEN
        """
        if comm is not None:
            self.comm = comm
        if rank is not None:
            self.rank = rank
        if not self.is_meshed:
            self.build_and_mesh()
        if not self.is_sim_ready and (MCH.do_master_only_work() or self.is_multi_proc):
            t0 = time.time()
            # SETTING DOMAINS
            # del self.mesh
            self.sim = FEMSimulation(
                mesh_file=self.mesh_file,
                mesh=self.mesh,
                elem=self.elem,
                comm=self.comm,
                rank=self.rank,
            )
            # Outerbox domain
            self.sim.add_domain(
                mesh_domain=ENT_DOM_offset["Outerbox"], mat_pty=self.Outer_mat
            )
            # Nerve domain
            self.sim.add_domain(
                mesh_domain=ENT_DOM_offset["Nerve"], mat_pty=self.Epineurium_mat
            )
            for i in self.fascicles.keys():
                self.sim.add_domain(
                    mesh_domain=ENT_DOM_offset["Fascicle"] + (2 * i),
                    mat_pty=self.Endoneurium_mat,
                )
            for _, (i, elec) in enumerate(self.electrodes.items()):
                if not elec["type"] == "LIFE":
                    self.sim.add_domain(
                        mesh_domain=ENT_DOM_offset["Electrode"] + (2 * i),
                        mat_pty=self.Electrodes_mat,
                    )
            # SETTING INTERNAL BOUNDARY CONDITION (for perineuriums)
            for i in self.fascicles:
                thickness = self.Perineurium_thickness[i]
                f_dom = ENT_DOM_offset["Fascicle"] + (2 * i)
                self.sim.add_inboundary(
                    mesh_domain=ENT_DOM_offset["Surface"] + f_dom,
                    mat_pty=self.Perineurium_mat,
                    thickness=thickness,
                    in_domains=[f_dom],
                )
            # SETTING BOUNDARY CONDITION
            # Ground (to the external ring of Outerbox)
            self.sim.add_boundary(mesh_domain=1, btype="Dirichlet", value=0)
            # Injected current from active electrode
            # For EIT change in for E in elec_patren:
            for _, (E, active_elec) in enumerate(self.electrodes.items()):
                E_var = "E" + str(E)
                mesh_domain_3D = self.__find_elec_subdomain(active_elec)
                self.jstims += {self.__find_elec_jstim(active_elec)}
                self.j_electrode[E_var] = 0
                e_dom = (
                    ENT_DOM_offset["Surface"] + ENT_DOM_offset["Electrode"] + (2 * E)
                )
                self.sim.add_boundary(
                    mesh_domain=e_dom,
                    btype="Neuman",
                    variable=E_var,
                    mesh_domain_3D=mesh_domain_3D,
                )
            # set a parallelizable preconditionner if sim solve on multiple precesses
            if self.is_multi_proc:
                self.sim.set_solver_opt(pc_type="hypre")
            self.is_sim_ready = True
            self.preparing_timer += time.time() - t0

    def set_materials(
        self,
        Outer_mat=None,
        Epineurium_mat=None,
        Endoneurium_mat=None,
        Perineurium_mat=None,
        Electrodes_mat=None,
    ):
        """
        Set material files for any domain
        Outer_mat       :str
            Outer box material fname if None not changed, by default None
        Epineurium_mat      :str
            Epineurium material fname if None not changed, by default None
        Endoneurium_mat     :str
            Endoneurium material fname if None not changed, by default None
        Perineurium_mat     :str
            Outer material fname if None not changed, by default None
        Electrodes_mat      :str
            Electrodes material fname if None not changed, by default None
        """
        if Outer_mat is not None:
            self.Outer_mat = Outer_mat
        if Epineurium_mat is not None:
            self.Epineurium_mat = Epineurium_mat
        if Endoneurium_mat is not None:
            self.Endoneurium_mat = Endoneurium_mat
        if Perineurium_mat is not None:
            self.Perineurium_mat = Perineurium_mat
        if Electrodes_mat is not None:
            self.Electrodes_mat = Electrodes_mat

    def __find_elec_subdomain(self, elec) -> int:
        """
        Internal use only:
        """
        if elec["type"] == "LIFE":
            y_e, z_e = elec["kwargs"]["y_c"], elec["kwargs"]["z_c"]
            for i in self.fascicles:
                fascicle = self.fascicles[i]
                d_f, y_f, z_f = fascicle["D"], fascicle["y_c"], fascicle["z_c"]
                if (y_e - y_f) ** 2 + (z_e - z_f) ** 2 < (d_f / 2) ** 2:
                    return 10 + 2 * i
        return 0

    def __find_elec_jstim(self, elec, I=None) -> float:
        """
        Internal use only: return electrical current density in electrode
        from current valeu and electrode geometry
        """
        # Unitary stimulation
        if I is not None:
            self.Istim = I

        if elec["type"] == "CUFF":
            d_e = self.Nerve_D + 2 * elec["kwargs"]["contact_thickness"]
            l_e = elec["kwargs"]["contact_length"]

        elif elec["type"] == "LIFE":
            d_e = elec["kwargs"]["D"]
            l_e = elec["kwargs"]["length"]

        S = pi * (d_e) * (l_e)
        jstim = self.Istim / S
        return jstim

    ###################
    ## Use the model ##
    ###################

    def get_meshes(self):
        """
        Visualize the model mesh
        WARNING: debbug use only + might not work on all os
        """
        if self.is_meshed:
            self.mesh.visualize()

    def build_and_mesh(self):
        """
        Build the geometry and perform meshing process
        """
        if not self.mesh_file_status and not self.is_meshed:
            t0 = time.time()
            self.__update_parameters()
            if self.N_fascicle == 0:
                self.reshape_fascicle(
                    Fascicle_D=self.default_fascicle["D"],
                    y_c=self.default_fascicle["y_c"],
                    z_c=self.default_fascicle["z_c"],
                    res=self.default_fascicle["res"],
                )
            if self.N_electrode == 0:
                self.add_electrode(
                    elec_type=self.default_electrode["elec_type"],
                    x_c=self.default_electrode["x_c"],
                    y_c=self.default_electrode["y_c"],
                    z_c=self.default_electrode["z_c"],
                    length=self.default_electrode["length"],
                    D=self.default_electrode["D"],
                    res=self.default_electrode["res"],
                )
            self.__update_parameters(bcast=self.is_multi_proc)
            if MCH.do_master_only_work():
                self.mesh.compute_mesh()
            if self.is_multi_proc:
                synchronize_processes()
            self.is_meshed = True
            self.mesh.get_info(verbose=True)
            self.meshing_timer += time.time() - t0

    def solve(self, comm=None, rank=None):
        """
        Solve the model
        """
        if not self.is_sim_ready:
            self.setup_simulations()
        if not self.is_computed:
            t0 = time.time()
            # For EIT change in for E in elec_patren:
            for E in range(self.N_electrode):
                for i_elec in self.j_electrode:
                    if i_elec == "E" + str(E):
                        self.j_electrode[i_elec] = self.jstims[E]
                    else:
                        self.j_electrode[i_elec] = 0
                self.sim.prepare_sim(**self.j_electrode)
                self.sim_res += [self.sim.solve()]
                self.sim_res[-1].vout.label = "E" + str(E)
            self.is_computed = True
            self.solving_timer += time.time() - t0

    ######################
    ## results handling ##
    ######################

    def get_potentials(self, x, y, z, E=-1):
        """
        Get the potential on a line to get extracellular potential for axons stimulation.

        Parameters
        ----------
        x   : np.array
            array of x coordinates in the model
        y   : float
            y-coordinate of the axon
        z   : float
            z-coordinate of the axon
        E   : int
            ID of the electrode from witch the potentials should be evaluated

        Returns:
        --------
        array
            All potential for all paramtric sweeps (all electrodes in NRV2 models)\
            (line: electrode selection, column: potential)
        """
        if self.is_computed:
            t0 = time.time()
            line = [[x_, y, z] for x_ in x]
            if self.N_electrode == 1 or (E < self.N_electrode and E >= 0):
                potentials = self.sim_res[E].eval(line, self.is_multi_proc) * V
            else:
                potentials = []
                for E in range(self.N_electrode):
                    potentials += [self.sim_res[E].eval(line, self.is_multi_proc)]
                potentials = np.transpose(np.array(potentials) * V)
            self.access_res_timer += time.time() - t0
            return potentials
