"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""

import numpy as np
from ...utils.units import V
from ...backend.file_handler import rmv_ext
from .FEM import *

from .mesh_creator.NerveMshCreator import *
from .fenics_utils.FEMSimulation import *
from.fenics_utils.SimResult import *

# built in FENICS models
dir_path = os.environ['NRVPATH'] + '/_misc'
material_library = os.listdir(dir_path+'/fenics_templates/')

###############
## Constants ##
###############
machine_config = configparser.ConfigParser()
config_fname = dir_path + '/NRV.ini'
machine_config.read(config_fname)

FENICS_Ncores = machine_config.get('FENICS', 'FENICS_CPU')
FENICS_Status = machine_config.get('FENICS', 'FENICS_STATUS') == 'True'

fem_verbose = True


class FENICS_model(FEM_model):
    """
    A class for FENICS Finite Element Models, inherits from FEM_model.
    """
    def __init__(self, fname=None, Ncore=None, handle_server=False, elem=None):
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
        self.type = 'FENICS'
        
        # Default paramerters
        self.L = 5000
        self.y_c = 0
        self.z_c = 0
        self.Outer_D = 5       #mm
        self.Nerve_D = 250     #um
        self.N_fascicle = 0
        self.fascicles = {}
        self.Perineurium_thickness={}
        self.N_electrode = 0
        self.electrodes = {}
        self.Istim = 1e-3        #A

        self.Outer_mat = "saline"
        self.Epineurium_mat = "epineurium"
        self.Endoneurium_mat = "endoneurium_ranck"
        self.Perineurium_mat = "perineurium"

        self.default_fascicle = {"D":200, "y_c":0, "z_c":0, "res":20}
        self.default_electrode = {"elec_type":"LIFE", "x_c":self.L/2, "y_c":0, "z_c":0, "length":1000, "D":25, "res":3}

        # Mesh 
        self.mesh_file = fname
        self.mesh = None
        self.elem = elem
        if elem is None:
            self.elem = ('Lagrange', 2)

        # FEM 
        self.sim = []
        self.sim_res = []

        # Status
        self.mesh_file_status = not self.mesh_file is None
        self.is_sim_ready = False

        if not self.mesh_file_status:
            self.mesh = NerveMshCreator(Length=self.L, Outer_D=self.Outer_D, Nerve_D=self.Nerve_D,\
                y_c=self.y_c, z_c=self.z_c)




    def save(self, fname, type='msh'):
        """
        Save the changes to the model file. (Avoid for the overal weight of the package)
        """
        if self.is_computed:
                self.sim_res[0].save_sim_result(fname)
                self.sim_res[0].save_sim_result(fname, ftype='xdmf')
                E = 1
                while E <self.N_electrode:
                    self.sim_res[E].save_sim_result(fname)
                    self.sim_res[E].save_sim_result(fname, ftype='xdmf', overwrite=True)
                    E += 1

        elif self.is_meshed: 
            self.mesh_file = rmv_ext(fname)
            self.mesh.save(fname +'msh')

    def clear(self):
        """
        Clear the mesh and result section of the model
        """
        pass

    def close(self):
        """
        Close the FEM simulation and the FENICS link
        """
        pass

    def __del__(self):
        self.close()


    #############################
    ## Access model parameters ##
    #############################
    def get_parameters(self):
        """
        Get the  all the parameters in the model as a python dictionary.

        Returns
        -------
        list    : dict
            all parameters as dictionnaries in a list, names a keys, with corresponding values
        """
        param = {}
        param['L'] = self.L
        param['y_c'] = self.y_c
        param['z_c'] = self.z_c
        param['Outer_D'] = self.Outer_D
        param['Nerve_D'] = self.Nerve_D
        param['N_fascicle'] = self.N_fascicle
        param['fascicles'] = self.fascicles
        param['Perineurium_thickness'] = self.Perineurium_thickness
        param['N_electrode'] = self.N_electrode
        param['electrodes'] = self.electrodes
        
        param['Outer_mat'] = self.Outer_mat
        param['Epineurium_mat'] = self.Epineurium_mat
        param['Endoneurium_mat'] = self.Endoneurium_mat
        param['Perineurium_mat'] = self.Perineurium_mat
        
        param['Istim'] = self.Istim 
        return param
        
    def get_parameter(self, p_name):
        """
        Get a specific parameter

        Returns
        -------
        str
            value of the parameter as in FENICS (with unit)
        """
        pass

    def set_parameter(self, p_name, p_value):
        """
        Set a parameter to a desired value

        Parameters
        ----------
        p_name  : str
            parameter name in the FENICS model
        p_value : str
            parameter value as in FENICS, with unit
        """
        pass

    def _update_parameters(self):
        """
        Internal use only: updates all the parameters from the mesh
        """   
        param = self.mesh.get_parameters()
        self.L = param['L']
        self.y_c = param['y_c']
        self.z_c = param['z_c']
        self.Outer_D = param['Outer_D']
        self.Nerve_D = param['Nerve_D']
        self.N_fascicle = param['N_fascicle']
        self.fascicles = param['fascicles']
        self.N_electrode = param['N_electrode']
        self.electrodes = param['electrodes']


    ######################
    ## custom the model ##
    ######################

    def reshape_outerBox(self, Outer_D, res="default"):
        """
        Reshape the size of the FEM simulation outer box

        Parameters
        ----------
        outer_D : float
            FEM simulation outer box diameter, in mm, WARNING, this is the only parameter in mm !
        """
        if not self.mesh_file_status:
            self.mesh.reshape_outerBox(Outer_D, res)
            self._update_parameters()

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
            self.mesh.reshape_nerve(Nerve_D, Length, y_c, z_c, res)
            self._update_parameters()

    def reshape_fascicle(self, Fascicle_D, y_c=0, z_c=0, ID=None, Perineurium_thickness=5, res="default"):
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
            self._update_parameters()
            if ID is None:
                if self.Perineurium_thickness == {}:
                    ID = 0
                else:                                   ## To check when not all ID are fixed
                    ID = max(self.Perineurium_thickness) + 1
            self.Perineurium_thickness[ID] = Perineurium_thickness
        
    def add_electrode(self, elec_type, ID=None, res="default", **kwargs):
        """
        
        """
        if not self.mesh_file_status:
            self.mesh.add_electrode(elec_type=elec_type, ID=ID, res=res, **kwargs)


    ########################
    ## setup simulation ##
    ########################

    def setup_simulations(self):
        if self.is_meshed and not self.is_sim_ready:
            # For EIT change in for E in elec_patren:
            for E in range(self.N_electrode):
                active_elec = self.electrodes[E] 
                # SETTING DOMAINS
                sim = FEMSimulation(mesh_file=self.mesh_file,mesh=self.mesh, elem=self.elem)
                # Outerbox domain
                sim.add_domain(mesh_domain=0,mat_file=self.Outer_mat)
                # Nerve domain
                sim.add_domain(mesh_domain=2,mat_file=self.Epineurium_mat)
                for i in range(self.N_fascicle):
                    sim.add_domain(mesh_domain=10+(2*i),mat_file=self.Endoneurium_mat)
                # SETTING INTERNAL BOUNDARY CONDITION (for perineuriums)
                for i in self.fascicles:
                    thickness = self.Perineurium_thickness[i]
                    sim.add_inboundary(mesh_domain=11+(2*i),mat_file=self.Perineurium_mat, thickness=thickness, in_domains=[10+(2*i)])
                # SETTING BOUNDARY CONDITION
                # Ground (to the external ring of Outerbox)
                sim.add_boundary(mesh_domain=1, btype='Dirichlet', value=0)
                # Injected current from active electrode
                mesh_domain_3D = self.__find_elec_subdomain(active_elec)
                jstim = self.__find_elec_jstim(active_elec)
                sim.add_boundary(mesh_domain=101+(2*E), btype='Neuman', value=jstim, mesh_domain_3D=mesh_domain_3D)
                sim.prepare_sim()
                self.sim += [sim]
            self.is_sim_ready = True
            
    
    def set_materials(self, Outer_mat=None, Epineurium_mat=None, Endoneurium_mat=None, Perineurium_mat=None):
        """
            Set material files
        """
        if Outer_mat is not None:
            self.Outer_mat = Outer_mat
        if Epineurium_mat is not None:
            self.Epineurium_mat = Epineurium_mat
        if Endoneurium_mat is not None:
            self.Endoneurium_mat = Endoneurium_mat
        if Perineurium_mat is not None:
            self.Perineurium_mat = Perineurium_mat

    def __find_elec_subdomain(self, elec) -> int:
        """
            Internal use only: 
        """
        if elec["type"]=="LIFE":
            y_e, z_e = elec["kwargs"]['y_c'], elec["kwargs"]['z_c']
            for i in self.fascicles:
                fascicle = self.fascicles[i]
                d_f, y_f, z_f = fascicle["D"], fascicle["y_c"], fascicle["z_c"]
                if (y_e - y_f)**2 + (z_e - z_f)**2 < d_f**2:
                    return 10 + i
        else:
            return 0

    def __find_elec_jstim(self, elec, I=None) -> float:
        """
            Internal use only: 
        """ 
        # Unitary stimulation
        if I is None:
            if elec["type"] == "LIFE":
                d_e = elec["kwargs"]['D']
                l_e = elec["kwargs"]['length']
                S = pi*(d_e)*(l_e/m)
                jstim = self.Istim / S

        return jstim

    ###################
    ## Use the model ##
    ###################

    def get_meshes(self):
        """
        Get the different meshes implemented in the model

        Returns
        -------
        list
            list of meshes implemented in the FENICS model file
        """
        if self.is_meshed:
            self.mesh.visualize()

    def build_and_mesh(self):
        """
        Build the geometry and perform meshing process
        """
        if not self.mesh_file_status:
            self._update_parameters()
            if self.N_fascicle == 0:
                self.reshape_fascicle(Fascicle_D=self.default_fascicle['D'], y_c=self.default_fascicle['y_c'], z_c=self.default_fascicle['z_c'], res=self.default_fascicle['res'])
            if self.N_electrode == 0:
                self.add_electrode(elec_type=self.default_electrode['elec_type'], x_c=self.default_electrode['x_c'], y_c=self.default_electrode['y_c'], \
                    z_c=self.default_electrode['z_c'], length=self.default_electrode['length'], D=self.default_electrode['D'], res=self.default_electrode['res'])
            self._update_parameters()
            self.mesh.compute_mesh()
            self.is_meshed = True

    def solve(self):
        """
        Solve the model
        """
        if not self.is_sim_ready:
            self.setup_simulations()
        # For EIT change in for E in elec_patren:
        for E in range(self.N_electrode):
            self.sim_res +=[self.sim[E].solve()]
        self.is_computed = True

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
        if self.is_computed == True:
            line = [[x_, y, z] for x_ in x]
            if self.N_electrode==1 or (E < self.N_electrode and E >= 0):
                potentials =  self.sim_res[E].eval(line)*V
            else:
                potentials = []
                for E in range(self.N_electrode):
                    potentials += [self.sim_res[E].eval(line)]
                potentials = np.transpose(np.array(potentials)*V)
            return potentials
                


    def export(self, path=''):
        """
        Export the figures of the FENICS results and posprocess (in PNG format)

        Parameters
        ----------
        path    : str
            path address where to save graphics
        """
        pass