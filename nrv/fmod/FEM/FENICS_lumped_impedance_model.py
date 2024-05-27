"""
NRV-:class:`.FENICS_model` handling.
"""

import configparser
import os
import time

import numpy as np
from mpi4py import MPI

from ...backend.file_handler import rmv_ext
from ...utils.units import V, mm
from ...utils.misc import get_perineurial_thickness
from ...backend.MCore import MCH, synchronize_processes
from .fenics_utils.FEMSimulation import FEMSimulation

from .FENICS_model import FENICS_model
from .fenics_utils.FEMResults import save_sim_res_list
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


class FENICS_lumped_impedance_model(FENICS_model):
    """
    A class for FENICS Finite Element Models, inherits from FENICS_model.
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
        super().__init__(
            fname=fname,
            Ncore=Ncore,
            handle_server=handle_server,
            elem=elem,
            comm=comm,
            rank=rank,
        )

        self.axons = {}
        self.axons_gmem = {}

        self.Myeline_mat = "endoneurium_ranck"
        self.Axoplasmic_mat = 1 / 70

    def reshape_axon(
        self,
        d,
        y=0,
        z=0,
        ID=None,
        myelinated=False,
        res="default",
        res_node="default",
        **kwargs
    ):
        if not self.mesh_file_status:
            self.mesh.reshape_axon(
                d=d,
                y=y,
                z=z,
                ID=ID,
                myelinated=myelinated,
                res=res,
                res_node=res_node,
                **kwargs
            )
            self.__update_parameters()

    ######################
    ## setup simulation ##
    ######################
    def __set_domains(self):
        super().__set_domains()
        for i in self.axons.keys():
            self.sim.add_domain(
                mesh_domain=ENT_DOM_offset["Axons"] + (2 * i),
                mat_pty=self.Endoneurium_mat,
            )

    def __set_iboundaries(self):
        """
        Internal use only: set internam boundaries
        """
        for i in self.fascicles:
            thickness = self.Perineurium_thickness[i]
            f_dom = ENT_DOM_offset["Fascicle"] + (2 * i)
            self.sim.add_inboundary(
                mesh_domain=ENT_DOM_offset["Surface"] + f_dom,
                mat_pty=self.Perineurium_mat,
                thickness=thickness,
                in_domains=[f_dom],
            )

    def set_materials(
        self,
        Outer_mat=None,
        Epineurium_mat=None,
        Endoneurium_mat=None,
        Perineurium_mat=None,
        Electrodes_mat=None,
        Myeline_mat=None,
        Axoplasmic_mat=None,
    ):
        super().set_materials(
            Outer_mat, Epineurium_mat, Endoneurium_mat, Perineurium_mat, Electrodes_mat
        )
        self.Myeline_mat = Myeline_mat or self.Myeline_mat
        self.Axoplasmic_mat = Axoplasmic_mat or self.Axoplasmic_mat

    def set_axon_membrane(id, gmem_pty):
        pass

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
                    Fascicle_D=self.default_fascicle["d"],
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
                    d=self.default_electrode["d"],
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
                self.sim.setup_sim(**self.j_electrode)
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
