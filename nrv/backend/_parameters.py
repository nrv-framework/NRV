"""
Access and modify NRV Parameters.
"""

import configparser
import os
from ._NRV_Singleton import NRV_singleton
from pathlib import Path
from multiprocessing import Process, current_process, parent_process, active_children, Lock

is_master_proc = current_process().name=="MainProcess"

class nrv_parameters(metaclass=NRV_singleton):
    """
    A class for NRV parameters used to gather parameters
    """

    def __init__(self):
        """
        Initialize the class for parameters
        """
        if type(self) in nrv_parameters._instances:
            self = self._instances[type(self)]
        else:
            self.nrv_path = str(Path(os.path.dirname(__file__)).parent.absolute()) 
            self.dir_path = self.nrv_path + "/_misc"
            self.config_fname = self.dir_path + "/NRV.ini"
            self.load()

    def save(self):
        """
        Saving the parameters
        """
        with open(self.config_fname, "w") as configfile:
            self.machine_config.write(configfile)

    def load(self, fname=None):
        """
        Loading the parameters
        """
        if fname is None:
            fname = self.config_fname

        self.machine_config = configparser.ConfigParser()
        self.machine_config.read(self.config_fname)

        # GMSH
        self.GMSH_Ncores = int(self.machine_config.get("GMSH", "GMSH_CPU"))
        self.GMSH_Status = self.machine_config.get("GMSH", "GMSH_STATUS") == "True"
        # nmod
        self.nmod_Ncores = int(self.machine_config.get("NRV", "NMOD_CPU"))
        # optim
        self.optim_Ncores = int(self.machine_config.get("OPTIM", "OPTIM_CPU"))

        # LOG
        self.LOG_Status = self.machine_config.get("LOG", "LOG_STATUS") == "True"
        self.VERBOSITY_LEVEL = int(self.machine_config.get("LOG", "VERBOSITY_LEVEL"))

    def get_nrv_verbosity(self):
        """
        get general verbosity level
        """
        return self.VERBOSITY_LEVEL

    def set_nrv_verbosity(self, i):
        """
        set general verbosity level
        Parameters
        ----------
        O: None
        1: + Error
        2: + Warning
        3: + Info
        4: + Debug
        NB: to add Debug verbosity to the log VERBOSITY_LEVEL has to be set to 4
        """
        self.VERBOSITY_LEVEL = i


    ############################
    # Multi process parameters #
    ############################
    @property
    def is_alone(self):
        return current_process().name=="MainProcess" and len(active_children())==0
    
    @property
    def proc_label(self):
        return current_process().name

    def get_gmsh_ncore(self):
        """
        get gmsh core number
        """
        return self.GMSH_Ncores

    def set_gmsh_ncore(self, n:int):
        """
        set gmsh core number
        """
        self.GMSH_Ncores = n

    def get_nmod_ncore(self):
        """
        get nmod core number
        """
        return self.nmod_Ncores

    def set_nmod_ncore(self, n:int):
        """
        set nmod core number
        """
        self.nmod_Ncores = n

    def get_optim_ncore(self):
        """
        get optim core number
        """
        return self.optim_Ncores

    def set_optim_ncore(self, n:int):
        """
        set optim core number
        """
        self.optim_Ncores = n

    def set_ncores(self, n_nrv:int=None, n_nmod:int=None, n_gmsh:int=None,n_optim:int=None):
        """
        set for all subpakages core number

        Parameters
        ----------
        n_nmod : int, optional
            _description_, by default None
        n_gmsh : int, optional
            _description_, by default None
        n_optim : int, optional
            _description_, by default None
        """
        if n_nrv is not None:
            n_nmod = n_nrv
            n_gmsh = n_nrv
            n_optim = n_nrv
        if n_nmod is not None:
            self.set_nmod_ncore(n_nmod)
        if n_gmsh is not None:
            self.set_gmsh_ncore(n_gmsh)
        if n_optim is not None:
            self.set_optim_ncore(n_optim)


###########################
#   Parameter singleton   #
###########################

parameters = nrv_parameters()
