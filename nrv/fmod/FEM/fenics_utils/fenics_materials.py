"""
NRV-fenics_materials
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import os
from dolfinx.fem import Function, FunctionSpace, Constant
from petsc4py.PETSc import ScalarType 
from ufl import as_tensor
import numpy as np


from ...materials import *
from ....utils.nrv_function import nrv_interp
from ....backend.log_interface import rise_error, rise_warning, pass_info
from ....backend.file_handler import json_dump, json_load, rmv_ext

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

# get the built-in material librairy
dir_path = os.environ['NRVPATH'] + '/_misc'

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



def mat_from_interp(X, Y, kind="linear", dx=0.01, interpolator=None, dxdy=None,\
        scale=None, columns=0):
    """
    Return a fenics material with a conductivity space function define as the nrv_interp of X and Y
    (see nrv_function for more details)

    Parameters
    ----------
    f_material  : str
        either material name if the material is in the NRV2 Librairy or path to the corresponding\
        .mat material file
    kwar
    """
    sigma_func = nrv_interp(X, Y, kind=kind, dx=dx, interpolator=interpolator, dxdy=dxdy,\
        scale=scale, columns=columns)

    # creat material instance
    mat_obj = fenics_material()
    mat_obj.set_conductivity_function(sigma_func)
    return mat_obj

def mat_from_csv(f_material, **kwargs):
    """
    Return a fenics material with a conductivity space function define as the nrv_interp from the 
    value of a .csv file

    Parameters
    ----------
    f_material  : str
        name of the .csv file

    """
    fname = rmv_ext(f_material) + '.csv'

    data = np.loadtxt(fname, delimiter=',')
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
        if '.csv' in X:
            mat = mat_from_csv(X,**kwargs)
        else:
            mat = fenics_material(load_material(X))
    elif isinstance(X, (float, int)):
        mat = fenics_material()
        mat.set_isotropic_conductivity(X)
    elif np.iterable(X):
        if len(X) == 2:
            mat = mat_from_interp(X[0], X[1], **kwargs)
        elif len(X)==3:
            mat = fenics_material()
            mat.set_anisotropic_conductivity(X[0], X[1], X[2])
    return mat



####################
## material class ##
####################
class fenics_material(material):
    """
    a class for material material more suited for the FEM solving with fenics
    Inherit from material class. see material for further detail
    """
    def __init__(self, mat=None):
        """
        initialisation of the fenics_material
        mat     :material
            generate the fenics material from mat attribute
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
    def save(self, save=False, fname='material.json'):
        """
        Return material as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default 'material.json'

        Returns
        -------
        mat_dic : dict
            dictionary containing all information
        """
        mat_dic = super().save_material(save=False, fname=fname)
        mat_dic['is_func'] = self.is_func
        mat_dic['sigma_func'] = self.sigma_func
        mat_dic['elem'] = self.elem
        mat_dic['UN'] = self.UN
        if save:
            json_dump(mat_dic, fname)
        return mat_dic


    def load(self, data):
        """
        Load all material properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing material information
        """
        if type(data) == str:
            mat_dic = json_load(data)
        else: 
            mat_dic = data
        super().load_material(data)
        self.is_func = mat_dic['is_func']
        self.sigma_func = mat_dic['sigma_func']
        self.is_func = mat_dic['is_func']
        self.sigma_func = mat_dic['sigma_func']
        self.elem = mat_dic['elem']
        self.UN = mat_dic['UN']
        self.update_fenics_sigma()

    def save_fenics_material(self, save=False, fname='fenics_material.json'):
        rise_warning('save_fenics_material is a deprecated method use save')
        self.save(save=save, fname=fname)
    def load_fenics_material(self, data='fenics_material.json'):
        rise_warning('load_fenics_material is a deprecated method use load')
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
            rise_warning('Not an material nothing is load')
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
    
    def get_fenics_sigma(self, domain, elem=("Discontinuous Lagrange", 1), UN=1, id=None):
        """
        Returns fenicsx compatible sigma
        """
        self.update_fenics_sigma(domain, elem=elem, UN=UN, id=id)
        return self.sigma_fen

    def update_fenics_sigma(self, domain=None, elem=None, UN=None, id=None):
        if id is None:
            name = ""
        else:
            name = "_"+str(id)
        if elem is not None:
            self.elem = elem
        if UN is not None:
            self.UN = UN
        if self.sigma_fen is None:
            if self.is_isotropic():
                self.sigma_fen = Constant(domain, ScalarType(self.sigma * self.UN))
            elif not self.is_func:
                self.sigma_fen = as_tensor([\
                        [self.sigma_xx * self.UN, 0, 0],\
                        [0, self.sigma_yy * self.UN, 0],\
                        [0, 0, self.sigma_zz * self.UN],\
                        ])
            else:
                unit = Constant(domain, ScalarType(self.UN))
                Q = FunctionSpace(domain, self.elem)
                self.sigma_fen = Function(Q)
                self.sigma_fen.interpolate(self.sigma_func)
                self.sigma_fen.name = "f" + name
                self.sigma_fen = self.sigma_fen * unit
        else:
            if self.is_isotropic():
                self.sigma_fen.value = self.sigma * self.UN

            elif not self.is_func:
                self.sigma_fen = as_tensor([\
                        [self.sigma_xx * self.UN, 0, 0],\
                        [0, self.sigma_yy * self.UN, 0],\
                        [0, 0, self.sigma_zz * self.UN],\
                        ])
            else:
                self.sigma_fen.ufl_operands[0].interpolate(self.sigma_func)
                self.sigma_fen.ufl_operands[1].value = self.UN
