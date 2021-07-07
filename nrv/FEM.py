"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import configparser
import os
import numpy as np
import mph
import sys
from .units import V
from .log_interface import rise_error, rise_warning, pass_info

# built in COMSOL models
dir_path = os.path.dirname(os.path.realpath(__file__))
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

###################
## Model classes ##
###################
class FEM_model():
    """
    A generic class for Finite Element models
    """
    def __init__(self, fname):
        """
        Creates a instance of FEM_model

        Parameters
        ----------
        fname : str
            path to the model file
        """
        super(FEM_model, self).__init__()
        self.model_path = fname

#############################
## COMSOL Specific classes ##
#############################
class COMSOL_model(FEM_model):
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
        if COMSOL_Status:
            super().__init__(fname)
            f_in_librairy = str(fname) + '.mph'
            if f_in_librairy in material_library:
                self.fname = dir_path+'/comsol_templates/' + str(fname) + '.mph'
            else:
                self.fname = fname
            #self.model_path = fname
            if Ncore is None:
                self.Ncore = COMSOL_Ncores
            else:
                self.Ncore = Ncore
            self.handle_server = handle_server
            # start client and server
            pass_info('Starting COMSOL server/client, this may take few seconds')
            if self.handle_server:
                self.server = mph.Server(cores=self.Ncore)
            else:
                self.server = None
            self.client = mph.start(cores=self.Ncore)
            self.client.caching(True)
            print('... loading the COMSOL model')
            self.model = self.client.load(self.fname)
            #self.client.caching(True)
            # Flags
            self.is_meshed = False
            self.is_computed = False
            # source
            self.fname = fname
        else:
            ## COMSOL TURNED OFF, no error, but only a warning and no computation (exit)
            rise_warning('Bad implementation, a COMSOL simulation is implemented while NRV2 has COMSOL status turned OFF, unterminated computation, early exit without error', abort=True)


    def save(self):
        """
        Save the changes to the model file. (Avoid for the overal weight of the package)
        """
        self.model.save()

    def clear(self):
        """
        Clear the mesh and result section of the model
        """
        self.model.clear()
        self.model.reset()

    def close(self):
        """
        Close the FEM simulation and the COMSOL link
        """
        #self.client.disconnect()
        del self.client
        if self.handle_server:
            self.server.stop()
            del self.server


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
        return self.model.parameters()

    def get_parameter(self, p_name):
        """
        Get a specific parameter

        Returns
        -------
        str
            value of the parameter as in COMSOL (with unit)
        """
        return self.model.parameter(p_name)

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
        self.model.parameter(p_name, p_value)

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
        return self.model.meshes()

    def build_and_mesh(self):
        """
        Build the geometry and perform meshing process
        """
        pass_info('... Building model geometry')
        self.model.build()
        pass_info('... Meshing geometry')
        self.model.mesh()
        self.is_meshed = True

    def solve(self):
        """
        Solve the model
        """
        if not self.is_meshed:
            self.build_and_mesh()
        pass_info('... Solving model')
        self.model.solve()
        self.is_computed = True

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
        COMSOL_expressions = ['at3('+str(x[k])+'[um], '+str(y)+'[um], '+str(z)+'[um], V)' \
            for k in range(len(x))]
        Voltage = self.model.evaluate(COMSOL_expressions,dataset=self.model.datasets()[0])*V
        return np.asarray(Voltage)

    def export(self, path=''):
        """
        Export the figures of the COMSOL results and posprocess (in PNG format)

        Parameters
        ----------
        path    : str
            path address where to save graphics
        """
        exports = self.model.exports()
        for export in exports:
            self.model.export(export, path+export+'.png')
