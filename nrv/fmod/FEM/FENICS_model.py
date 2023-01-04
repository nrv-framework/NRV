"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""

import numpy as np
import mph
from ...utils.units import V
from .FEM import *

# built in COMSOL models
dir_path = os.environ['NRVPATH'] + '/_misc'
material_library = os.listdir(dir_path+'/comsol_templates/')

###############
## Constants ##
###############
machine_config = configparser.ConfigParser()
config_fname = dir_path + '/NRV.ini'
machine_config.read(config_fname)
COMSOL_Ncores = machine_config.get('COMSOL', 'COMSOL_CPU')
COMSOL_Status = machine_config.get('COMSOL', 'COMSOL_STATUS') == 'True'

fem_verbose = True

class FENICS_model(FEM_model):
    """
    A class for COMSOL Finite Element Models, inherits from FEM_model.
    """
    def __init__(self, fname, Ncore=None, handle_server=False):
        """
        Creates a instance of a COMSOL Finite Element Model object.

        Parameters
        ----------
        fname   : str
            path to the COMSOL (.mph) model file
        Ncore   : int
            number of COMSOL cores for computation. If None is specified, this number is taken from the NRV2.ini configuration file. Byu default set to None
        handle_server   : bool
            if True, the instantiation creates the server, else a external server is used. Usefull for multiple cells sharing the same model
        """
        pass


    def save(self):
        """
        Save the changes to the model file. (Avoid for the overal weight of the package)
        """
        pass

    def clear(self):
        """
        Clear the mesh and result section of the model
        """
        pass

    def close(self):
        """
        Close the FEM simulation and the COMSOL link
        """
        #self.client.disconnect()
        pass


    #############################
    ## Access model parameters ##
    #############################
    def get_parameters(self):
        """
        Get the  all the parameters in the model as a python dictionary.

        Returns
        -------
        list
            all parameters as dictionnaries in a list, names a keys, with corresponding values
        """
        pass

    def get_parameter(self, p_name):
        """
        Get a specific parameter

        Returns
        -------
        str
            value of the parameter as in COMSOL (with unit)
        """
        pass

    def set_parameter(self, p_name, p_value):
        """
        Set a parameter to a desired value

        Parameters
        ----------
        p_name  : str
            parameter name in the COMSOL model
        p_value : str
            parameter value as in COMSOL, with unit
        """
        pass

    ###################
    ## Use the model ##
    ###################
    def get_meshes(self):
        """
        Get the different meshes implemented in the model

        Returns
        -------
        list
            list of meshes implemented in the COMSOL model file
        """
        pass

    def build_and_mesh(self):
        """
        Build the geometry and perform meshing process
        """
        pass

    def solve(self):
        """
        Solve the model
        """
        pass
    ######################
    ## results handling ##
    ######################
    def get_potentials(self, x, y, z):
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

        Returns:
        --------
        array
            All potential for all paramtric sweeps (all electrodes in NRV2 models)\
            (line: electrode selection, column: potential)
        """
        pass

    def export(self, path=''):
        """
        Export the figures of the COMSOL results and posprocess (in PNG format)

        Parameters
        ----------
        path    : str
            path address where to save graphics
        """
        pass