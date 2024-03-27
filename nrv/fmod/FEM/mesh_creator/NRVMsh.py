"""
NRV-:class:`.NerveMshCreator` handling.
"""
from cmath import phase
import numpy as np

from ....backend.NRV_Class import NRV_class
from ....backend.log_interface import rise_error, rise_warning
from ....nmod.myelinated import myelinated
from ....utils.units import mm
from ....backend.file_handler import rmv_ext
from .NerveMshCreator import NerveMshCreator, pi

ENT_DOM_offset = {
    "Volume": 0,
    "Surface": 1,
    "Outerbox": 0,
    "Nerve": 2,
    "Fascicle": 10,
    "Electrode": 100,
    "Axon": 1000,
}

ELEC_TYPES = ["CUFF MP", "CUFF", "LIFE"]


def is_NRVMsh(object):
    """
    check if an object is a NerveMshCreator, return True if yes, else False

    Parameters
    ----------
    result : object
        object to test

    Returns
    -------
    bool
        True it the type is a NerveMshCreator object
    """
    return isinstance(object, NRVMsh)


class NRVMsh(NerveMshCreator):
    """
    Class allowing to generate Nerve shape 3D gmsh mesh with labeled physical domain
    Contains methodes dealing with the mesh geometries, physical domains and feilds
    Inherit from MshCreator class. see MshCreator for further detail
    """

    def __init__(
        self,
        Length=10000,
        Outer_D=5,
        Nerve_D=4000,
        y_c=0,
        z_c=0,
        ver_level=2,
    ):
        """
        initialisation of the NerveMshCreator

        Parameters
        ----------
        Length          : float
            Nerve length in um, by default 10000
        Outer_D         : float
            Outer box diameter in mm, by default 5
        Nerve_D         : float
            Nerve diameter in um, by default 4000
        y_c             : float
            y-axis position of the Nerve center, by default 0
        z_c             : float
            z-axis position of the Nerve center, by default 0
        ver_level       : int(0,1,2,3,4,5,99)
            verbosity level of gmsh (see MshCreator.set_verbosity), by default 2
        """
        super().__init__(
            Length=Length,
            Outer_D=Outer_D,
            Nerve_D=Nerve_D,
            y_c=y_c,
            z_c=z_c,
            ver_level=ver_level,
        )

    def reshape_entity(self, obj):
        """
        """