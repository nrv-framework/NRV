"""
NRV-FEM
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from abc import abstractmethod
from ...backend.log_interface import rise_error, rise_warning, pass_info
from ...backend.NRV_Class import NRV_class
import time

###############
## Constants ##
###############
fem_verbose = True

###################
## Model classes ##
###################
class FEM_model(NRV_class):
    """
    A generic class for Finite Element models
    """
    @abstractmethod
    def __init__(self, Ncore=None):
        """
        Creates a instance of FEM_model

        Parameters
        ----------
        Ncore   : int
            number of cores for computation. If None is specified, this number is taken from the NRV2.ini configuration file. Byu default set to None
        """
        super().__init__()
        self.Ncore = Ncore
        self.type = 'FEM'

        # Timmers
        self.meshing_timer = 0
        self.preparing_timer = 0
        self.solving_timer = 0
        self.access_res_timer = 0

        # Flags
        self.is_meshed = False
        self.is_computed = False

    
    def get_timers(self, verbose=False):
        """
        
        """
        pass_info("mesh done in " + str(self.meshing_timer) + " s")
        pass_info("simulation prepared in " + str(self.preparing_timer) + " s")
        pass_info("simulation solved in " + str(self.solving_timer) + " s")
        pass_info("Time spent to access results " + str(self.access_res_timer) + " s")
        total_timer = self.meshing_timer + self.preparing_timer + self.solving_timer + self.access_res_timer
        pass_info("total duration " + str(total_timer) + " s")
        return self.meshing_timer, self.preparing_timer, self.solving_timer, total_timer
