"""
NRV-:class:`.fascicle` handling.
"""

import faulthandler
import os

import matplotlib.pyplot as plt
import numpy as np
#import multiprocessing as mp
from ..backend._NRV_Mproc import get_pool
from rich import progress

from ..backend._parameters import parameters
from ..backend._file_handler import *
from ..backend._log_interface import pass_info, rise_warning
from ..backend._NRV_Simulable import NRV_simulable
from ..backend._NRV_Class import load_any
from ..fmod._extracellular import *
from ..fmod._recording import *
from ..ui._axon_postprocessing import *
from ..backend._inouts import check_function_kwargs
from ._axons import *
from ._axon_pop_generator import *
from ._myelinated import *
from ._unmyelinated import *
from .results._fascicles_results import fascicle_results
from .results._axons_results import axon_results




# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()


builtin_postproc_functions = {
    "default": default_PP,
    "default_PP": default_PP,
    "rmv_keys": rmv_keys,
    "is_recruited": is_recruited,
    "is_blocked": is_blocked,
    "is_onset": is_blocked,
    "sample_keys": sample_keys,
    "vmem_plot": vmem_plot,
    "raster_plot": raster_plot,
}

deprecated_builtin_postproc_functions = {
    "is_excited": "is_recruited",
    "save_gmem": "sample_g_mem",
}

#####################
## Fasscicle class ##
#####################


def is_fascicle(object):
    """
    check if an object is a fascicle, return True if yes, else False

    Parameters
    ----------
    result : object
        object to test

    Returns
    -------
    bool
        True it the type is a fascicle object
    """
    return isinstance(object, fascicle)


class fascicle(NRV_simulable):
    r"""
    Class for Fascicle, defined as a group of axons near one to the other in the same Perineurium Sheath. All axons are independant of each other, no ephaptic coupling.


    See Also
    --------
    :doc:`Simulables users guide</usersguide/simulables>`, :class:`Nerve-class<._nerve.nerve>`, :class:`Axon-class<._axons.axon>`


    .. rubric:: Customizable Attributes:

    .. list-table::
       :widths: 10 10 10 70
       :header-rows: 1

       * - Attributes
         - Type
         - Default
         - Description
       * - ``ID``
         - ``int``
         - 0
         - Identification number of the fascicle.
       *
         - ``L``
         - ``float``
         - None
         - Length of the fascicle.
       *
         - ``D``
         - ``float``
         - None
         - Diameter of the fascicle.
       *
         - ``y_grav_center``
         - ``float``
         - 0
         - y-position of the fascicle center.
       *
         - ``z_grav_center``
         - ``float``
         - 0
         - z-position of the fascicle center.
       *
         - ``postproc_label``
         - ``str``
         - None
         - Label of the axon postprocessing funtion, used for the buildin postproc functions.
       *
         - ``postproc_function``
         - ``function``
         - None
         - Axon postprocessing funtion, used for the custom postproc functions.
       *
         - ``postproc_script``
         - ``str`` | ``function``
         - None
         - Either postprocessing funtion or postprocessing funtion label, automatically set depending on the type
       *
         - ``postproc_kwargs``
         - ``dict``
         - None
         - key arguments of the postporcessing function
       *
         - ``save_results``
         - ``bool``
         - False
         - If ``True``, fascicle configuration and all axon simulations results are saved in ``save_path`` directory.
       *
         - ``save_path``
         - ``str``
         - ""
         - Path of the directory where simulation results should be saved.
       *
         - ``return_parameters_only``
         - ``bool``
         - False
         - If ``True`` (and ``save_results`` also ``True``), only the parameters should be returned from the simulation.
       *
         - ``loaded_footprints``
         - ``bool``
         - False
         - If ``False``, the footprints already computed are favored over new footprint computation.
       *
         - ``verbose``
         - ``bool``
         - False
         - Plot or not.


    Note
    ----
    Customizable attributes can either be set using :meth:`.fascicle.set_parameters` or simply by reafecting the value of the attribute.

    Tip
    ---
    Additional simulation parameters can be changed using (:meth:`.fascicle.set_axons_parameters`, :meth:`.fascicle.change_stimulus_from_electrode`, ...).



    """

    def __init__(self, diameter=None, ID=0, **kwargs):
        """
        Instantation of a Fascicle
        """
        super().__init__(**kwargs)

        # to add to a fascicle/nerve common mother class

        #:str: path where the simulation results should be saved
        self.save_path:str = ""
        #:str: value: False: verbosity mainly for pbars. Tests more comment
        self.verbose = False 
        self.return_parameters_only = False
        self.loaded_footprints = False
        self.save_results = False
        self.result_folder_name:str = ""

        self.postproc_label = "default"
        self.postproc_function = None
        self.postproc_script = None
        self.postproc_kwargs = {}

        self.config_filename = ""
        self.ID = ID
        self.type = None
        self.L = None
        self.D = diameter
        # geometric properties
        self.y_grav_center = 0
        self.z_grav_center = 0

        # Update parameters with kwargs
        self.set_parameters(**kwargs)

        # axonal content
        self.axons_diameter = np.array([])
        self.axons_type = np.array([], dtype=int)
        self.axons_y = np.array([])
        self.axons_z = np.array([])
        self.NoR_relative_position = np.array([])
        # Axons objects default parameters
        self.unmyelinated_param = {
            "model": "Rattay_Aberham",
            "dt": 0.001,
            "Nrec": 0,
            "Nsec": 1,
            "Nseg_per_sec": 100,
            "freq": 100,
            "freq_min": 0,
            "mesh_shape": "plateau_sigmoid",
            "alpha_max": 0.3,
            "d_lambda": 0.1,
            "v_init": None,
            "T": None,
            "threshold": -40,
        }

        self.myelinated_param = {
            "model": "MRG",
            "dt": 0.001,
            "Nseg_per_sec": 3,
            "freq": 100,
            "freq_min": 0,
            "mesh_shape": "plateau_sigmoid",
            "alpha_max": 0.3,
            "d_lambda": 0.1,
            "rec": "nodes",
            "T": None,
            "threshold": -40,
        }
        self.set_axons_parameters(**kwargs)

        # extra-cellular stimulation
        self.extra_stim = None
        self.footprints = {}
        self.is_footprinted = False
        # intra-cellular stimulation
        self.N_intra = 0
        self.intra_stim_position = []
        self.intra_stim_t_start = []
        self.intra_stim_duration = []
        self.intra_stim_amplitude = []
        self.intra_stim_ON = []
        ## recording mechanism
        self.record = False
        self.recorder = None
        # Simulation status
        self.is_simulated = False

    ## save/load methods
    def save(
        self,
        fname="fascicle.json",
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        save=True,
        _fasc_save=True,
        blacklist=[],
    ):
        """
        Save a fascicle in a json file

        Parameters
        ----------
        fname :             str
            name of the file to save the fascicle
        extracel_context:   bool
            if True, add the extracellular context to the saving
        intracel_context:   bool
            if True, add the intracellular context to the saving
        rec_context:        bool
            if True, add the recording context to the saving
        blacklist:          list[str]
            key to exclude from saving
        save:               bool
            if false only return the dictionary

        Returns
        -------
        key_dict:           dict
            Python dictionary containing all the fascicle information
        """
        bl = [i for i in blacklist]
        to_save = (save and _fasc_save)

        bl += ["postproc_function", "postproc_script"]
        if self.postproc_label not in builtin_postproc_functions:
            rise_warning(
                "custom axon postprocessing cannot be save. Be carefull to set the postproc_function again when reloading fascicle"
            )

        if not intracel_context:
            bl += [
                "N_intra",
                "intra_stim_position",
                "intra_stim_t_start",
                "intra_stim_duration",
                "intra_stim_amplitude",
                "intra_stim_ON",
            ]

        if not extracel_context:
            bl += ["extra_stim", "footprints", "is_footprinted"]

        if not rec_context:
            bl += ["record", "recorder"]

        return super().save(fname=fname, save=to_save, blacklist=bl)

    def load(
        self,
        data,
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        blacklist=[],
    ):
        """
        Load a fascicle configuration from a json file

        Parameters
        ----------
        fname           : str
            path to the json file describing a fascicle
        extracel_context: bool
            if True, load the extracellular context as well
        intracel_context: bool
            if True, load the intracellular context as well
        rec_context: bool
            if True, load the recording context as well
        blacklist       : list[str]
            key to exclude from loading
        """
        if type(data) == str:
            key_dic = json_load(data)
        else:
            key_dic = data

        bl = [i for i in blacklist]
        if not intracel_context:
            bl += [
                "N_intra",
                "intra_stim_position",
                "intra_stim_t_start",
                "intra_stim_duration",
                "intra_stim_amplitude",
                "intra_stim_ON",
            ]

        if not extracel_context:
            bl += [
                "extra_stim",
                "footprints",
                "myelinated_nseg_per_sec",
                "unmyelinated_nseg",
                "is_footprinted",
            ]

        if not rec_context:
            bl += ["record", "recorder"]

        super().load(data=key_dic, blacklist=bl)
        if "unmyelinated_param" not in key_dic:
            rise_warning("Deprecated fascicle file")
            self.set_axons_parameters(key_dic)

    def save_fascicle_configuration(
        self, fname, extracel_context=False, intracel_context=False, rec_context=False
    ):
        rise_warning(
            "save_fascicle_configuration is a deprecated method use save instead"
        )
        self.save(
            fname=fname,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )

    def load_fascicle_configuration(
        self, fname, extracel_context=False, intracel_context=False, rec_context=False
    ):
        rise_warning(
            "load_fascicle_configuration is a deprecated method use load instead"
        )
        self.load(
            data=fname,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )

    ## Fascicle property method
    @property
    def n_ax(self):
        """
        Number of axons in the fascicle
        """
        return len(self.axons_diameter)

    @property
    def N(self):
        """
        :meta private:
        """
        rise_warning(
            "DeprecationWarning: ",
            "fascicle.N property is obsolete use fascicle.n_ax instead",
        )
        return self.n_ax

    @property
    def A(self):
        """
        Area of the fascicle
        """
        if self.D is None:
            return None
        return np.pi * (self.D / 2) ** 2

    def set_ID(self, ID):
        """
        set the ID of the fascicle

        Parameters
        ----------
        ID : int
            ID number of the fascicle
        """
        self.ID = ID

    def define_length(self, L):
        """
        set the length over the x axis of the fascicle

        Parameters
        ----------
        L   : float
            length of the fascicle in um
        """
        if self.extra_stim is not None or self.N_intra > 0:
            rise_warning(
                "Modifying length of a fascicle with extra or intra cellular context can lead to error"
            )
        self.L = L
        self.unmyelinated_param["Nseg_per_sec"] == self.L // 25

    ## generate stereotypic Fascicle
    def define_circular_contour(self, D, y_c=None, z_c=None):
        """
        Define a circular countour to the fascicle

        Parameters
        ----------
        D           : float
            diameter of the circular fascicle contour, in um
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        """
        self.type = "Circular"
        self.D = D
        if y_c is not None:
            self.y_grav_center = y_c
        if z_c is not None:
            self.z_grav_center = z_c

    def get_circular_contour(self):
        """
        Returns the properties of the fascicle contour considered as a circle (y and z center and diameter)

        Returns
        -------
        D : float
            diameter of the contour, in um. Set to 0 if not applicable
        y : float
            y position of the contour center, in um
        z : float
            z position of the contour center, in um
        """
        y = self.y_grav_center
        z = self.z_grav_center
        D = self.D
        return D, y, z

    def fit_circular_contour(self, y_c=None, z_c=None, delta=0.1, round_dgt=None):
        """
        Define a circular countour to the fascicle

        Parameters
        ----------
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        delta       : float
            distance between farest axon and contour, in um
        """
        rise_warning(
            "fit_circular_contour method usage is not recommended anymore and will be removed in future release."
        )
        pass_info("Define fascicle size/shape at object creation instead.")
        N_axons = len(self.axons_diameter)
        D = 2 * delta

        if y_c is not None:
            self.y_grav_center = y_c
        if z_c is not None:
            self.z_grav_center = z_c
        if N_axons == 0:
            pass_info("No axon to fit fascicul diameter set to " + str(D) + "um")
        else:
            dist_axons = np.linalg.norm((self.axons_y, self.axons_z), axis=0) + (self.axons_diameter/2)
            D = 2 * (dist_axons.max() + delta)
        if round is not None:
            D = round(D, round_dgt)
        self.define_circular_contour(D, y_c=None, z_c=None)

    def define_ellipsoid_contour(self, a, b, y_c=0, z_c=0, rotate=0):
        """
        Define ellipsoidal contour
        """
        pass

    ## generate Fascicle from histology
    def import_contour(self, smthing_else):
        """
        Define contour from a file
        """
        pass

    ## fill fascicle methods
    def fill(
        self,
        percent_unmyel=0.7,
        FVF=0.55,
        M_stat="Schellens_1",
        U_stat="Ochoa_U",
        ppop_fname=None,
        pop_fname=None,
    ):
        """
        Fill a geometricaly defined contour with axons

        Parameters
        ----------
        parallel        : bool
            if True, the generation process (quite long) is split over multiples cores, if False everything is perfrmed by the master.
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        FVF             : float
            Fiber Volume Fraction estimated for the area. By default set to 0.55
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition
        ppop_fname      : str
            optional, if specified, name file to store the placed population generated
        pop_fname       : str
            optional, if specified, name file to store the population generated
        """
        rise_warning(
            "fill method usage is not recommended anymore and will be removed in future release."
        )
        pass_info("Use axon_pop_generator methods instead.")
        #### AXON GENERATION: parallelization if resquested ####
        Area_to_fill = 0
        # Note: generate a bit too much axons just in case
        if self.type == "Circular":
            Area_to_fill = np.pi * (self.D / 2 + 28) ** 2
        (
            axons_diameter,
            axons_type,
            M_diam_list,
            U_diam_list,
        ) = fill_area_with_axons(
            Area_to_fill,
            percent_unmyel=percent_unmyel,
            FVF=FVF,
            M_stat=M_stat,
            U_stat=U_stat,
        )
        #### AXON PACKING: never parallel
        N = len(axons_diameter)
        pass_info("\n ... " + str(N) + " axons generated")
        if pop_fname is not None:
            save_axon_population(
                pop_fname, axons_diameter, axons_type, comment=None
            )
        (
            axons_y,
            axons_z,
        ) = axon_packer(
            axons_diameter,
            delta=0.1,
            y_gc=self.y_grav_center,
            z_gc=self.z_grav_center,
            n_iter=20000,
        )

        N = len(axons_diameter)
        # check if axons are inside the fascicle
        inside_axons = (
            np.power(axons_y - self.y_grav_center, 2)
            + np.power(axons_z - self.z_grav_center, 2)
            - np.power(np.ones(N) * (self.D / 2) - axons_diameter / 2, 2)
        )
        axons_to_keep = np.argwhere(inside_axons < 0)
        axons_diameter = axons_diameter[axons_to_keep]
        axons_type = axons_type[axons_to_keep]
        axons_y = axons_y[axons_to_keep]
        axons_z = axons_z[axons_to_keep]
        N = len(axons_diameter)
        # save the good population
        if ppop_fname is not None:
            save_axon_population(
                ppop_fname,
                self.axons_diameter,
                self.axons_type,
                self.axons_y,
                self.axons_z,
                comment=None,
            )


    def fill_with_population(
        self,
        axons_diameter: np.array,
        axons_type: np.array,
        delta: float = 1,
        y_axons: np.array = None,
        z_axons: np.array = None,
        fit_to_size: bool = False,
        n_iter: int = 20_000,
    ) -> None:
        """
        Fill the fascicle with an axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        delta               : float
            axon-to-axon and axon to border minimal distance
        y_axons             : np.array
            y coordinate of the axon population, in um
        z_axons             : np.array
            z coordinate of the axons population, in um
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        WARNING: If y_axons and z_axons are not specified then axon-packing algorithm is called within the method.
        """
        N = len(axons_diameter)
        if (y_axons is None) and (z_axons is None):
            y_axons, z_axons = axon_packer(
                axons_diameter, delta=delta, n_iter=n_iter
            )
        if fit_to_size:
            if self.D is not None:
                d_pop = get_circular_contour(
                    axons_diameter, y_axons, z_axons, delta
                )
                if (d_pop) < self.D:
                    exp_factor = 0.99 * (self.D / d_pop)
                    y_axons, z_axons = expand_pop(y_axons, z_axons, exp_factor)
            else:
                rise_warning(
                    "Can't fit population to size, fascicle diameter is not defined."
                )

        axons_diameter, y_axons, z_axons, axons_type = remove_collision(
            axons_diameter, y_axons, z_axons, axons_type
        )
        if self.D is not None:
            axons_diameter, y_axons, z_axons, axons_type = remove_outlier_axons(
                axons_diameter, y_axons, z_axons, axons_type, self.D - delta
            )
        
        self.axons_diameter = axons_diameter.flatten()
        self.axons_type = axons_type.flatten()
        self.axons_y = y_axons.flatten()
        self.axons_z = z_axons.flatten()
        self.translate_axons(self.y_grav_center, self.z_grav_center)


    def fit_population_to_size(self, delta: float = 1):
        """
        Fit the axon positions to the size of the fascicle

        Parameters
        ----------
        delta   : float
            minimum axon to fascicle border distance, in um
        """
        self.translate_axons(-self.y_grav_center, -self.z_grav_center)
        d_pop = get_circular_contour(
            self.axons_diameter, self.axons_y, self.axons_z, delta
        )
        if (d_pop) < self.D:
            exp_factor = 0.99 * (self.D / d_pop)
            self.axons_y, self.axons_z = expand_pop(
                self.axons_y, self.axons_z, exp_factor
            )
        self.translate_axons(self.y_grav_center, self.z_grav_center)

    ## Move methods
    def translate_axons(self, y, z):
        """
        Move axons only in a fascicle by group translation

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.axons_y += y
        self.axons_z += z

    def translate_fascicle(self, y, z):
        """
        Translate a complete fascicle

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.y_grav_center += y
        self.z_grav_center += z
        self.translate_axons(y, z)
        if self.extra_stim is not None:
            self.extra_stim.translate(y=y, z=z)
        if self.recorder is not None:
            self.recorder.translate(y=y, z=z)

    def rotate_axons(self, theta, y_c=0, z_c=0):
        """
        Move axons only in a fascicle by group rotation

        Parameters
        ----------
        theta   : float
            angular value of the translation, in rad
        y_c     : float
            y axis value of the rotation center in um, by default set to 0
        z_c     : float
            z axis value for the rotation center in um, by default set to 0
        """
        self.axons_y = (
            np.cos(theta) * (self.axons_y - y_c) - np.sin(theta) * (self.axons_z - z_c)
        ) + y_c
        self.axons_z = (
            np.sin(theta) * (self.axons_y - y_c) + np.cos(theta) * (self.axons_z - z_c)
        ) + z_c

    def rotate_fascicle(self, theta, y_c=0, z_c=0):
        """
        Rotate a complete fascicle

        Parameters
        ----------
        theta   : float
            angular value of the translation, in rad
        y_c     : float
            y axis value of the rotation center in um, by default set to 0
        z_c     : float
            z axis value for the rotation center in um, by default set to 0
        """
        self.y_grav_center = (
            np.cos(theta) * (self.y_grav_center - y_c)
            - np.sin(theta) * (self.z_grav_center - z_c)
        ) + y_c
        self.z_grav_center = (
            np.sin(theta) * (self.y_grav_center - y_c)
            + np.cos(theta) * (self.z_grav_center - z_c)
        ) + z_c
        self.rotate_axons(theta, y_c=y_c, z_c=z_c)

    ## Axons related method
    def set_axons_parameters(
        self, unmyelinated_only=False, myelinated_only=False, **kwargs
    ):
        """
        set parameters of axons in the fascicle

        Parameters
        ----------
        unmyelinated_only:      bool
            if true modification only done for unmyelinated axons parameters, by default False
        myelinated_only:        bool
            if true modification only done for myelinated axons parameters, by default False
        kwargs:
            parameters to modify (see myelinated and unmyelinated)
        """
        ## Standard keys
        for key in kwargs:
            if "model" in key:
                if not myelinated_only and kwargs[key] in unmyelinated_models:
                    self.unmyelinated_param["model"] = kwargs[key]
                elif not unmyelinated_only and kwargs[key] in myelinated_models:
                    self.myelinated_param["model"] = kwargs[key]
                else:
                    rise_warning(kwargs[key], " is not an implemented axon model")
            else:
                if not myelinated_only and key in self.unmyelinated_param:
                    self.unmyelinated_param[key] = kwargs[key]
                if not unmyelinated_only and key in self.myelinated_param:
                    self.myelinated_param[key] = kwargs[key]

        ## Specific keys
        if "unmyelinated_nseg" in kwargs:
            self.unmyelinated_param["Nseg_per_sec"] = kwargs["unmyelinated_nseg"]
        if "myelinated_nseg_per_sec" in kwargs:
            self.myelinated_param["Nseg_per_sec"] = kwargs["myelinated_nseg_per_sec"]

    def get_axons_parameters(self, unmyelinated_only=False, myelinated_only=False):
        """
        get parameters of axons in the fascicle

        Parameters
        ----------
        unmyelinated_only:      bool
            modification will only
        myelinated_only:        bool
            modification will only
        """
        if unmyelinated_only:
            return self.unmyelinated_param
        if myelinated_only:
            return self.myelinated_param
        return self.unmyelinated_param, self.myelinated_param

    def __generate_axon(self,k:int)->axon:
        """
        Internal use only: generate fascicle't kth axon

        Parameters
        ----------
        k : int
            _description_
        """
        if self.axons_type[k] == 0:
            axon = unmyelinated(
                self.axons_y[k],
                self.axons_z[k],
                self.axons_diameter[k],
                self.L,
                ID=k,
                **self.unmyelinated_param,
            )
        else:
            self.myelinated_param["node_shift"] = self.NoR_relative_position[k]
            axon = myelinated(
                self.axons_y[k],
                self.axons_z[k],
                self.axons_diameter[k],
                self.L,
                ID=k,
                **self.myelinated_param,
            )
            self.myelinated_param.pop("node_shift")
        return axon

    def remove_unmyelinated_axons(self):
        """
        Remove all unmyelinated fibers from the fascicle
        """
        mask = self.axons_type.astype(bool)
        self.axons_diameter = self.axons_diameter[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]
        self.axons_type = self.axons_type[mask]
        if len(self.NoR_relative_position) != 0:
            self.NoR_relative_position = self.NoR_relative_position[mask]

    def remove_myelinated_axons(self):
        """
        Remove all myelinated fibers from the
        """
        mask = np.invert(self.axons_type.astype(bool))
        self.axons_diameter = self.axons_diameter[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]
        self.axons_type = self.axons_type[mask]
        if len(self.NoR_relative_position) != 0:
            # almost useless but here for coherence
            self.NoR_relative_position = self.NoR_relative_position[mask]

    def remove_axons_size_threshold(self, d, min=True):
        """
        Remove fibers with diameters below/above a threshold
        """
        if min:
            mask = self.axons_diameter >= d
        else:
            mask = self.axons_diameter <= d

        self.axons_diameter = self.axons_diameter[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]
        self.axons_type = self.axons_type[mask]
        if len(self.NoR_relative_position) != 0:
            # almost useless but here for coherence
            self.NoR_relative_position = self.NoR_relative_position[mask]

    ## Representation methods
    def plot(
        self,
        axes,
        contour_color="k",
        myel_color="b",
        unmyel_color="r",
        elec_color="gold",
        num=False,
    ):
        """
        plot the fascicle in the Y-Z plane (transverse section)

        Parameters
        ----------
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        contour_color   : str
            matplotlib color string applied to the contour. Black by default
        myel_color      : str
            matplotlib color string applied to the myelinated axons. Red by default
        unmyel_color    : str
            matplotlib color string applied to the myelinated axons. Blue by default
        num             : bool
            if True, the index of each axon is displayed on top of the circle
        """
        ## plot contour
        axes.add_patch(
            plt.Circle(
                (self.y_grav_center, self.z_grav_center),
                self.D / 2,
                color=contour_color,
                fill=False,
                linewidth=2,
            )
        )
        ## plot axons
        circles = []
        for k in range(self.n_ax):
            if self.axons_type[k] == 1:  # myelinated
                circles.append(
                    plt.Circle(
                        (self.axons_y[k], self.axons_z[k]),
                        self.axons_diameter[k] / 2,
                        color=myel_color,
                        fill=True,
                    )
                )
            else:
                circles.append(
                    plt.Circle(
                        (self.axons_y[k], self.axons_z[k]),
                        self.axons_diameter[k] / 2,
                        color=unmyel_color,
                        fill=True,
                    )
                )
        for circle in circles:
            axes.add_patch(circle)
        if self.extra_stim is not None:
            self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.D)
        if num:
            for k in range(self.n_ax):
                axes.text(self.axons_y[k], self.axons_z[k], str(k))
        axes.set_xlim((-1.1 * self.D / 2, 1.1 * self.D / 2))
        axes.set_ylim((-1.1 * self.D / 2, 1.1 * self.D / 2))

    def plot_x(self, axes, myel_color="b", unmyel_color="r", Myelinated_model="MRG"):
        """
        plot the fascicle's axons along Xline (longitudinal)

        Parameters
        ----------
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        myel_color      : str
            matplotlib color string applied to the myelinated axons. Red by default
        unmyel_color    : str
            matplotlib color string applied to the myelinated axons. Blue by default
        Myelinated_model : str
            model use for myelinated axon (use to calulated node position)
        """
        if self.L is None or len(self.NoR_relative_position)>0:
            drange = [
                min(self.axons_diameter.flatten()),
                max(self.axons_diameter.flatten()),
            ]
            polysize = np.poly1d(np.polyfit(drange, [0.5, 5], 1))
            for k in range(self.n_ax):
                relative_pos = self.NoR_relative_position[k]
                d = self.axons_diameter[k]
                if self.axons_type.flatten()[k] == 0.0:
                    color = unmyel_color
                    size = polysize(d)
                    axes.plot([0, self.L], np.ones(2) + k - 1, color=color, lw=size)
                else:
                    color = myel_color
                    size = polysize(d)
                    axon = self.__generate_axon(k)
                    x_nodes = axon.x_nodes
                    node_number = len(x_nodes)
                    del axon
                    axes.plot([0, self.L], np.ones(2) + k - 1, color=color, lw=size)
                    axes.scatter(
                        x_nodes,
                        np.ones(node_number) + k - 1,
                        marker="x",
                        color=color,
                    )
            ## plot electrode(s) if existings
            if self.extra_stim is not None:
                for electrode in self.extra_stim.electrodes:
                    if not is_FEM_electrode(electrode):
                        axes.plot(
                            electrode.x * np.ones(2),
                            [0, self.n_ax - 1],
                            color="gold",
                        )
            axes.set_xlabel("x (um)")
            axes.set_ylabel("axon ID")
            axes.set_yticks(np.arange(self.n_ax))
            axes.set_xlim(0, self.L)
            plt.tight_layout()

    ## Context handling methods
    def clear_context(
        self, extracel_context=True, intracel_context=True, rec_context=True
    ):
        """
        Clear all stimulation and recording mecanism
        """
        if extracel_context:
            self.L = None
            # extra-cellular stimulation
            self.extra_stim = None
            self.footprints = {}
            self.is_footprinted = False
        if intracel_context:
            # intra-cellular stimulation
            self.N_intra = 0
            self.intra_stim_position = []
            self.intra_stim_t_start = []
            self.intra_stim_duration = []
            self.intra_stim_amplitude = []
            self.intra_stim_ON = []
        if rec_context:
            ## recording mechanism
            self.record = False
            self.recorder = None
        self.is_simulated = False

    def attach_extracellular_stimulation(self, stimulation):
        """
        attach a extracellular context of simulation for an axon.

        Parameters
        ----------
            stimulation  : stimulation object, see Extracellular.stimulation help for more details
        """
        if is_extra_stim(stimulation):
            self.extra_stim = stimulation
        # remove overlaping axons
        for electrode in stimulation.electrodes:
            self.remove_axons_electrode_overlap(electrode)

    def remove_axons_electrode_overlap(self, electrode):
        """
        Remove the axons that could overlap an electrode

        Parameters
        ----------
        electrode : object
            electrode instance, see electrodes for more details
        """
        y, z, D = 0, 0, 0
        # CUFF electrodes do not affect intrafascicular state
        if not is_CUFF_electrode(electrode):
            y = electrode.y
            z = electrode.z
            if is_LIFE_electrode(electrode):
                D = electrode.D
            # compute the distance of all axons to electrode
            D_vectors = np.sqrt((self.axons_y - y) ** 2 + (self.axons_z - z) ** 2) - (
                self.axons_diameter / 2 + D / 2
            )
            colapse = np.argwhere(D_vectors < 0)
            mask = np.ones(len(self.axons_diameter), dtype=bool)
            mask[colapse] = False
            # remove axons colliding the electrode
            if len(colapse) > 0:
                pass_info(
                    f"From Fascicle {self.ID}: Electrode/Axons overlap, {len(colapse)} axons will be removed from the fascicle"
                )
                pass_info(self.n_ax, " axons remaining")
            self.axons_diameter = self.axons_diameter[mask]
            self.axons_type = self.axons_type[mask]
            self.axons_y = self.axons_y[mask]
            self.axons_z = self.axons_z[mask]

    def change_stimulus_from_electrode(self, ID_elec, stimulus):
        """
        Change the stimulus of the ID_elec electrods

        Parameters
        ----------
            ID_elec  : int
                ID of the electrode which should be changed
            stimulus  : stimulus
                new stimulus to set
        """
        if self.extra_stim is not None:
            self.extra_stim.change_stimulus_from_electrode(ID_elec, stimulus)
        else:
            rise_warning("Cannot be changed: no extrastim in the fascicle")

    def insert_I_Clamp(self, position, t_start, duration, amplitude, ax_list=None):
        """
        Insert a IC clamp stimulation

        Parameters
        ----------
        position    : float
            relative position over the fascicle. Note that all thin myelinated and myelinated
            will be stimulated in the nearest node of Ranvier around the clamp specified position
        t_start     : float
            starting time, in ms
        duration    : float
            duration of the pulse, in ms
        amplitude   : float
            amplitude of the pulse (nA)
        ax_list     : list, array, np.array
            list of axons to insert the clamp on, if None, all axons are stimulated
        """
        self.intra_stim_position.append(position)
        self.intra_stim_t_start.append(t_start)
        self.intra_stim_duration.append(duration)
        self.intra_stim_amplitude.append(amplitude)
        self.intra_stim_ON.append(ax_list)
        self.N_intra += 1

    def clear_I_clamp(self):
        """
        Clear any I-clamp attached to the fascicle
        """
        self.N_intra = 0
        self.intra_stim_position = []
        self.intra_stim_t_start = []
        self.intra_stim_duration = []
        self.intra_stim_amplitude = []
        self.intra_stim_ON = []

    ## RECORDING MECHANIMS
    def attach_extracellular_recorder(self, rec: recorder):
        """
        attach an extracellular recorder to the axon

        Parameters
        ----------
        rec     : recorder object
            see Recording.recorder help for more details
        """
        if is_recorder(rec):
            self.record = True
            self.recorder = rec

    def shut_recorder_down(self):
        """
        Shuts down the recorder locally
        """
        self.record = False

    ## SIMULATION HANDLING
    def generate_random_NoR_position(self):
        """
        Generates radom Node of Ranvier shifts to prevent from axons with the same diamters to be aligned.
        """
        # also generated for unmyelinated but the meaningless value won't be used
        self.NoR_relative_position = np.random.uniform(
            low=0.0, high=1.0, size=len(self.axons_diameter)
        )

    def generate_ligned_NoR_position(self, x=0):
        """
        Generates Node of Ranvier shifts to aligned a node of each axon to x postition.

        Parameters
        ----------
        x    : float
            x axsis value (um) on which node are lined, by default 0
        """
        # also generated for unmyelinated but the meaningless value won't be used
        self.NoR_relative_position = []

        for i in range(self.n_ax):
            if self.axons_type.flatten()[i] == 0.0:
                self.NoR_relative_position += [0.0]
            else:
                d = self.axons_diameter[i]
                node_length = get_MRG_parameters(d)[5]
                self.NoR_relative_position += [(x - 0.5) % node_length / node_length]
                # -0.5 to be at the node of Ranvier center as a node is 1um long

    @property
    def __footprint_to_compute(self):
        """
        returns True only if loaded footprint are selected AND footprint exist
        """
        return not (self.is_footprinted and self.loaded_footprints)

    def compute_electrodes_footprints(
        self, save_ftp_only=False, filename="electrodes_footprint.ftpt", **kwargs
    ):
        """
        get electrodes footprints on each segment of each axon

        Parameters
        ----------
        save_ftp_only        :bool
            if true save result in a .ftpt file
        filename    :str
            saving file name and path
        Unmyelinated_model  : str
            model for unmyelinated fibers, by default 'Rattay_Aberham'
        Adelta_model        : str
            model for A-delta thin myelinated fibers, by default'extended_Gaines'
        Myelinated_model    : str
            model for myelinated fibers, by default 'MRG'
        myelinated_nseg_per_sec        : int
            number of segment per section for myelinated axons
        Returns
        -------
        footprints   : dict
            Dictionnary composed of axon footprint dictionary, the keys are int value
            of the corresponding axon ID
        """
        footprints = {}
        if is_FEM_extra_stim(self.extra_stim):
            self.extra_stim.run_model()
        self.set_axons_parameters(**kwargs)
        if len(self.NoR_relative_position) == 0:
            self.generate_random_NoR_position()
        for k in range(len(self.axons_diameter)):
            axon = self.__generate_axon(k)
            axon.attach_extracellular_stimulation(self.extra_stim)
            footprints[k] = axon.get_electrodes_footprints_on_axon(
                save_ftp_only=save_ftp_only, filename=filename
            )
            del axon
        if save_ftp_only:
            json_dump(footprints, filename)
        else:
            self.footprints = footprints
        self.is_footprinted = True
        return footprints

    def get_electrodes_footprints_on_axons(
        self, save_ftp_only=False, filename="electrodes_footprint.ftpt", **kwargs
    ):
        """
        :meta private:
        """
        rise_warning(
            DeprecationWarning,
            "Deprecation method get_electrodes_footprints_on_axons",
            "\nuse compute_electrodes_footprints instead",
        )
        self.compute_electrodes_footprints(
            save_ftp_only=save_ftp_only, filename=filename, **kwargs
        )

    def __init_axon_postprocessing(self):
        """
        Internal use only: initialize the axon on-the-fly postprocessing.
        """
        # Set the axon postprocessing label and function
        # self.postproc_script, self.postproc_function or self.postproc_label should have been set by self.set_parameters
        if callable(self.postproc_script):
            self.postproc_function = self.postproc_script
        elif isinstance(self.postproc_script, str):
            self.postproc_label = self.postproc_script
        self.postproc_script = None

        if callable(self.postproc_function):
            self.postproc_label = self.postproc_function.__name__
        else:
            # Custom postproc is ca
            if self.postproc_label in globals():
                self.postproc_function = globals()[self.postproc_label]
            else:
                if isinstance(self.postproc_label, str):
                    self.postproc_label = self.postproc_label.lower()
                if self.postproc_label in deprecated_builtin_postproc_functions:
                    rise_warning(
                        DeprecationWarning,
                        self.postproc_label,
                        " is a deprecated, use",
                        deprecated_builtin_postproc_functions[self.postproc_label],
                        "instead",
                    )
                    self.postproc_label = deprecated_builtin_postproc_functions[
                        self.postproc_label
                    ]
                elif self.postproc_label not in builtin_postproc_functions:
                    rise_warning(
                        self.postproc_label,
                        " isn't a buitin function, default post processing will be used instead",
                    )
                    self.postproc_label = "default"
                self.postproc_function = builtin_postproc_functions[self.postproc_label]

        # update and check function_kwargs
        ## !!See if this part should be kept ##
        if "save" not in self.postproc_kwargs.keys():
            self.postproc_kwargs["save"] = len(self.save_path) > 0
        if "fdir" not in self.postproc_kwargs.keys():
            self.postproc_kwargs["fdir"] = self.save_path + "Fascicle_" + str(self.ID)
        ##  ##
        self.postproc_kwargs = check_function_kwargs(
            self.postproc_function, self.postproc_kwargs
        )
        
    def __set_pbar_label(self, **kwargs):
        if "pbar_label" in kwargs:
            __label = kwargs["pbar_label"]
        else:
            __label = f"Fascicle {self.ID}" 
        __label += f" -- {parameters.get_nmod_ncore()} CPU"
        if parameters.get_nmod_ncore() > 1:
            __label += "s"
        return __label

    def sim_axon(
        self,
        k,
    ) -> axon_results:
        """
        Internal use only simumlated one axon of the fascicle

        Parameters
        ----------
        k       : int
            ID of the axon to simulate
        """
        ## test axon axons_type[k]
        assert self.axons_type[k] in [0, 1]
        axon = self.__generate_axon(k)
        ## add extracellular stimulation
        axon.attach_extracellular_stimulation(self.extra_stim)
        ## add recording mechanism
        if self.record:
            axon.attach_extracellular_recorder(self.recorder)
        # add intracellular stim
        if self.N_intra > 0:
            for j in range(self.N_intra):
                if is_iterable(self.intra_stim_ON[j]):
                    # in this case, the stimulation is possibly not for all axons
                    if self.intra_stim_ON[j][k]:
                        # then stimulation should apply, look for the parameters
                        # get position
                        if is_iterable(self.intra_stim_position[j]):
                            position = self.intra_stim_position[j][k]
                        else:
                            position = self.intra_stim_position[j]
                        # get t_start
                        if is_iterable(self.intra_stim_t_start[j]):
                            t_start = self.intra_stim_t_start[j][k]
                        else:
                            t_start = self.intra_stim_t_start[j]
                        # get duration
                        if is_iterable(self.intra_stim_duration[j]):
                            duration = self.intra_stim_duration[j][k]
                        else:
                            duration = self.intra_stim_duration[j]
                        # get amplitude
                        if is_iterable(self.intra_stim_amplitude[j]):
                            amplitude = self.intra_stim_amplitude[j][k]
                        else:
                            amplitude = self.intra_stim_amplitude[j]
                        # APPLY INTRA CELLULAR STIMULATION
                        axon.insert_I_Clamp(position, t_start, duration, amplitude)
                else:
                    # in this case , stimulate all axons
                    if is_iterable(self.intra_stim_position[j]):
                        position = self.intra_stim_position[j][k]
                    else:
                        position = self.intra_stim_position[j]
                    # get t_start
                    if is_iterable(self.intra_stim_t_start[j]):
                        t_start = self.intra_stim_t_start[j][k]
                    else:
                        t_start = self.intra_stim_t_start[j]
                    # get duration
                    if is_iterable(self.intra_stim_duration[j]):
                        duration = self.intra_stim_duration[j][k]
                    else:
                        duration = self.intra_stim_duration[j]
                    # get amplitude
                    if is_iterable(self.intra_stim_amplitude[j]):
                        amplitude = self.intra_stim_amplitude[j][k]
                    else:
                        amplitude = self.intra_stim_amplitude[j]
                    # APPLY INTRA CELLULAR STIMULATION
                    axon.insert_I_Clamp(position, t_start, duration, amplitude)
        if not self.__footprint_to_compute:
            axon_ftpt = True
            if k in self.footprints:
                axon.footprints = self.footprints[k]
            elif str(k) in self.footprints:
                axon.footprints = self.footprints[str(k)]
            else:
                rise_warning("footprints not computed for axon " + str(k))
                axon_ftpt = False
        else:
            axon_ftpt = False
        axon_sim = axon.simulate(
            t_sim=self.t_sim,
            record_V_mem=self.record_V_mem,
            record_I_mem=self.record_I_mem,
            record_I_ions=self.record_I_ions,
            record_g_mem=self.record_g_mem,
            record_g_ions=self.record_g_ions,
            record_particles=self.record_particles,
            loaded_footprints=axon_ftpt,
        )
        #print(axon.recorder.save())
        del axon

        axon_sim = self.postproc_function(axon_sim, **self.postproc_kwargs)
        if self.save_results:
            ax_fname = "sim_axon_" + str(k) + ".json"
            axon_sim.save(save=True, fname=self.result_folder_name + "/" + ax_fname)
        return axon_sim

    def simulate(
        self,
        **kwargs,
    ) -> fascicle_results:
        """
        Simulates the fascicle using neuron framework. Parallel computing friendly. Does not return
        results (possibly too large in memory and complex with parallel computing), but instead
        creates a folder and store fascicle configuration and all axons results.
        On the fly post processing is possible by specifying an additional script.

        Parameters
        ----------
        t_sim               : float
            total simulation time (ms), by default 20 ms
        record_V_mem        : bool
            if true, the membrane voltage is recorded, set to True by default
        record_I_mem        : bool
            if true, the membrane current is recorded, set to False by default
        record_I_ions       : bool
            if true, the ionic currents are recorded, set to False by default
        record_particules   : bool
            if true, the marticule states are recorded, set to False by default
        loaded_footprints          : dict or bool
            Dictionnary composed of axon footprint dictionary, the keys are int value
            of the corresponding axon ID. if type is bool, fascicle footprints attribute is used
            if None, footprins calculated during the simulation, by default None
        save_V_mem          : bool
            if true, all membrane voltages values are stored in results whe basic postprocessing is
            applied. Can be heavy ! False by default
        save_path           : str
            name of the folder to store results of the fascicle simulation.
        Unmyelinated_model  : str
            model for unmyelinated fibers, by default 'Rattay_Aberham'
        Myelinated_model    : str
            model for myelinated fibers, by default 'MRG'
        myelinated_seg_per_sec        : int
            number of segment per section for myelinated axons
        PostProc_Filtering  : float, list, array, np.array
            value or iterable values for basic post proc filtering. If None specified, no filtering
            is performed
        postproc_script     : str
            path to a postprocessing file. If specified, the basic post processing is not
            performed, and all postprocessing have to be handled by user. The specified script
            can access global and local variables. Can also be key word ('Vmem_plot' or 'scarter')
            to use script saved in OTF_PP folder, use with caution
        return_parameters_only        : bool
            if True the results of axon simulations are integrated into fasc_sim return after simulation
            use with caution: can increase a lot computational memory
        save_results                  : bool
            if False disable the result storage
            can only be False if return_parameters_only is False

        Return
        ------
            fasc_sim    : sim_results
                results of the simulation
        """
        fasc_sim = super().simulate(**kwargs)
        if not self.save_results:
            if self.return_parameters_only:
                rise_warning(
                    "Fascicle's simulation parameters are misused",
                    "results are neither saved or return",
                    "save anyway",
                )
                self.save_results = True
        self.__init_axon_postprocessing()
        if len(self.NoR_relative_position) == 0:
            self.generate_random_NoR_position()
        # create folder and save fascicle config
        self.result_folder_name = self.save_path + "Fascicle_" + str(self.ID)
        if len(self.save_path):  # LR: Force folder creation if any save_path is specified --> usefull for some PP functions (ex: scatter_plot)
            create_folder(self.result_folder_name)

        if self.save_results:
            # create_folder(folder_name)
            self.config_filename = self.result_folder_name + "/00_Fascicle_config.json"
            fasc_sim.save(save=True, fname=self.config_filename)
        else:
            pass

        # impose myelinated_nseg_per_sec if footprint are loaded
        if self.loaded_footprints:
            kwargs["myelinated_nseg_per_sec"] = self.myelinated_param["Nseg_per_sec"]
            kwargs["unmyelinated_nseg"] = self.unmyelinated_param["Nseg_per_sec"]
        self.set_axons_parameters(**kwargs)

        bckup = None
        if self.__footprint_to_compute and self.has_FEM_extracel:
            self.compute_electrodes_footprints()

        if self.has_FEM_extracel:
            self.loaded_footprints = True   # To set __footprint_to_compute to false
            if "model" in self.extra_stim.__dict__: #!! for nerve no model to investigate
                bckup = self.extra_stim.model   # Can't be passed to mp pool :'(
                del self.extra_stim.model

        # create ID for all axons
        axons_ID = np.arange(len(self.axons_diameter), )

        ## perform simulations in //
        results = []
        # Todo add upperlevel progress handler in nerve.simulate()
        with progress.Progress(
            "[progress.description]{task.description}",
            "{task.completed} / {task.total}",
            progress.BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
        ) as pg:
            __label = self.__set_pbar_label(**kwargs)
            task_id = pg.add_task(f"[cyan]{__label}:", total=self.n_ax)
            #with mp.get_context('spawn').Pool(parameters.get_nmod_ncore()) as pool:  #forces spawn mode
            with get_pool(parameters.get_nmod_ncore(),backend="spawn") as pool: 
                for result in pool.imap(self.sim_axon, axons_ID):
                    results.append(result)
                    pg.advance(task_id)
                    pg.refresh()
                pool.close() #LR: Apparently this avoid PETSC Terminate ERROR
                pool.join()  #LR: but this shouldn't be needed as we are in "with"...

        #results = list(pool_results)

        if bckup is not None:
            self.extra_stim.model = bckup
        # Todo see if it can be added to // for loop
        if self.record:
            self.recorder.gather_all_recordings(results)
            for i in range(self.n_ax):
                results[i].pop("recorder")
        # Todo see if it can be added to // for loop
        if not self.return_parameters_only:
            for k in axons_ID:
                fasc_sim.update({"axon" + str(k): results[k]})
        if not self.return_parameters_only:
            if "extra_stim" in fasc_sim:
                fasc_sim["extra_stim"] = load_any(
                    fasc_sim["extra_stim"]
                )  # dirty hack to force NRV_class instead of dict
            if self.record:
                fasc_sim["recorder"] = load_any(fasc_sim["recorder"])

        if self.verbose:
            pass_info("... Simulation done")
            fasc_sim["is_simulated"] = True
        self.is_simulated = True
        return fasc_sim
