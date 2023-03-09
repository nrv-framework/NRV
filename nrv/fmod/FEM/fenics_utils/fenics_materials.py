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
    check if an object is a material, return True if yes, else False

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



def mat_from_csv(f_material,kind="linear", dx=0.01, interpolator=None, dxdy=None,\
        scale=None, columns=[]):
    """
    Load a material by its name. if the name is in the NRV2 material librairy, the extention is
    automatically added.

    Parameters
    ----------
    f_material  : str
        either material name if the material is in the NRV2 Librairy or path to the corresponding\
        .mat material file
    """
    # load from librairy or from file
    fname = rmv_ext(f_material) + '.csv'

    data = np.loadtxt(fname, delimiter=',')
    X = data[0]
    Y = data[1]
    sigma_func = nrv_interp(X, Y, kind=kind, dx=dx, interpolator=interpolator, dxdy=dxdy,\
        scale=scale, columns=0)

    # creat material instance
    mat_obj = fenics_material()
    mat_obj.set_conductivity_function(sigma_func)

    return mat_obj

def load_fenics_material(f_material, **kwargs):
    """
    """
    if '.csv' in f_material:
        mat = mat_from_csv(f_material,**kwargs)
    else:
        mat = fenics_material(load_material(f_material))
    return mat



####################
## material class ##
####################
class fenics_material(material):
    """
    a class for material
    """
    def __init__(self, mat=None):
        """
        class suppose to simplify the use  
        """
        super().__init__()
        self.is_func = False
        self.sigma_func = None

        if is_mat(mat):
            self.name = mat.name 
            self.source = mat.source 
            self.isotrop_cond = mat.isotrop_cond
            self.sigma = mat.sigma
            self.sigma_xx = mat.sigma_xx
            self.sigma_yy = mat.sigma_yy
            self.sigma_zz = mat.sigma_zz



    ## Save and Load mehtods
    def save_fenics_material(self, save=False, fname='material.json'):
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
        if save:
            json_dump(mat_dic, fname)
        return mat_dic


    def load_fenics_material(self, data):
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


    def set_conductivity_function(self, sigma_func):
        """
        set the conductivity tensor for an anisotropic material

        Parameters
        ----------
        sigma_xx    : float
            conductivity along the x axis, in S/m
        sigma_yy    : float
            conductivity along the y axis, in S/m
        sigma_zz    : float
            conductivity along the z axis, in S/m
        """
        self.isotrop_cond = False
        self.is_func = True
        self.sigma_func = sigma_func
        

    def is_function_defined(self):
        """
        check that the material is isotropic or not, return true if isotropic, else false

        Returns
        -------
        bool    :
            True if the per
        """
        return self.is_func
    
    def get_fenics_sigma(self, domain, elem=("Discontinuous Lagrange", 1), UN=1):

        if self.is_isotropic():
            sigma = Constant(domain, ScalarType(self.sigma * UN))
        elif not self.is_func:
            sigma = as_tensor([\
                    [self.sigma_xx * UN, 0, 0],\
                    [0, self.sigma_yy * UN, 0],\
                    [0, 0, self.sigma_zz * UN],\
                    ])
        else:
            unit = Constant(domain, ScalarType(UN))
            Q = FunctionSpace(domain, elem)
            sigma = Function(Q)
            sigma.interpolate(self.sigma_func)
            sigma = sigma * unit
        return sigma
