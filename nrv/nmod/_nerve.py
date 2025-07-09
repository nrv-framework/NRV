"""
NRV-:class:`.nerve` handling.
"""

import numpy as np

from ..backend._log_interface import pass_info, rise_warning
from ..backend._NRV_Class import load_any
from ..backend._NRV_Simulable import NRV_simulable
from ..utils.geom._misc import cshape_overlap_checker, create_cshape
from ..utils._stimulus import stimulus
from ._fascicles import *
from .results._nerve_results import nerve_results


#################
## Nerve class ##
#################
class nerve(NRV_simulable):
    r"""
    A nerve in NRV is defined as:
        - a list of :class:`.fascicle`
        - an `analytical` :class:`~nrv.fmod.extracellular.stimulation` or a :class:`~nrv.fmod.extracellular.FEM_stimulation` context

    A nerve can be instrumented by adding couples of electrodes+stimulus

    The extracellular context of the nerve is automatically generated from the context of its
    fascicles and an optional context added directly to the nerve.

    See Also
    --------
    :doc:`Simulables users guide</usersguide/simulables>`, :class:`Fascicle-class<._fascicles.fascicle>`, :class:`Axon-class<._axons.axon>`


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
         - Identification number of the nerve.
       *
         - ``L``
         - ``float``
         - None
         - Length of the nerve.
       *
         - ``D``
         - ``float``
         - None
         - Diameter of the nerve.
       *
         - ``y_grav_center``
         - ``float``
         - 0
         - y-position of the nerve center.
       *
         - ``z_grav_center``
         - ``float``
         - 0
         - z-position of the nerve center.
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
         - If ``True``, nerve configuration and all axon simulations results are saved in ``save_path`` directory.
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
    Customizable attributes can either be set using :meth:`nerve.set_parameters` or simply by reafecting the value of the attribute.

    Tip
    ---
    Additional simulation parameters can be changed using (:meth:`.nerve.set_axons_parameters`, :meth:`.nerve.change_stimulus_from_electrode`, ...).

    Parameters
    ----------
    length              : float
        Nerve length, in um
    diameter    : float
        Nerve diameter, in um
    Outer_D            : float
        Outer saline box diameter, in mm
    ID        : int
        Nerve unique identifier
    """

    def __init__(self, length=10_000, diameter=100, Outer_D=5, ID=0, **kwargs):
        """
        Instanciates an empty nerve.
        """
        super().__init__(**kwargs)

        # to add to a fascicle/nerve common mother class
        self.verbose = True
        self.loaded_footprints = True
        self.return_parameters_only = False
        self.save_results = False
        self.save_path = ""

        self.postproc_label = "default"
        self.postproc_function = None
        self.postproc_script = None
        self.postproc_kwargs = {}

        self.n_proc = None

        self.type = "nerve"
        self.L = length
        self.D = None
        self.Outer_D = Outer_D
        self.ID = ID

        # geometric properties
        self.y_grav_center: float = 0
        self.z_grav_center: float = 0

        # Update parameters with kwargs
        self.set_parameters(**kwargs)

        # Fascicular content
        self.fascicles_IDs: list[str] = []
        self.fascicles: dict[str, fascicle] = {}

        # Axons objects default parameters
        self.unmyelinated_param = {
            "model": "Rattay_Aberham",
            "dt": 0.001,
            "Nrec": 0,
            "Nsec": 1,
            "Nseg_per_sec": length // 25,
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
            "node_shift": 0,
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
        self.is_extra_stim = False
        self.added_extra_stims = []
        self.footprints = {}
        self.is_footprinted = False
        self.myelinated_nseg_per_sec = 3
        self.unmyelinated_nseg = length // 25
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
        self.is_simulated = False
        # Simulation status

        self.define_circular_contour(diameter)

    ## save/load methods
    def save(
        self,
        fname="nerve.json",
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        fascicles_context=True,
        save=True,
        _fasc_save=False,
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
        fascicles_context:  bool
            if True, add the fascicles are fully saved
        blacklist:          list[str]
            key to exclude from saving
        save:               bool
            if false only return the dictionary

        Returns
        -------
        key_dict:           dict
            Pyhton dictionary containing all the fascicle information
        """
        bl = [i for i in blacklist]

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

        if not fascicles_context:
            bl += ["fascicles"]

        to_save = save
        return super().save(
            fname=fname,
            save=to_save,
            blacklist=bl,
            intracel_context=intracel_context,
            extracel_context=extracel_context,
            rec_context=rec_context,
            _fasc_save=_fasc_save,
        )

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

        super().load(
            data=key_dic,
            blacklist=bl,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )

    ## Nerve property method
    @property
    def n_fasc(self):
        """
        Number of fascicles in the nerves

        Returns
        -------
        int
            Number of fascicles.
        """
        return len(self.fascicles)

    @property
    def n_ax(self):
        """
        Number of axons in the nerves

        Returns
        -------
        int
            Number of axons.
        """
        return self.get_n_ax()

    def get_n_ax(self, id_fasc: int | None = None) -> int:
        """
        Returns the number of axons in a given fascicle or in all the nerve

        Parameters
        ----------
        id_fasc : _type_, optional
            ID of the fascicle from which the number of axons is returned; if None, number of all axons in the nerve is returned, by default None

        Returns
        -------
        int
            Number of axons.
        """
        n = 0
        if id_fasc is None:
            id_fasc = self.fascicles.keys()
        elif not np.iterable(id_fasc):
            id_fasc = [id_fasc]
        for i_fasc in id_fasc:
            if i_fasc in self.fascicles:
                fasc = self.fascicles[i_fasc]
                n += fasc.n_ax
        return n

    def set_ID(self, ID):
        """
        set the ID of the nerve

        Parameters
        ----------
        ID : int
            ID number of the nerve
        """
        self.ID = ID

    def define_length(self, L):
        """
        Set the length over the x axis of the nerve

        Parameters
        ----------
        L   : float
            length of the nerve in um.
        """
        if self.extra_stim is not None or self.N_intra > 0:
            rise_warning(
                "Modifying length of a fascicle with extra or intra cellular context can lead to error"
            )
        self.L = L
        self.set_axons_parameters(unmyelinated_nseg=self.L // 25)
        for fasc in self.fascicles.values():
            fasc.define_length(L)
        if self.is_extra_stim:
            self.extra_stim.reshape_nerve(
                Nerve_D=self.D,
                Length=self.L,
                y_c=self.y_grav_center,
                z_c=self.z_grav_center,
            )

    ## generate stereotypic Nerve
    def define_circular_contour(self, D, y_c=None, z_c=None):
        """
        Define a circular countour to the nerve

        Parameters
        ----------
        D           : float
            diameter of the circular nerve contour, in um
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
        self.A = np.pi * (D / 2) ** 2
        if self.is_extra_stim:
            pass_info("FEM nerve resized!")
            self.extra_stim.reshape_nerve(
                Nerve_D=self.D,
                Length=self.L,
                y_c=self.y_grav_center,
                z_c=self.z_grav_center,
            )

    def get_circular_contour(self):
        """
        Returns the properties of the nerve contour considered as a circle (y and z center and diameter)

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

    def fit_circular_contour(self, y_c=None, z_c=None, delta=20, Delta=None):
        """
        Define a circular countour to the nerve

        Parameters
        ----------
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        delta       : float
            distance between farest axon and contour, in um
        """
        if Delta is not None:
            rise_warning(DeprecationWarning, "please use delta instead of Delta")
            delta = Delta
        N_fasc = len(self.fascicles)
        D = 2 * delta

        if y_c is not None:
            self.y_grav_center = y_c
        if z_c is not None:
            self.z_grav_center = z_c
        if N_fasc == 0:
            pass_info("No fascicles to fit - Nerve diameter set to " + str(D) + "um")
        else:
            _r = 0
            for fasc in self.fascicles.values():
                y_tr, z_tr = fasc.geom.get_trace(n_theta=1000)
                _r_fasc = np.hypot(
                    (y_tr - self.y_grav_center), (z_tr - self.z_grav_center)
                ).max()
                _r = np.max((_r, _r_fasc))
            self.D = 2 * (_r + delta)
            print(self.D)

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

    ## Fascicles handling methods
    def get_fascicles(self, ID_only=False):
        """
        Return a :class:`._fascicle.fascicle` object from it ID in the nerve

        Parameters
        ----------
        ID_only : bool, optional
            ID of the fascicle, by default False

        Returns
        -------
        _type_
            _description_
        """
        if ID_only:
            return self.fascicles_IDs
        else:
            return self.fascicles

    def add_fascicle(
        self,
        fascicle,
        ID: None | int = None,
        y: None | float = None,
        z: None | float = None,
        rot: None | float = None,
        degree: bool = False,
        **kwargs,
    ):
        """
        Add a fascicle to the list of fascicles

        Parameters
        ----------
        fascicle : object
            object that can be load to a fascicle to add to the nerve struture
        ID : None | int, optional
            ID of the fascicle, if None keep the value of from `fascicle`, by default None
        y :  None | float, optional
            y-position of the fascicle, if None keep the value of from `fascicle`, by default None
        z :  None | float, optional
            y-position of the fascicle, if None keep the value of from `fascicle`, by default None
        rot : None | float, optional
            Rotation angle of the fascicle, if None keep the value of from `fascicle`, by default None
        degree : bool, optional
            if true angle is considered in degree, by default False
        """
        fasc = load_any(fascicle, **kwargs)
        if not is_fascicle(fasc):
            rise_warning(
                "Only fascile (nrv object, dict or file) can be added with add fascicle method: nothing added"
            )
        else:
            if ID is not None:
                fasc.set_ID(ID)
            if y is None:
                y = fasc.y
            if z is None:
                z = fasc.z
            fasc.translate(y - fasc.y, z - fasc.z)
            if rot is not None:
                fasc.rotate(rot, degree=degree)
            if self.__check_fascicle_overlap(fasc):
                rise_warning(
                    "fascicles overlap:  fasicle " + str(fasc.ID) + " cannot be added"
                )
            else:
                if fasc.ID in self.fascicles_IDs:
                    pass_info(
                        "Fascicle "
                        + str(fasc.ID)
                        + " already in the nerve: will be replace"
                    )
                    self.fascicles[fasc.ID]
                else:
                    self.fascicles_IDs += [fasc.ID]
                    self.fascicles[fasc.ID] = fasc

                self.__merge_fascicular_context(self.fascicles[fasc.ID])
                self.fascicles[fasc.ID].define_length(self.L)

    def __check_fascicle_overlap(self, fasc: fascicle):
        """
        To handle in fascicle group
        """
        if len(self.fascicles) == 0:
            return False
        fasc_geom = [fasc_i.geom for fasc_i in self.fascicles.values()]
        return any(cshape_overlap_checker(s=fasc.geom, s_comp=fasc_geom))

    def __merge_fascicular_context(self, fasc: fascicle):
        if self.is_extra_stim:
            self.extra_stim.reshape_fascicle(fasc.geom, fasc.ID)
        if fasc.extra_stim is not None:
            self.attach_extracellular_stimulation(fasc.extra_stim)

        if fasc.recorder is not None:
            self.attach_extracellular_recorder(fasc.recorder)

        fasc.clear_context(intracel_context=False)

    ## Axons handling method
    def set_axons_parameters(
        self, unmyelinated_only=False, myelinated_only=False, **kwargs
    ):
        """
        set parameters of axons in the nerve

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
        if "Adelta_limit" in kwargs:
            self.Adelta_limit = kwargs["self.Adelta_limit"]

        for fasc in self.fascicles.values():
            fasc.set_axons_parameters(unmyelinated_only=True, **self.unmyelinated_param)
            fasc.set_axons_parameters(myelinated_only=True, **self.myelinated_param)

    def get_axons_parameters(self, unmyelinated_only=False, myelinated_only=False):
        """
        get parameters of axons in the nerve

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

    ## Representation methods
    def plot(
        self,
        axes: plt.axes,
        contour_color: str = "k",
        myel_color: str = "b",
        unmyel_color: str = "r",
        elec_color: str = "gold",
        num: bool = False,
        **kwgs,
    ):
        """
        plot the nerve in the Y-Z plane (transverse section)

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
        elec_color    : str
            matplotlib color string applied to the electrodes axons. Blue by default
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
                linewidth=4,
            )
        )
        for i in self.fascicles:
            fasc = self.fascicles[i]
            fasc.plot(
                axes=axes,
                contour_color="grey",
                myel_color=myel_color,
                unmyel_color=unmyel_color,
                num=num,
            )
        if self.extra_stim is not None:
            self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.D)
        axes.set_xlim((-1.1 * self.D / 2, 1.1 * self.D / 2))
        axes.set_ylim((-1.1 * self.D / 2, 1.1 * self.D / 2))

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
            self.added_extra_stims = None
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

    # Intra cellular
    def insert_I_Clamp(
        self,
        position: float,
        t_start: float,
        duration: float,
        amplitude: float,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        ax_list: None | list = None,
        fasc_list: None | list = None,
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
        fasc_list     : None | list
            To select a subpopulation of axon for the clamp, list of fascicle to insert the clamp on, if None, all fascicle are stimulated, by default None
        """
        if fasc_list is None:
            fasc_list = list(self.fascicles.keys())
        for _fid, fasc in self.fascicles.items():
            if _fid in fasc_list:
                fasc.insert_I_Clamp(
                    position=position,
                    t_start=t_start,
                    duration=duration,
                    amplitude=amplitude,
                    mask_labels=mask_labels,
                    expr=expr,
                    ax_list=ax_list,
                )
        self.N_intra += 1

    def clear_I_clamp(self):
        """
        Clear any I-clamp attached to the nerve
        """
        for fasc in self.fascicles.values():
            fasc.clear_I_clamp()
        self.N_intra = 0

    # Extracellular
    def attach_extracellular_stimulation(self, stimulation):  #: FEM_stimulation):
        """
        attach a extracellular context of simulation for an axon.

        Parameters
        ----------
            stimulation  : stimulation object, see Extracellular.stimulation help for more details
        """
        if not self.is_extra_stim:
            self.extra_stim = FEM_stimulation(
                endo_mat=stimulation.endoneurium,
                peri_mat=stimulation.perineurium,
                epi_mat=stimulation.epineurium,
                ext_mat=stimulation.external_material,
            )

            self.extra_stim.reshape_outerBox(self.Outer_D)
            self.extra_stim.reshape_nerve(
                Nerve_D=self.D,
                Length=self.L,
                y_c=self.y_grav_center,
                z_c=self.z_grav_center,
            )
            self.extra_stim.remove_fascicles()
            for fasc in self.fascicles.values():
                self.extra_stim.reshape_fascicle(
                    geometry=fasc.geom,
                    ID=fasc.ID,
                )
            self.is_extra_stim = True

        for i, elec in enumerate(stimulation.electrodes):
            _overlap = self.__check_perineurium_electrode_overlap(elec)
            if _overlap == -1:
                self.extra_stim.add_electrode(elec, stimulation.stimuli[i])
                for fasc in self.fascicles.values():
                    fasc.remove_axons_electrode_overlap(elec)
            else:
                rise_warning(
                    f"Electrode {i} ovelerlap with the perineurium the fascicle {_overlap}"
                )

    def change_stimulus_from_electrode(self, ID_elec, stimulus):
        """
        Change the stimulus of the ID_elec electrods

        Parameters
        ----------
            ID_elec  : int
                ID of the electrode which should be changed
            stimulus  : stimulus
                New stimulus to set
        """
        if self.extra_stim is not None:
            self.extra_stim.change_stimulus_from_electrode(ID_elec, stimulus)
        else:
            rise_warning("Cannot be changed: no extrastim in the nerve")

    def __check_perineurium_electrode_overlap(self, electrode: electrode) -> int:
        """
        Check if an electrode overlap with one fascicle perineurium of the nerve.

        Paramters
        ---------
        electrode   : electrode
            electrode to check

        Returns
        -------
        int
            ID of the fascicle overlapping, -1 if no overlap
        """
        y, z, d = 0, 0, 0.001
        # CUFF electrodes do not affect intrafascicular state
        if not is_CUFF_electrode(electrode):
            y = electrode.y
            z = electrode.z
            if is_LIFE_electrode(electrode):
                d = electrode.D
            e_geom = create_cshape(center=(y, z), diameter=d)
            for fasc in self.fascicles.values():
                if cshape_overlap_checker(
                    s=fasc.geom,
                    s_comp=e_geom,
                    on_trace=True,
                ):
                    return fasc.ID
        return -1

    # RECORDING MECHANIMS
    def attach_extracellular_recorder(self, rec: recorder):
        """
        attach an extracellular recorder to the axon

        Parameters
        ----------
        rec     : recorder object
            see Recording.recorder help for more details
        """
        if is_recorder(rec):
            if self.recorder is None:
                self.recorder = rec
            else:
                for rec_p in rec.recording_points:
                    self.recorder.add_recording_point(rec_p)
            self.record = True

    def shut_recorder_down(self):
        """
        Shuts down the recorder locally
        """
        self.record = False
        for fasc in self.fascicles.values():
            fasc.shut_recorder_down()

    def __set_fascicles_context(self):
        """ """
        for fasc in self.fascicles.values():
            if self.extra_stim is not None:
                fasc.attach_extracellular_stimulation(self.extra_stim)
            if self.recorder is not None:
                fasc.attach_extracellular_recorder(self.recorder)

    def __set_fascicles_simulation_parameters(self):
        self.__set_fascicles_context()
        for fasc in self.fascicles.values():
            fasc.t_sim = self.t_sim
            fasc.record_V_mem = self.record_V_mem
            fasc.record_I_mem = self.record_I_mem
            fasc.record_I_ions = self.record_I_ions
            fasc.record_g_mem = self.record_g_mem
            fasc.record_g_ions = self.record_g_ions
            fasc.record_particles = self.record_particles

            fasc.postproc_script = self.postproc_script
            fasc.postproc_label = self.postproc_label
            fasc.postproc_function = self.postproc_function
            fasc.save_results = self.save_results
            fasc.return_parameters_only = self.return_parameters_only
            fasc.verbose = self.verbose

    # Footprint and mesh
    @property
    def __footprint_to_compute(self):
        """
        returns True only if loaded footprint are selected AND footprint exist
        """
        return not (self.is_footprinted and self.loaded_footprints)

    def compute_electrodes_footprints(self, **kwargs):
        """
        compute electrodes footprints
        """
        if not self.is_footprinted:
            if self.verbose:
                pass_info("...computing electrodes footprint")
            self.__set_fascicles_context()
            self.set_axons_parameters(**kwargs)
            if self.is_extra_stim:
                if is_FEM_extra_stim(self.extra_stim):
                    self.extra_stim.run_model()
                for fasc in self.fascicles.values():
                    fasc.compute_electrodes_footprints()
            self.is_footprinted = True

    ## SIMULATION
    def simulate(
        self,
        **kwargs,
    ) -> nerve_results:
        """
        Simulate the nerve with the proposed extracellular context. Top level method for large
        scale neural simulation.

        Parameters
        ----------

        Warning
        -------
        calling this method can result in long processing time, even with large computational ressources.
        Keep aware of what is really implemented, ensure configuration and simulation protocol is correctly designed.
        """
        if self.verbose:
            pass_info("Starting nerve simulation")
        nerve_sim = super().simulate(**kwargs)
        self.__set_fascicles_simulation_parameters()

        if (
            self.save_path
        ):  # LR: Force folder creation if any save_path is specified --> usefull for some PP functions (ex: scatter_plot)
            folder_name = self.save_path + "Nerve_" + str(self.ID) + "/"
            create_folder(folder_name)

        if self.save_results:
            folder_name = self.save_path + "Nerve_" + str(self.ID) + "/"
            config_filename = folder_name + "/00_Nerve_config.json"
            self.save(config_filename, fascicles_context=False)

        # run FEM model
        if self.__footprint_to_compute and self.has_FEM_extracel:
            self.compute_electrodes_footprints()
            self.loaded_footprints = True

        # Simulate all fascicles
        fasc_kwargs = kwargs
        if self.save_path:
            fasc_kwargs["save_path"] = folder_name
        if self.verbose:
            i_pbar = 1

        for fasc in self.fascicles.values():
            if self.verbose:
                fasc_kwargs["pbar_label"] = f"fascicle {i_pbar}/{self.n_fasc}"
                i_pbar += 1
            nerve_sim["fascicle" + str(fasc.ID)] = fasc.simulate(
                in_nerve=True,
                **fasc_kwargs,
            )
        if self.verbose:
            pass_info("...Done!")
        # dirty hack to force NRV_class type when saved
        if "extra_stim" in nerve_sim:
            nerve_sim["extra_stim"] = load_any(nerve_sim["extra_stim"])
        if self.record:  # recorder not saved in result !!BUG
            nerve_sim["recorder"] = self.recorder
        self.is_simulated = True
        return nerve_sim
