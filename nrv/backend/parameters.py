"""
Access and modify NRV Parameters
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

from ..fmod.FEM.mesh_creator.MshCreator import GMSH_Ncores, GMSH_Status

from .log_interface import LOG_Status, VERBOSITY_LEVEL



def get_nrv_verbosity():
    """
    get general verbosity level
    """
    global VERBOSITY_LEVEL
    return VERBOSITY_LEVEL


def set_nrv_verbosity(i):
    """
    set general verbosity level
    """
    global VERBOSITY_LEVEL
    VERBOSITY_LEVEL = i


def get_gmsh_ncore():
    """
    get gmsh core number
    """
    global GMSH_Ncores
    return GMSH_Ncores

def set_gmsh_ncore(n):
    """
    set gmsh core number
    """
    global GMSH_Ncores
    GMSH_Ncores = n