"""
NRV-materials
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import os

from ..backend.log_interface import rise_warning
from ..backend.NRV_Class import NRV_class

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

# get the built-in material librairy
dir_path = os.environ["NRVPATH"] + "/_misc"
material_library = os.listdir(dir_path + "/materials/")

###############
## Functions ##
###############


def is_mat(mat):
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
    return isinstance(mat, material)


def get_mat_file_as_dict(fname):
    """
    Open .mat material librairy file and return all lines as a dictionnary

    Returns
    -------
    d   : dictionnary
        physical properties of the material
    """
    d = {}
    with open(fname, "r") as f:
        for line in f:
            (key, value) = line.split()
            d[key] = value
    return d


def load_material(f_material):
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
    f_in_librairy = str(f_material) + ".mat"
    if f_in_librairy in material_library:
        mat_file = get_mat_file_as_dict(dir_path + "/materials/" + f_in_librairy)
    else:
        mat_file = get_mat_file_as_dict(f_material)
    # creat material instance
    mat_obj = material()
    if "name" in mat_file:
        mat_obj.set_name(mat_file["name"])
    if "source" in mat_file:
        mat_obj.set_source(mat_file["source"])
    if "sigma_xx" in mat_file:
        mat_obj.set_anisotropic_conductivity(
            mat_file["sigma_xx"], mat_file["sigma_yy"], mat_file["sigma_zz"]
        )
    elif "sigma" in mat_file:
        mat_obj.set_isotropic_conductivity(mat_file["sigma"])
    else:
        rise_warning(
            "loading a material with 0 conductivity, \
            this may induce further division by 0"
        )
    return mat_obj


####################
## material class ##
####################
class material(NRV_class):
    """
    a class for material, where all the physical properties constants are stored.
    """

    def __init__(self):
        """
        material instantiation
        """
        super().__init__()
        self.name = ""
        self.source = ""
        self.isotrop_cond = True
        self.sigma = 0
        self.sigma_xx = 0
        self.sigma_yy = 0
        self.sigma_zz = 0

    def save_material(self, save=False, fname="material.json"):
        rise_warning("save_material is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_material(self, data="material.json"):
        rise_warning("load_material is a deprecated method use load")
        self.load(data=data)

    def set_name(self, name):
        """
        set a name to a material

        Parameters
        ----------
        name :  str
            name of the material
        """
        self.name = name

    def set_source(self, source):
        """
        set a source to a material. Note that this source is a string without spaces

        Parameters
        ----------
        source  : str
            scientific reference to the value, for clarity only
        """
        self.source = source

    def set_isotropic_conductivity(self, sigma):
        """
        set the conductivity for an isotropic material

        Parameters
        ----------
        sigma   : float
            conductivity in S/m
        """
        self.isotrop_cond = True
        self.sigma = float(sigma)

    def set_anisotropic_conductivity(self, sigma_xx, sigma_yy, sigma_zz):
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
        self.sigma_xx = float(sigma_xx)
        self.sigma_yy = float(sigma_yy)
        self.sigma_zz = float(sigma_zz)

    def is_isotropic(self):
        """
        check that the material is isotropic or not, return true if isotropic, else false

        Returns
        -------
        bool    :
            True if the per
        """
        return self.isotrop_cond
