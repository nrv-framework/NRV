"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import configparser
import os
from ...backend.log_interface import rise_error, rise_warning, pass_info

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

###################
## Model classes ##
###################
class FEM_model():
    """
    A generic class for Finite Element models
    """
    def __init__(self, Ncore=None):
        """
        Creates a instance of FEM_model

        Parameters
        ----------
        Ncore   : int
            number of cores for computation. If None is specified, this number is taken from the NRV2.ini configuration file. Byu default set to None
        """
        self.Ncore = Ncore
        self.type = 'FEM'

        # Flags
        self.is_meshed = False
        self.is_computed = False