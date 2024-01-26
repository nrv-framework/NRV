"""
NRV-fenics_materials class handling.
"""
import faulthandler
import os

import numpy as np
from dolfinx.fem import Constant, Function, FunctionSpace
from petsc4py.PETSc import ScalarType
from ufl import as_tensor

from ....backend.file_handler import json_dump, rmv_ext
from ....backend.log_interface import rise_warning
from ....utils.nrv_function import nrv_interp
from ...materials import is_mat, load_material, material

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

# get the built-in material librairy
dir_path = os.environ["NRVPATH"] + "/_misc"

###############
## Functions ##
###############


def is_fen_mat(mat):
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
    return isinstance(mat, fenics_material)


def mat_from_interp(
    X, Y, kind="linear", dx=0.01, interpolator=None, dxdy=None, scale=None, columns=0
):
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
    mat_obj = fenics_material()
    mat_obj.set_conductivity_function(sigma_func)
    return mat_obj


def mat_from_csv(f_material, **kwargs):
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
    fname = rmv_ext(f_material) + ".csv"

    data = np.loadtxt(fname, delimiter=",")
    X = data[0]
    Y = data[1]

    return mat_from_interp(X, Y, **kwargs)


def load_fenics_material(X, **kwargs):
    """
    Return fenics material from an object X

    Parameters
    ----------
    X   : objects
        if material or fenics material returning the corresponding fenics material
        if float returns an isotropic fenics material with X as conductivity value
        if str finishing with .csv use mat_from_csv with kwargs
        if
        else return None
    """
    mat = None
    if is_fen_mat(X):
        mat = X
    elif is_mat(X):
        mat = fenics_material(X)
    elif isinstance(X, str):
        if ".csv" in X:
            mat = mat_from_csv(X, **kwargs)
        else:
            mat = fenics_material(load_material(X))
    elif isinstance(X, (float, int)):
        mat = fenics_material()
        mat.set_isotropic_conductivity(X)
    elif np.iterable(X):
        if len(X) == 2:
            mat = mat_from_interp(X[0], X[1], **kwargs)
        elif len(X) == 3:
            mat = fenics_material()
            mat.set_anisotropic_conductivity(X[0], X[1], X[2])
    return mat


####################
## material class ##
####################
class fenics_material(material):
    """
    A class of materials better suited to FEM resolution with fenics.
    It allows material parameters to be updated dynamically between FEM simulations,
    which reduces calculation speed and memory consumption.

    parameters
    ----------
    mat     :material
        generate the fenics material from mat attribute
    """

    def __init__(self, mat=None):
        """
        initialisation of the fenics_material
        """
        super().__init__()
        self.is_func = False
        self.sigma_func = None
        self.sigma_fen = None
        self.elem = ("Discontinuous Lagrange", 1)
        self.UN = 1

        if is_mat(mat):
            self.name = mat.name
            self.source = mat.source
            self.isotrop_cond = mat.isotrop_cond
            self.sigma = mat.sigma
            self.sigma_xx = mat.sigma_xx
            self.sigma_yy = mat.sigma_yy
            self.sigma_zz = mat.sigma_zz

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

    def save_fenics_material(self, save=False, fname="fenics_material.json"):
        rise_warning("save_fenics_material is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_fenics_material(self, data="fenics_material.json"):
        rise_warning("load_fenics_material is a deprecated method use load")
        self.load(data=data)

    def load_from_mat(self, mat):
        if is_mat(mat):
            self.name = mat.name
            self.source = mat.source
            self.isotrop_cond = mat.isotrop_cond
            self.sigma = mat.sigma
            self.sigma_xx = mat.sigma_xx
            self.sigma_yy = mat.sigma_yy
            self.sigma_zz = mat.sigma_zz
        if is_fen_mat(mat):
            self.is_func = mat.is_func
            self.sigma_func = mat.sigma_func

        else:
            rise_warning("Not an material nothing is load")
        self.update_fenics_sigma()

    def set_conductivity_function(self, sigma_func):
        """
        set the conductivity space function for an anisotropic material

        Parameters
        ----------
        sigma_xx    : func(X : array([3, N]))-> array([N])
            conductivity function in 3D space

        """
        self.isotrop_cond = False
        self.is_func = True
        self.sigma_func = sigma_func

    def is_function_defined(self):
        """
        check that the material conductivity is define as a function

        Returns
        -------
        bool    :
            True if the per
        """
        return self.is_func

    def get_fenics_sigma(
        self, domain, elem=("Discontinuous Lagrange", 1), UN=1, id=None
    ):
        """
        Returns fenicsx compatible sigma
        """
        self.update_fenics_sigma(domain, elem=elem, UN=UN, id=id)
        return self.sigma_fen

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
        if self.sigma_fen is None:
            # isotropic material: sigma set as a cst
            if self.is_isotropic():
                self.sigma_fen = Constant(domain, ScalarType(self.sigma * self.UN))
            # constant anisotropic material: sigma set as a tensor
            elif not self.is_func:
                self.sigma_fen = as_tensor(
                    [
                        [self.sigma_xx * self.UN, 0, 0],
                        [0, self.sigma_yy * self.UN, 0],
                        [0, 0, self.sigma_zz * self.UN],
                    ]
                )
            # function defined anisotropic material: sigma set as a product of a
            # function and a constant (unit coeficient)
            else:
                unit = Constant(domain, ScalarType(self.UN))
                Q = FunctionSpace(domain, self.elem)
                self.sigma_fen = Function(Q)
                self.sigma_fen.interpolate(self.sigma_func)
                self.sigma_fen.name = "f" + name
                self.sigma_fen = self.sigma_fen * unit
        # Sigma value has already been set into fencis FEM model
        else:
            # isotropic material: sigma set as a constant
            if self.is_isotropic():
                self.sigma_fen.value = self.sigma * self.UN
            # constant anisotropic material: sigma set as a tensor
            elif not self.is_func:
                self.sigma_fen = as_tensor(
                    [
                        [self.sigma_xx * self.UN, 0, 0],
                        [0, self.sigma_yy * self.UN, 0],
                        [0, 0, self.sigma_zz * self.UN],
                    ]
                )
            # function defined anisotropic material: sigma set as a
            # product of a function and a constant (unit coeficient)
            else:
                # test required because after version "0.6.0" of dolfinx, ufl_operands
                # are sorted by constant then function regardless the order of creation
                if isinstance(self.sigma_fen.ufl_operands[0], Constant):
                    self.sigma_fen.ufl_operands[0].value = self.UN
                    self.sigma_fen.ufl_operands[1].interpolate(self.sigma_func)
                else:
                    self.sigma_fen.ufl_operands[0].interpolate(self.sigma_func)
                    self.sigma_fen.ufl_operands[1].value = self.UN
