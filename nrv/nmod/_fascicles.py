"""
NRV-:class:`.fascicle` handling.
"""

import faulthandler
import os

from copy import deepcopy
import matplotlib.pyplot as plt
from typing import Literal, Callable
import numpy as np

# import multiprocessing as mp
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
from ..utils.geom import create_cshape, circle_overlap_checker
from ._axon_population import axon_population
from ..backend._inouts import check_function_kwargs
from ._axons import *
from .utils._axon_pop_generator import *
from ._myelinated import myelinated
from ._unmyelinated import unmyelinated
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

    def __init__(self, diameter=50, ID=0, **kwargs):
        """
        Instantation of a Fascicle
        """
        super().__init__(**kwargs)

        # to add to a fascicle/nerve common mother class

        #:str: path where the simulation results should be saved
        self.save_path: str = ""
        #:str: value: False: verbosity mainly for pbars. Tests more comment
        self.verbose: bool = False
        self.return_parameters_only: bool = False
        self.loaded_footprints: bool = False
        self.save_results: bool = False
        self.result_folder_name: str = ""

        self.postproc_label: str = "default"
        self.postproc_function: Callable = None
        self.postproc_script: Callable | str = None
        self.postproc_kwargs: dict = {}

        self.config_filename: str = ""
        self.ID: int = ID
        self.n_proc: None | int = None

        self.L: float | None = None
        # add an empty axon population
        self.axons: axon_population = axon_population(
            geometry=create_cshape(diameter=diameter)
        )

        # self.D = diameter
        # # geometric properties
        # self.y_grav_center = 0
        # self.z_grav_center = 0

        # Update parameters with kwargs
        self.set_parameters(**kwargs)

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

        self.sim_list: list[int] = []
        self.sim_mask = []

        # extra-cellular stimulation
        self.extra_stim: extracellular_context = None
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
        self.recorder: None | recorder = None
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
        to_save = save and _fasc_save

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
        extracel_context: bool = False,
        intracel_context: bool = False,
        rec_context: bool = False,
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
        self.__check_deprecation(key_dic=key_dic)

    def __check_deprecation(self, key_dic: dict):
        d_status = False
        if "unmyelinated_param" not in key_dic:
            rise_warning(
                "Deprecated fascicle file, does not contains unmyelinated_param requiered since v0.8.0"
            )
            self.set_axons_parameters(key_dic)
            d_status = True

        if "axons" not in key_dic:
            rise_warning(
                "Deprecated fascicle file, does not contains axon_populaiton requiered since v1.2.2"
            )
            self.axons.generate_from_deprected_fascicle(key_dic)
            d_status = True

        if d_status:
            rise_warning(
                "Deprecated fascicle file: consider updating using nrv.ui.update_fascicle_file"
            )

    ## Fascicle property method
    @property
    def n_ax(self) -> int:
        """
        Number of axons in the fascicle
        """
        return len(self.axons.get_sub_population(mask_labels=self.sim_mask))

    @property
    def geom(self) -> CShape:
        """
        Fascicle geometry
        """
        return self.axons.geom

    @property
    def center(self) -> tuple[float, float]:
        """
        (y,z) position of the fascicle center

        Returns
        -------
        tuple[float,float]
        """
        return self.geom.center

    @property
    def radius(self) -> float | tuple[float, float]:
        """
        radius of the fascicle

        Returns
        -------
        float | tuple[float,float]
            `float` for circular fascicles
            `tuple[float,float]` for elliptic fascicles
        """
        return self.geom.radius

    @property
    def d(self) -> float:
        """
        diameter of the fascicle

        Returns
        -------
        float | tuple[float,float]
            `float` for circular fascicles
            `tuple[float,float]` for elliptic fascicles
        """
        if isinstance(self.radius, tuple):
            return tuple([2 * r for r in self.radius])
        return 2 * self.radius

    @property
    def y(self) -> float:
        """
        y position of the center of the fascicle

        Returns
        -------
        float
        """
        return self.center[0]

    @property
    def z(self) -> float:
        """
        z position of the center of the fascicle

        Returns
        -------
        float
        """
        return self.center[1]

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
            if self.loaded_footprints:
                rise_warning("Modifying length of a fascicle delete the su")
                self.loaded_footprints = False
                self.footprints = {}
                self.is_footprinted = False
        self.L = L
        self.unmyelinated_param["Nseg_per_sec"] == self.L // 25

    ## generate stereotypic Fascicle
    def set_geometry(self, **kwgs):
        """
        Set the fascicle geometry

        Note
        ----
        alias for :meth:`self.axons.set_geometry<axon_population.set_geometry>`

        """
        self.axons.set_geometry(**kwgs)

    ## generate Fascicle from histology
    def import_contour(self, smthing_else):
        """
        Define contour from a file
        """
        rise_error(NotImplementedError)

    ## fill fascicle methods
    def fill(
        self,
        data: tuple[np.ndarray] | np.ndarray | str = None,
        n_ax: int = 100,
        FVF: None | float = None,
        percent_unmyel: float = 0.7,
        M_stat: str = "Schellens_1",
        U_stat: str = "Ochoa_U",
        pos: None | tuple[np.ndarray] | np.ndarray | str = None,
        method: Literal["default", "packing"] = "default",
        delta: float = 0.01,
        delta_trace: float | None = None,
        delta_in: float | None = None,
        n_iter: int = None,
        fit_to_size: bool = False,
        with_node_shift: bool = True,
        overwrite: bool = False,
        fname: str = None,
    ):
        """
        Fill a geometricaly defined contour with axons.

        Note
        ----
        alias for :meth:`self.axons.fill_geometry<axon_population.fill_geometry>`

        Parameters
        ----------
        data : tuple[np.ndarray] | np.ndarray | str
            data to used to create the population. Supported data:

                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax) or (4, n_ax).
        n_ax               : int, optional
            Number of axon to generate for the population (Unmyelinated and myelinated), default 100
        FVF             : float
            Fiber Volume Fraction estimated for the area. If None, the value n_ax is used. By default set to None
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition
        method : Literal[&quot;default&quot;, &quot;packing&quot;], optional
            method to use for the , by default "default"
        overwrite : bool, optional
            If True placement is skipped if the population is already paced, by default False
        delta               : float
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        with_node_shift            : bool
            if True also compute the Node of Ranviers shifts
        fname      : str
            optional, if specified, name file to store the population generated

        Note
        ----
        When `FVF` is set, an approximated value of `n_ax` is calculated from:

        .. math::

            FVF = \\frac{n_{axons}*E_{d}}{A_{tot}}

        where $E_{d}$ is the espected diameters from the myelinated and unmyelinated fibers stats and $A_{tot}$ is geometry total area.

        Tip
        ---
        It goes for the previous definition that `FVF` will only be accurate for large axon population. This might be improved in future version but for now it is adviced to define small population using `n_ax` instead of `FVF`
        """
        self.axons.fill_geometry(
            data=data,
            n_ax=n_ax,
            FVF=FVF,
            percent_unmyel=percent_unmyel,
            M_stat=M_stat,
            U_stat=U_stat,
            pos=pos,
            method=method,
            delta=delta,
            delta_trace=delta_trace,
            delta_in=delta_in,
            n_iter=n_iter,
            fit_to_size=fit_to_size,
            with_node_shift=with_node_shift,
            overwrite=overwrite,
            fname=fname,
        )

    ## Move methods
    def translate(
        self,
        y=0,
        z=0,
        with_geom: bool = True,
        with_pop: bool = True,
        with_context: bool = True,
    ):
        """
        Translate the population and/or its geometry and/or stim and rec context.

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        with_geom : bool, optional
            if True rotate the geometry, by default True
        with_pop : bool, optional
            if True rotate the population, by default True
        with_context : bool, optional
            if True stimulation and recording contexts attach to the fascicle , by default True
        """
        self.axons.translate(y=y, z=z, with_geom=with_geom, with_pop=with_pop)
        if with_context:
            if self.extra_stim is not None:
                self.extra_stim.translate(y=y, z=z)
            if self.recorder is not None:
                self.recorder.translate(y=y, z=z)

    def rotate(
        self,
        angle: float,
        with_geom: bool = True,
        with_pop: bool = True,
        with_context: bool = True,
        degree: bool = False,
    ):
        """
        Rotate the population and/or its geometry and/or stim and rec context.

        Parameters
        ----------
        angle : float
            Angle of the rotation
        with_geom : bool, optional
            if True rotate the geometry, by default True
        with_pop : bool, optional
            if True rotate the population, by default True
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        self.axons.rotate(angle, with_geom=with_geom, with_pop=with_pop, degree=degree)
        if with_context:
            if self.extra_stim is not None:
                self.extra_stim.rotate(angle, self.center)
            if self.recorder is not None:
                self.recorder.rotate(angle, self.center)

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

    def __generate_axon(self, k: int) -> axon:
        """
        Internal use only: generate fascicle't kth axon

        Parameters
        ----------
        k : int
            _description_
        """
        if self.axons["types"][k] == 0:
            axon = unmyelinated(
                self.axons["y"][k],
                self.axons["z"][k],
                self.axons["diameters"][k],
                self.L,
                ID=k,
                **self.unmyelinated_param,
            )
        else:
            self.myelinated_param["node_shift"] = self.axons["node_shift"][k]
            axon = myelinated(
                self.axons["y"][k],
                self.axons["z"][k],
                self.axons["diameters"][k],
                self.L,
                ID=k,
                **self.myelinated_param,
            )
            self.myelinated_param.pop("node_shift")
        return axon

    def add_sim_mask(
        self, data: np.ndarray | str, label: None | str = None, overwrite: bool = True
    ):
        """
        Add a mask on the axon population

        Parameters
        ----------
        data : np.ndarray | str
            Data to use for the mask, can be either:
             - str: compatible to :meth:`DataFrame.eval` from wich the mask will be generated.
             - 1D array-like: Mask that will be converted to booleen and added.
        label : None | str, optional
            Mask label, if None the label is set to `"mask_n"` where n in the smaller leading to an unused label, by default None.
        overwrite : bool, optional
            if True and `label` exists the method will do nothing, by default True
        """
        _lab, mask = self.axons.add_mask(data=data, label=label, overwrite=overwrite)
        self.sim_mask.append(_lab)

    def remove_sim_masks(
        self,
        mask_labels: None | Iterable[str] | str = None,
        remove_from_pop: bool = True,
        keep_elec: bool = True,
    ):
        if mask_labels is None:
            mask_labels = self.sim_mask  # to keep is_placed
        elif isinstance(mask_labels, str):
            mask_labels = [mask_labels]
        _rmved = []
        for _lab in mask_labels:
            if _lab in self.sim_mask and (not "_elec" in _lab or not keep_elec):
                _rmved.append(self.sim_mask.pop(self.sim_mask.index(_lab)))
        if remove_from_pop:
            self.axons.clear_masks(mask_labels=_rmved)
        else:
            pass_info(f"The following masks were removed from fascicle: {_rmved}")

    def __set_elec_mask(self):
        """
        Set the mask corresponding to
        """
        mask_to_keep = []
        if self.extra_stim is not None:
            for elec in self.extra_stim.electrodes:
                mask_to_keep += [f"_elec{elec.ID}"]
        mask_to_rmv = [
            ml for ml in self.sim_mask if ml not in mask_to_keep and "_elec" in ml
        ]
        if len(mask_to_rmv):
            self.remove_sim_masks(
                remove_from_pop=False,
                mask_labels=mask_to_rmv,
                keep_elec=False,
            )

    def remove_unmyelinated_axons(self):
        """
        Remove all unmyelinated fibers from the fascicle
        """
        _mask = self.axons["types"] == 1
        _lab = "mye_only"
        self.axons.add_mask(mask=_mask, label=_lab)
        self.sim_mask.append(_lab)

    def remove_myelinated_axons(self):
        """
        Remove all myelinated fibers from the
        """
        _mask = self.axons["types"] == 0
        _lab = "unm_only"
        self.axons.add_mask(mask=_mask, label=_lab)
        self.sim_mask.append(_lab)

    def remove_axons_size_threshold(self, d, min=True):
        """
        Remove fibers with diameters below/above a threshold
        """
        if min:
            mask = self.axons["diameters"] >= d
            _lab = f"d_over_{d}"

        else:
            mask = self.axons["diameters"] <= d
            _lab = f"d_under_{d}"
        self.axons.add_mask(mask=mask, label=_lab)
        self.sim_mask.append(_lab)

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
        self.axons.plot(
            axes,
            mask_labels=self.sim_mask,
            contour_color=contour_color,
            myel_color=myel_color,
            unmyel_color=unmyel_color,
            num=num,
        )
        if self.extra_stim is not None:
            self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.radius)

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
        if self.L is not None:
            if self.axons.has_node_shift:
                self.__update_sim_list()
                drange = [
                    self.axons["diameters"].min(),
                    self.axons["diameters"].max(),
                ]
                polysize = np.poly1d(np.polyfit(drange, [0.5, 5], 1))
                for s_k in range(self.n_ax):
                    k = self.sim_list[s_k]
                    d = self.axons["diameters"][k]
                    if self.axons["types"][k] == 0.0:
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
                axes.set_xlabel("x (um)")
                axes.set_ylabel("axon ID")
                axes.set_yticks(np.arange(self.n_ax))
                axes.set_xlim(0, self.L)
            ## plot electrode(s) if existings
            if self.extra_stim is not None:
                for electrode in self.extra_stim.electrodes:
                    if not is_FEM_electrode(electrode):
                        axes.plot(
                            electrode.x * np.ones(2),
                            [0, self.n_ax - 1],
                            color="gold",
                        )

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

    def attach_extracellular_stimulation(self, stimulation: extracellular_context):
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

    def remove_axons_electrode_overlap(self, electrode: electrode):
        """
        Remove the axons that could overlap an electrode

        Parameters
        ----------
        electrode : object
            electrode instance, see electrodes for more details
        """
        _y_z_r_elec = np.zeros(3)
        # CUFF electrodes do not affect intrafascicular state
        if not is_CUFF_electrode(electrode):
            _y_z_r_elec[0] = electrode.y
            _y_z_r_elec[1] = electrode.z
            if is_LIFE_electrode(electrode):
                _y_z_r_elec[2] = electrode.D / 2
            e_mask = ~circle_overlap_checker(
                c=_y_z_r_elec[:2],
                r=_y_z_r_elec[2],
                c_comp=self.axons[["y", "z"]].to_numpy(),
                r_comp=self.axons["diameters"].to_numpy() / 2,
            )
            e_mlabel = f"_elec{electrode.ID}"
            self.add_sim_mask(e_mask, label=e_mlabel)

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

    def insert_I_Clamp(
        self,
        position: float,
        t_start: float,
        duration: float,
        amplitude: float,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        ax_list=None,
    ):
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
        expr : str | None, optional
            To select a subpopulation of axon for the clamp, If not None mask is generated using :meth:`pandas.DataFrame.eval` of this expression, by default None
        mask_labels : None | Iterable[str] | str, optional
            To select a subpopulation of axon for the clamp, Label or list of labels already added to the axon populations population, by default []
        ax_list     : None | list
            To select a subpopulation of axon for the clamp, list of axons to insert the clamp on, if None, all axons are stimulated, by default None
        """
        self.intra_stim_position.append(position)
        self.intra_stim_t_start.append(t_start)
        self.intra_stim_duration.append(duration)
        self.intra_stim_amplitude.append(amplitude)

        if ax_list is not None:
            self.intra_stim_ON.append(ax_list)
        else:
            self.intra_stim_ON.append(
                self.axons.get_mask(expr=expr, mask_labels=mask_labels, otype="list")
            )
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
    def __update_sim_list(self):
        self.__set_elec_mask()
        self.sim_list = (
            self.axons.get_sub_population(mask_labels=self.sim_mask)
            .index.astype(int)
            .to_list()
        )

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
        if not self.axons.has_node_shift:
            self.axons.generate_random_NoR_position()
        self.__update_sim_list()
        for k in self.sim_list:
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

    def __set_pbar_label(self, n_proc: int, **kwargs):
        if "pbar_label" in kwargs:
            __label = kwargs["pbar_label"]
        else:
            __label = f"Fascicle {self.ID}"
        __label += f" -- {n_proc} CPU"
        if n_proc > 1:
            __label += "s"
        return __label

    def sim_axon(
        self,
        k_sim,
    ) -> axon_results:
        """
        Internal use only simumlated one axon of the fascicle

        Parameters
        ----------
        k       : int
            ID of the axon to simulate
        """
        ## test axon axons_type[k]
        k = self.sim_list[k_sim]
        assert self.axons["types"][k] in [0, 1]
        axon = self.__generate_axon(k)
        ## add extracellular stimulation
        axon.attach_extracellular_stimulation(self.extra_stim)
        ## add recording mechanism
        if self.record:
            axon.attach_extracellular_recorder(self.recorder)
        # add intracellular stim
        if self.N_intra > 0:
            for j in range(self.N_intra):
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
        # print(axon.recorder.save())
        if axon_sim["Simulation_state"] != "Successful":
            rise_error(
                "SimulationError: ",
                f"something went wrong during the simulation of axon {k}:\n",
                self.axons.iloc(k),
            )
        del axon

        axon_sim = self.postproc_function(axon_sim, **self.postproc_kwargs)
        if self.save_results:
            ax_fname = "sim_axon_" + str(k) + ".json"
            axon_sim.save(save=True, fname=self.result_folder_name + "/" + ax_fname)
        return axon_sim

    def simulate(
        self,
        pbar_off=False,
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
        in_nerve = "in_nerve" in kwargs
        if not self.save_results:
            if self.return_parameters_only:
                rise_warning(
                    "Fascicle's simulation parameters are misused",
                    "results are neither saved or return",
                    "save anyway",
                )
                self.save_results = True
        self.__init_axon_postprocessing()
        if not self.axons.has_node_shift:
            self.axons.generate_random_NoR_position()
        # create folder and save fascicle config
        self.result_folder_name = self.save_path + "Fascicle_" + str(self.ID)
        if len(
            self.save_path
        ):  # LR: Force folder creation if any save_path is specified --> usefull for some PP functions (ex: scatter_plot)
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
            self.loaded_footprints = True  # To set __footprint_to_compute to false
            if (
                "model" in self.extra_stim.__dict__
            ):  #!! for nerve no model to investigate
                bckup = self.extra_stim.model  # Can't be passed to mp pool :'(
                del self.extra_stim.model

        # create ID for all axons
        self.__update_sim_list()
        axons_ID = np.arange(len(self.sim_list))

        ## perform simulations in //
        results = []
        _n_proc = self.n_proc or parameters.get_nmod_ncore()
        _n_proc = min(_n_proc, self.n_ax)
        # Todo add upperlevel progress handler in nerve.simulate()
        with progress.Progress(
            "[progress.description]{task.description}",
            "{task.completed} / {task.total}",
            progress.BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
            disable=pbar_off,
        ) as pg:
            __label = self.__set_pbar_label(_n_proc, **kwargs)
            task_id = pg.add_task(f"[cyan]{__label}:", total=self.n_ax)
            # with mp.get_context('spawn').Pool(parameters.get_nmod_ncore()) as pool:  #forces spawn mode
            with get_pool(_n_proc, backend="spawn") as pool:
                for result in pool.imap(self.sim_axon, axons_ID):
                    results.append(result)
                    pg.advance(task_id)
                    pg.refresh()
                pool.close()  # LR: Apparently this avoid PETSC Terminate ERROR
                pool.join()  # LR: but this shouldn't be needed as we are in "with"...

        # results = list(pool_results)

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

        # dirty hack to force NRV_class instead of dict
        if not self.return_parameters_only:
            fasc_sim["axons"] = load_any(fasc_sim["axons"])
            if "extra_stim" in fasc_sim:
                fasc_sim["extra_stim"] = load_any(fasc_sim["extra_stim"])
            if self.record:
                fasc_sim["recorder"] = load_any(fasc_sim["recorder"])

        if self.verbose and not in_nerve:
            pass_info("... Simulation done")
        fasc_sim["is_simulated"] = True
        self.is_simulated = True
        return fasc_sim

    # ---------------------------------------------- #
    #               DEPRECATED Methods               #
    # ---------------------------------------------- #
    @property
    def y_grav_center(self):
        """
        :meta private:
        """
        rise_warning(
            DeprecationWarning,
            "fascicle.y_grav_center property is obsolete use fascicle.y instead",
        )
        return self.y

    @property
    def z_grav_center(self):
        """
        Area of the fascicle
        """
        rise_warning(
            DeprecationWarning,
            "fascicle.z_grav_center property is obsolete use fascicle.geom.z instead",
        )
        return self.z

    @property
    def N(self):
        """
        :meta private:
        """
        rise_warning(
            DeprecationWarning,
            "fascicle.N property is obsolete use fascicle.n_ax instead",
        )
        return self.n_ax

    @property
    def A(self):
        """
        Area of the fascicle
        """
        rise_warning(
            DeprecationWarning,
            "fascicle.A property is obsolete use fascicle.geom.area instead",
        )
        return self.geom.area

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
        rise_warning(
            DeprecationWarning,
            "define_circular_contour is deprecated, use define_geometry instead.",
        )
        if y_c is not None and z_c is not None:
            center = y_c, z_c
        else:
            center = None
        self.axons.reshape_geometry(radius=D / 2, center=center)

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
        rise_warning(
            DeprecationWarning,
            "define_circular_contour is deprecated, use define_geometry instead.",
        )
        return self.axons.geom.radius, self.axons.geom.center

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
        # TODO implement a fit contour method
        rise_warning(
            DeprecationWarning,
            "fit_circular_contour method usage is not recommended anymore and will be removed in future release. Nothing was done",
        )
        pass_info("Define fascicle size/shape at object creation instead.")

    def fill_with_population(
        self,
        axons_diameter: np.array = None,
        axons_type: np.array = None,
        y_axons: np.array = None,
        z_axons: np.array = None,
        fit_to_size: bool = False,
        delta: float = 1,
        delta_in: float | None = None,
        delta_trace: float = 1,
        method: Literal["default", "packing"] = "default",
        overwrite=False,
        n_iter: int = 500,
    ) -> None:
        """
        Fill the fascicle with an axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        y_axons             : np.array
            y coordinate of the axon population, in um
        z_axons             : np.array
            z coordinate of the axons population, in um
        delta               : float
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        """
        rise_warning(
            DeprecationWarning,
            "fascicle.fill_with_population deprecated, use fascicle.axons.place_population or fascicle.fill instead",
        )
        if axons_diameter is not None and axons_type is not None:
            self.axons.create_population(
                data=(axons_type, axons_diameter), overwrite=overwrite
            )
        pos = None
        if y_axons is not None and z_axons is not None:
            pos = (y_axons, z_axons)
        self.axons.place_population(
            pos=pos,
            fit_to_size=fit_to_size,
            delta=delta,
            delta_in=delta_in,
            delta_trace=delta_trace,
            method=method,
            n_iter=n_iter,
            overwrite=overwrite,
        )

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
        rise_warning(
            DeprecationWarning,
            "fascicle.translate_axons is deprecated and migth be removed in future version, use fascicle.translate instead",
        )
        self.translate((y, z), with_geom=False, with_context=False)

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
        rise_warning(
            DeprecationWarning,
            "fascicle.translate_fascicle is deprecated and migth be removed in future version, use fascicle.translate instead",
        )
        self.translate((y, z), with_axon=False)

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
        rise_warning(
            DeprecationWarning,
            "fascicle.rotate_axons is deprecated and migth be removed in future version, use fascicle.rotate instead",
        )
        self.translate(theta, with_geom=False, with_context=False)

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
        rise_warning(
            DeprecationWarning,
            "fascicle.rotate_fascicle is deprecated and migth be removed in future version, use fascicle.rotate instead",
        )
        self.translate(theta)

    def generate_random_NoR_position(self):
        """
        Generates radom Node of Ranvier shifts to prevent from axons with the same diamters to be aligned.
        """
        pass_info(
            DeprecationWarning,
            "fascicle.generate_random_NoR_position is depercated, use fascicle.axons.generate_random_NoR_position",
        )
        # also generated for unmyelinated but the meaningless value won't be used
        self.axons.generate_random_NoR_position()

    def generate_ligned_NoR_position(self, x=0):
        """
        Generates Node of Ranvier shifts to aligned a node of each axon to x postition.

        Parameters
        ----------
        x    : float
            x axsis value (um) on which node are lined, by default 0
        """
        pass_info(
            DeprecationWarning,
            "fascicle.generate_ligned_NoR_position is depercated, use fascicle.axons.generate_ligned_NoR_position",
        )
        # also generated for unmyelinated but the meaningless value won't be used
        self.axons.generate_ligned_NoR_position(x=x)

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
