"""
NRV-fenics_materials class handling.
"""

import faulthandler
import os

import numpy as np

from ....backend._file_handler import json_dump, rmv_ext
from ....backend._log_interface import rise_warning
from ....utils._nrv_function import nrv_interp, nrv_function
from ..._materials import (
    is_mat,
    load_material,
    material,
    compute_effective_conductivity,
)

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()


####################
## material class ##
####################
class f_material(material):
    """
    a class for conductive material wh

    parameters
    ----------
    mat     :material
        generate the fenics material from mat attribute
    """

    def __init__(self):
        """
        initialisation of the fenics_material
        """
        super().__init__()
        self._sigma_func = None

    ## Save and Load mehtods
    def save(self, save=False, fname="Fenics_model.json", blacklist=[], **kwargs):
        """
        Return material as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "material.json"

        Returns
        -------
        mat_dic : dict
            dictionary containing all information
        """
        bl = [i for i in blacklist]
        bl += ["sigma_func"]
        return super().save(save=save, fname=fname, blacklist=bl, **kwargs)

    @property
    def is_func(self):
        return not self._sigma_func is None

    @property
    def sigma(self):
        if self.is_func:
            return self.sigma_func
        else:
            return super().sigma

    @property
    def sigma_func(self):
        return compute_effective_conductivity(
            sigma=self._sigma_func, epsilon=self.epsilon, freq=self.freq
        )

    def set_conductivity_function(self, sigma_func: nrv_function) -> None:
        """
        set the conductivity space function for an anisotropic material

        Parameters
        ----------
        sigma_fuction    : func(X : array([3, N]))-> array([N])
            conductivity function in 3D space
        """
        self.isotrop_cond = False
        self._sigma_func = sigma_func

    def is_function_defined(self) -> bool:
        """
        check that the material conductivity is define as a function

        Returns
        -------
        bool    :
            True if the per
        """
        return self.is_func


###############
## Functions ##
###############


def is_f_mat(mat: object) -> bool:
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
    return isinstance(mat, f_material)


def mat_from_interp(
    X, Y, kind="linear", dx=0.01, interpolator=None, dxdy=None, scale=None, columns=0
) -> f_material:
    """
    Return a fenics material with a conductivity space function define as the
    :class:`~nrv.utils.nrv_function.nrv_interp` of X and Y

    Parameters
    ----------
    f_material  : str
        either material name if the material is in the NRV2 Librairy or path to the corresponding
        .mat material file
    kwargs      : dict
        interpolation k arguments (see :class:`~nrv.utils.nrv_function.nrv_interp`)

    Returns
    -------
    mat_obj     : fenics_material
        Fenics material with conductivity function defined from the interpolation
    """
    sigma_func = nrv_interp(
        X,
        Y,
        kind=kind,
        dx=dx,
        interpolator=interpolator,
        dxdy=dxdy,
        scale=scale,
        columns=columns,
    )

    # creat material instance
    mat_obj = f_material()
    mat_obj.set_conductivity_function(sigma_func)
    return mat_obj


def mat_from_csv(fname: str, **kwargs) -> f_material:
    """
    Return a fenics material with a conductivity space function define as the
    :class:`~nrv.utils.nrv_function.nrv_interp` from the value of a .csv file

    Parameters
    ----------
    f_material  : str
        name of the .csv file

    Returns
    -------
    mat_obj     : fenics_material
        Fenics material with conductivity function defined from the interpolation from the
        value of f_material file
    """
    fname = rmv_ext(fname) + ".csv"

    data = np.loadtxt(fname, delimiter=",")
    X = data[0]
    Y = data[1]

    return mat_from_interp(X, Y, **kwargs)


def load_f_material(X: any = None, **kwargs) -> f_material:
    """
    Return fenics material from an object X

    Parameters
    ----------
    X   : objects
        if material or fenics material returning the corresponding fenics material
        if float returns an isotropic fenics material with X as conductivity value
        if str finishing with .csv use mat_from_csv with kwargs
        else return None
    """
    mat = None
    if X is None:
        mat = f_material()
    elif is_f_mat(X):
        mat = X
    elif is_mat(X):
        mat = f_material()
        mat.load(X.save(save=False))
    elif isinstance(X, str):
        if ".csv" in X:
            mat = mat_from_csv(X, **kwargs)
        else:
            mat = f_material()
            mat.load(load_material(X).save(save=False))
    elif isinstance(X, (complex, float, int)):
        mat = f_material()
        mat.set_isotropic_conductivity(X)
    elif np.iterable(X):
        if len(X) == 2:
            mat = mat_from_interp(X[0, :], X[1, :], **kwargs)
        elif len(X) == 3:
            mat = f_material()
            mat.set_anisotropic_conductivity(X[0], X[1], X[2])
    elif hasattr(X, "mat"):
        mat = load_f_material(X.mat)
    if mat is None:
        rise_warning(
            TypeError(),
            f"{type(X)} not convertible in f_material\n",
            "empty material generated",
        )
        mat = f_material()
    return mat
