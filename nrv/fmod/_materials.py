"""
NRV-:class:`.material` handling.
"""

import faulthandler
import os
import numpy as np
from scipy.constants import pi, epsilon_0

from ..backend._log_interface import rise_warning
from ..backend._NRV_Class import NRV_class
from ..backend._parameters import parameters

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

# get the built-in material librairy
dir_path = parameters.nrv_path + "/_misc"
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
    if "epsilon_r" in mat_file:
        mat_obj.set_permitivity(mat_file["epsilon_r"])
    return mat_obj


def compute_effective_conductivity(sigma: float, epsilon: float, freq: float) -> float:
    r"""
    return the effective conductivity of the material.
    Two cases are psooible:

        - purely conductive material (when both `epsilon` or `freq` are set)

        .. math:: \sigma_{eff} = \sigma

        - dielectric material at a fixe frequency:

        .. math:: \sigma_{eff} = |\sigma+2j\pi f\epsilon_0\epsilon_r|

    Parameters
    ----------
    sigma   : float
        conductivity
    """
    if epsilon is None or freq is None:
        return sigma
    return abs(sigma + 2j * pi * freq * epsilon_0 * epsilon)


####################
## material class ##
####################
class material(NRV_class):
    """
    a class for material, where all the physical properties constants are stored.

    by default materials in NRV are considerated as purely conductive. Yet,
    """

    def __init__(self):
        """
        material instantiation
        """
        super().__init__()
        self.name = ""
        self.source = ""

        # Conduction properties
        self.isotrop_cond = True
        self._sigma = 0
        self._sigma_xx = 0
        self._sigma_yy = 0
        self._sigma_zz = 0
        self._sigma_func = None

        # permitivity property
        self.epsilon = None
        self.freq = None

    @property
    def sigma(self):
        """
        get the conductivity of the material
        """
        if not self.is_isotropic():
            return np.array([self.sigma_xx, self.sigma_yy, self.sigma_zz])
        return compute_effective_conductivity(
            sigma=self._sigma, epsilon=self.epsilon, freq=self.freq
        )

    @property
    def sigma_xx(self) -> float:
        """
        get the conductivity of the material along ox
        """
        if self.isotrop_cond:
            rise_warning("Isotropic conductor sigma_xx is sigma")
            return self.sigma
        return compute_effective_conductivity(
            sigma=self._sigma_xx, epsilon=self.epsilon, freq=self.freq
        )

    @property
    def sigma_yy(self) -> float:
        """
        get the conductivity of the material along oy
        """
        if self.isotrop_cond:
            rise_warning("Isotropic conductor sigma_yy is sigma")
            return self.sigma
        return compute_effective_conductivity(
            sigma=self._sigma_yy, epsilon=self.epsilon, freq=self.freq
        )

    @property
    def sigma_zz(self) -> float:
        """
        get the conductivity of the material along oz
        """
        if self.isotrop_cond:
            rise_warning("Isotropic conductor sigma_zz is sigma")
            return self.sigma
        return compute_effective_conductivity(
            sigma=self._sigma_zz, epsilon=self.epsilon, freq=self.freq
        )

    def save_material(self, save=False, fname="material.json"):
        rise_warning("save_material is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_material(self, data="material.json"):
        rise_warning("load_material is a deprecated method use load")
        self.load(data=data)

    def set_name(self, name: str) -> None:
        """
        set a name to a material

        Parameters
        ----------
        name :  str
            name of the material
        """
        self.name = name

    def set_source(self, source: str) -> None:
        """
        set a source to a material. Note that this source is a string without spaces

        Parameters
        ----------
        source  : str
            scientific reference to the value, for clarity only
        """
        self.source = source

    def set_isotropic_conductivity(self, sigma: float | complex) -> None:
        """
        set the conductivity for an isotropic material

        Parameters
        ----------
        sigma   : float
            conductivity in S/m
        """
        self.isotrop_cond = True
        if isinstance(sigma, complex):
            self._sigma = sigma
        else:
            self._sigma = float(sigma)

    def set_anisotropic_conductivity(
        self, sigma_xx: float, sigma_yy: float, sigma_zz: float
    ) -> None:
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
        self._sigma_xx = float(sigma_xx)
        self._sigma_yy = float(sigma_yy)
        self._sigma_zz = float(sigma_zz)

    def is_isotropic(self) -> bool:
        """
        check that the material is isotropic or not, return true if isotropic, else false

        Returns
        -------
        bool    :
            True if the per
        """
        return self.isotrop_cond

    ## Permitivity relatied methods
    def set_permitivity(self, epsilon: float) -> None:
        """
        set the relative permitivity of the material.

        Note
        ----
        The relative permetivity is used to compute an apparent conductivity at a frequency
        when ``freq``-attribute is set.

        Parameters
        ----------
        epsilon   : float
            relative permetivity in F/m
        """
        self.epsilon = float(epsilon)

    def set_frequency(self, freq: float) -> None:
        """
        set the frequency of the electric field in the material

        Parameters
        ----------
        freq   : float
            frequency of the fields in to set in kHz
        """
        self.freq = float(freq)

    def clear_frequency(self) -> None:
        """
        set the woking frequency to None

        Parameters
        ----------
        freq   : float
            frequency of the fields in to set in kHz
        """
        self.freq = None

    def is_permitive(self):
        """
        check if the material permitivity and the electric field frequency are set
        """
        return self.epsilon is not None and self.freq is not None
