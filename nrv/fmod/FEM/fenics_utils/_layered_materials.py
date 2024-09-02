"""
NRV-fenics_materials class handling.
"""

import faulthandler
import os

import numpy as np

from ....backend._file_handler import json_dump, rmv_ext
from ....backend._log_interface import rise_warning
from ....utils._nrv_function import nrv_interp
from ..._materials import (
    is_mat,
    load_material,
    material,
    compute_effective_conductivity,
)
from ._f_materials import f_material, load_f_material

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

###############
## Functions ##
###############


def is_lay_mat(mat: object) -> bool:
    """
    check if an object is a fenics_material, return True if yes, else False

    Parameters
    ----------
    mat : object
        object to test

    Returns
    -------
    bool
        True it the type is a material object
    """
    return isinstance(mat, layered_material)


def get_sig_ap(sig_in, sig_lay, alpha_lay):
    """ """

    _alpha_lay = 1 / alpha_lay
    _alpha_in = 1 / (1 - 1 / _alpha_lay)
    _sig1 = sig_in * _alpha_in
    _sig2 = sig_lay * _alpha_lay
    return (_sig1 * _sig2) / (_sig1 + _sig2)


####################
## material class ##
####################
class layered_material(f_material):
    """
    a class for conductive material wh

    parameters
    ----------
    mat1     :material
        generate the fenics material from mat attribute

    mat2     :material
        generate the fenics material from mat attribute
    """

    def __init__(
        self, mat_in: any = None, mat_lay: any = None, alpha_lay: float = 0.01
    ):
        """
        initialisation of the fenics_material
        """
        super().__init__()
        self.mat_in = load_f_material(mat_in)
        self.mat_lay = load_f_material(mat_lay)

        self.alpha_lay = alpha_lay

    def is_isotropic(self) -> bool:
        return self.mat_in.is_isotropic() and self.mat_lay.is_isotropic()

    def is_function_defined(self) -> bool:
        return self.mat_in.is_func or self.mat_lay.is_func

    def set_frequency(self, freq: float, set_in: bool = False) -> None:
        self.mat_lay.set_frequency(freq)
        if set_in:
            self.mat_in.set_frequency(freq)
        else:
            self.mat_in.clear_frequency()

    @property
    def sigma(self):
        """
        get the contuvity of the material
        """
        return get_sig_ap(
            self.mat_in.sigma,
            self.mat_lay.sigma,
            self.alpha_lay,
        )
