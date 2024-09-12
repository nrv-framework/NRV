"""
NRV-fenics_materials class handling.
"""

import faulthandler
import os

import numpy as np
from dolfinx.fem import Constant, Function, functionspace
from petsc4py.PETSc import ScalarType
from ufl import as_tensor

from ....backend._file_handler import json_dump, rmv_ext
from ....backend._log_interface import rise_warning
from ....backend._NRV_Class import NRV_class
from ....backend._parameters import parameters
from ....utils._nrv_function import nrv_interp
from ..._materials import is_mat, load_material
from ._f_materials import load_f_material

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

# get the built-in material librairy
dir_path = parameters.nrv_path + "/_misc"


####################
## material class ##
####################
class fenics_material(NRV_class):
    """
    A class of materials better suited to FEM resolution with fenics.
    It allows material parameters to be updated dynamically between FEM simulations,
    which reduces calculation speed and memory consumption.

    parameters
    ----------
    mat     :material
        generate the fenics material from mat attribute
    """

    def __init__(self, mat: any = None):
        """
        initialisation of the fenics_material
        """
        super().__init__()
        self.mat = load_f_material(mat)
        self._sigma_fen = None
        self.elem = ("Discontinuous Lagrange", 1)
        self.UN = 1

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
        bl += ["sigma_fen"]
        return super().save(save=save, fname=fname, blacklist=bl, **kwargs)

    def update_mat(self, mat):
        self.mat = load_f_material(mat)
        self.update_fenics_sigma()

    @property
    def sigma_fen(self):
        return self._sigma_fen

    @property
    def sigma(self):
        """
        conductivity of the material scaled by `UN` factor.

        Warning
        -------
        `fenics_material.sigma` and `fenics_material.mat.sigma` are not always equal
        as `fenics_material.sigma` is scaled by `UN`
        """
        return self.mat.sigma * self.UN

    def get_fenics_sigma(
        self, domain, elem=("Discontinuous Lagrange", 1), UN=1, id=None
    ):
        """
        Returns fenicsx compatible sigma
        """
        self.update_fenics_sigma(domain, elem=elem, UN=UN, id=id)
        return self._sigma_fen

    def update_fenics_sigma(self, domain=None, elem=None, UN=None, id=None):
        """
        Update sigma value of a material in fenics FEM simulation.
        Allow to reuse the same material when FEM_simulation object is solved multiple times.

        Parameters
        ----------
        domain      : dolfinx.mesh.Mesh or None
            mesh domain of the FEM simulation
        elem        : tupple (str, int)
            element type, element order, by default None
        UN          : int or None
            unit factor to use for to scale the material value,
            if None, keep the UN attribute of the instance
        id          :
            ID to use to name the ufl object
        """
        if id is None:
            name = ""
        else:
            name = "_" + str(id)
        if elem is not None:
            self.elem = elem
        if UN is not None:
            self.UN = UN
        # First declaration in fenics model (Sigma value has not been set into model)
        _sig = self.sigma
        if self._sigma_fen is None:
            # isotropic material: sigma set as a cst
            if self.mat.is_isotropic():
                self._sigma_fen = Constant(domain, ScalarType(_sig))
            # constant anisotropic material: sigma set as a tensor
            elif not self.mat.is_function_defined():
                self._sigma_fen = as_tensor(
                    [
                        [_sig[0], 0, 0],
                        [0, _sig[1], 0],
                        [0, 0, _sig[2]],
                    ]
                )
            # function defined anisotropic material: sigma set as a product of a
            # function and a constant (unit coeficient)
            else:
                Q = functionspace(domain, self.elem)
                self._sigma_fen = Function(Q)
                self._sigma_fen.interpolate(_sig)
                self._sigma_fen.name = "f" + name
        # Sigma value has already been set into fencis FEM model
        else:
            # isotropic material: sigma set as a constant
            if self.mat.is_isotropic():
                self._sigma_fen.value = _sig
            # constant anisotropic material: sigma set as a tensor
            elif not self.mat.is_function_defined():
                self._sigma_fen = as_tensor(
                    [
                        [_sig[0], 0, 0],
                        [0, _sig[1], 0],
                        [0, 0, _sig[2]],
                    ]
                )
            else:
                self._sigma_fen.interpolate(_sig)
