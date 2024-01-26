"""
Access and modify NRV Parameters.
"""
import configparser
import os
# issue #38 See if this should be kept or not
try:
    from dolfinx import __version__ as vdolfinx
except:
    vdolfinx = "0.7.0"
# issue #38 ############
from .NRV_Singleton import NRV_singleton


class nrv_parameters(metaclass=NRV_singleton):
    """
    A class for NRV parameters used to gather parameters
    """

    def __init__(self):
        """
        Initialize the class for parameters
        """
        self.dir_path = os.environ["NRVPATH"] + "/_misc"
        self.config_fname = self.dir_path + "/NRV.ini"
        # See if this should be kept or not
        self.vdolfinx = self.__extract_vertion(vdolfinx)
        # ############
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

    def get_gmsh_ncore(self):
        """
        get gmsh core number
        """
        return self.GMSH_Ncores

    def set_gmsh_ncore(self, n):
        """
        set gmsh core number
        """
        self.GMSH_Ncores = n

        # issue #38 See if this should be kept or not
    def __extract_vertion(self, v: str) -> tuple:
        """
        internal use only: convert library version from str to tuple
        """
        ip1 = v.find(".")
        ip2 = v[ip1+1:].find(".") + ip1+1
        return (int(v[:ip1]), int(v[ip1+1:ip2]), int(v[ip2+1:]))

    def check_dolfinx_version(self, v: str) -> bool:
        """
        Return True if dolfinx version is higher or equal than version v

        Parameters
        ----------
        v   : str
            version to compare
        """
        vt = self.__extract_vertion(v)
        for i in range(3):
            if vt[i] != self.vdolfinx[i]:
                return vt[i] <= self.vdolfinx[i]
        return True
        # issue #38 ############

###########################
#   Parameter singleton   #
###########################

parameters = nrv_parameters()
