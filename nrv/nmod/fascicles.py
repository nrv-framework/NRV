"""
NRV-fascicles
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import os

import matplotlib.pyplot as plt
import numpy as np

from ..backend.file_handler import *
from ..backend.log_interface import pass_info, rise_warning
from ..backend.MCore import MCH, synchronize_processes
from ..backend.NRV_Simulable import NRV_simulable, sim_results
from ..fmod.extracellular import *
from ..fmod.recording import *
from ..utils.cell.CL_postprocessing import *
from .axons import *
from .fascicle_generator import *
from .myelinated import *
from .unmyelinated import *



# Parallel computing options
if not MCH.is_alone():
    fg_verbose = False
    if MCH.do_master_only_work():
        fg_verbose = True

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

OTF_PP_path = os.environ["NRVPATH"] + "/_misc/OTF_PP/"
OTF_PP_library = os.listdir(OTF_PP_path)

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
    """
    Class for Fascicle, defined as a group of axons near one to the other in the same Perineurium Sheath. All axons are independant of each other, no ephaptic coupling.
    """

    def __init__(self, ID=0, **kwargs):
        """
        Instrantation of a Fascicle

        Parameters
        ----------
        dt              : float
            simulation time stem for Neuron (ms), by default 1us
        Nseg_per_sec    : float
            number of segment per section in Neuron. If set to 0, the number of segment per section is calculated with the d-lambda rule
        freq            : float
            frequency of the d-lambda rule (Hz), by default 100Hz
        freq_min        : float
            minimum frequency for the d-lambda rule when meshing is irregular, 0 for regular meshing
        v_init          : float
            initial value for the membrane voltage (mV), specify None for automatic model choice of v_init
        T               : float
            temperature (C), specify None for automatic model choice of temperature
        ID              : int
            axon ID, by default set to 0
        threshold       : int
            membrane voltage threshold for spike detection (mV), by default -40mV
        """
        super().__init__()

        # to add to a fascicle/nerve common mother class
        self.save_path=""
        self.verbose=False
        self.postproc_script="default"
        self.return_parameters_only = True
        self.loaded_footprints = True
        self.save_results = True

        self.config_filename = ""
        self.type = "fascicle"
        self.ID = ID
        self.type = None
        self.L = None
        self.D = None
        # geometric properties
        self.y_grav_center = 0
        self.z_grav_center = 0
        self.N_vertices = 0
        self.y_vertices = np.array([])
        self.z_vertices = np.array([])
        self.A = 0
        # axonal content
        self.N = 0
        self.axons_diameter = np.array([])
        self.axons_type = np.array([])
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
        self.processes_status = ["preparing" for _ in range(MCH.size)]

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
            Pyhton dictionary containing all the fascicle information
        """
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
            bl += ["extra_stim", "footprints", "is_footprinted"]

        if not rec_context:
            bl += ["record", "recorder"]

        to_save = (save and _fasc_save) and MCH.do_master_only_work()
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
        self.set_axons_parameters(unmyelinated_nseg=self.L // 25)

    ## generate stereotypic Fascicle
    def define_circular_contour(self, D, y_c=None, z_c=None, N_vertices=100):
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
        N_vertices  : int
            Number of vertice in the compute the contour
        """
        self.type = "Circular"
        self.D = D
        if y_c is not None:
            self.y_grav_center = y_c
        if z_c is not None:
            self.z_grav_center = z_c
        self.N_vertices = N_vertices
        theta = np.linspace(-np.pi, np.pi, num=N_vertices)
        self.y_vertices = self.y_grav_center + (D / 2) * np.cos(theta)
        self.z_vertices = self.z_grav_center + (D / 2) * np.sin(theta)
        self.A = np.pi * (D / 2) ** 2

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
        if self.y_vertices == np.array([]) and self.D is None:
            D = 0
        elif self.D is not None:
            D = self.D
        else:
            y = (np.amax(self.y_vertices) - np.amin(self.y_vertices)) / 2
            z = (np.amax(self.z_vertices) - np.amin(self.z_vertices)) / 2
            D = np.abs(np.amax(self.y_vertices) - np.amin(self.y_vertices))
        return D, y, z

    def fit_circular_contour(self, y_c=None, z_c=None, Delta=0.1, N_vertices=100):
        """
        Define a circular countour to the fascicle

        Parameters
        ----------
        y_c         : float
            y coordinate of the circular contour center, in um
        z_c         : float
            z coordinate of the circular contour center, in um
        Delta       : float
            distance between farest axon and contour, in um
        N_vertices  : int
            Number of vertice in the compute the contour
        """
        N_axons = len(self.axons_diameter)
        D = 2 * Delta

        if y_c is not None:
            self.y_grav_center = y_c
        if z_c is not None:
            self.z_grav_center = z_c
        if N_axons == 0:
            pass_info("No axon to fit fascicul diameter set to " + str(D) + "um")
        else:
            for axon in range(N_axons):
                dist_max = (
                    self.axons_diameter[axon] / 2
                    + (
                        (self.y_grav_center - self.axons_y[axon]) ** 2
                        + (self.z_grav_center - self.axons_z[axon]) ** 2
                    )
                    ** 0.5
                )
                D = max(D, 2 * (dist_max + Delta))
        self.define_circular_contour(D, y_c=None, z_c=None, N_vertices=N_vertices)

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
        parallel=True,
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
        #### AXON GENERATION: parallelization if resquested ####
        Area_to_fill = 0
        # Note: generate a bit too much axons just in case
        if self.type == "Circular":
            Area_to_fill = np.pi * (self.D / 2 + 28) ** 2
        if parallel:
            if MCH.do_master_only_work():
                pass_info("Generating axons")
            # split the generation over the N cores
            (
                partial_axons_diameter,
                partial_axons_type,
                M_diam_list,
                U_diam_list,
            ) = fill_area_with_axons(
                Area_to_fill / MCH.size,
                percent_unmyel=percent_unmyel,
                FVF=FVF,
                M_stat=M_stat,
                U_stat=U_stat,
            )
            # gather results
            axons_diameter = MCH.gather_jobs_as_array(partial_axons_diameter)
            axons_type = MCH.gather_jobs_as_array(partial_axons_type)
        else:
            if MCH.do_master_only_work():
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
        if MCH.do_master_only_work():
            N = len(axons_diameter)
            pass_info("\n ... " + str(N) + " axons generated")
            if pop_fname is not None:
                save_axon_population(
                    pop_fname, axons_diameter, axons_type, comment=None
                )
            pass_info("Axon Packing is starting")
            axons_y, axons_z, iteration, FVF_array, probed_iter = axon_packer(
                axons_diameter,
                Delta=0.1,
                y_gc=self.y_grav_center,
                z_gc=self.z_grav_center,
                max_iter=20000,
                monitor=False,
            )
            # check for remaining collisions and delete problematic axons
            axons_diameter, axons_type, axons_y, axons_z = delete_collisions(
                axons_diameter, axons_type, axons_y, axons_z
            )
            N = len(axons_diameter)
            pass_info("... Axon Packing done")
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
                save_placed_axon_population(
                    ppop_fname,
                    self.axons_diameter,
                    self.axons_type,
                    self.axons_y,
                    self.axons_z,
                    comment=None,
                )
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(
            axons_diameter
        ).flatten()
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type).flatten()
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y).flatten()
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z).flatten()
        self.N = MCH.master_broadcasts_array_to_all(N)

    def fill_with_population(
        self, axons_diameter, axons_type, Delta=0.1, ppop_fname=None, FVF=0.55
    ):
        """
        Fill a geometricaly defined contour with an already generated axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        ppop_fname      : str
            optional, if specified, name file to store the placed population generated
        FVF             : float
            Fiber Volume Fraction estimated for the area. By default set to 0.55
        """
        if MCH.do_master_only_work():
            ## check the population area
            total_ax_area = 0
            for diam in axons_diameter:
                total_ax_area += np.pi * ((diam / 2) ** 2)
            if self.A * FVF > total_ax_area:
                rise_warning(
                    "Warning: the specified population maybe too small to fill the current fascicle"
                )
            N = len(axons_diameter)
            pass_info("\n ... " + str(N) + " axons loaded")
            if ppop_fname is not None:
                save_axon_population(
                    ppop_fname, axons_diameter, axons_type, comment=None
                )
            pass_info("Axon Packing is starting")
            axons_y, axons_z, iteration, FVF_array, probed_iter = axon_packer(
                axons_diameter,
                Delta=Delta,
                y_gc=self.y_grav_center,
                z_gc=self.z_grav_center,
                max_iter=20000,
                monitor=False,
            )
            # check for remaining collisions and delete problematic axons
            axons_diameter, axons_type, axons_y, axons_z = delete_collisions(
                axons_diameter, axons_type, axons_y, axons_z
            )
            N = len(axons_diameter)
            pass_info("... Axon Packing done")
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
                save_placed_axon_population(
                    ppop_fname,
                    self.axons_diameter,
                    self.axons_type,
                    self.axons_y,
                    self.axons_z,
                    comment=None,
                )
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(
            axons_diameter
        ).flatten()
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type).flatten()
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y).flatten()
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z).flatten()
        self.N = MCH.master_broadcasts_array_to_all(N)

    def fill_with_placed_population(
        self,
        axons_diameter,
        axons_type,
        axons_y,
        axons_z,
        check_inside=True,
        check_collision=True,
        ppop_fname=None,
    ):
        """
        Fill a geometricaly defined contour with an already generated axon population

        Parameters
        ----------
        axons_diameters     : np.array
            Array  containing all the diameters of the axon population
        axons_type          : np.array
            Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
        axons_y             : np.array
            y coordinate of the axons, in um
        axons_z             : np.array
            z coordinate of the axons, in um
        check_inside        : bool
            if True the placed axons position are checked to ensure all remaining axons at the end are inside the fascicle
        check_collision     : bool
            if True, possible remaining collisions are check in the loaded population, and thiner axons are deleted
        ppop_fname          : str
            optional, if specified, name file to store the placed population generated
        """
        if MCH.do_master_only_work():
            N = len(axons_diameter)
            if check_collision:
                # check for remaining collisions and delete problematic axons
                axons_diameter, axons_type, axons_y, axons_z = delete_collisions(
                    axons_diameter, axons_type, axons_y, axons_z
                )
                N = len(axons_diameter)
            # check if axons are inside the fascicle
            if check_inside:
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
                save_placed_axon_population(
                    ppop_fname,
                    self.axons_diameter,
                    self.axons_type,
                    self.axons_y,
                    self.axons_z,
                    comment=None,
                )
        else:
            axons_diameter = None
            axons_type = None
            axons_y = None
            axons_z = None
            N = None
        ## BRODCASTING RESULTS TO ALL PARALLEL OBJECTS
        self.axons_diameter = MCH.master_broadcasts_array_to_all(
            axons_diameter
        ).flatten()
        self.axons_type = MCH.master_broadcasts_array_to_all(axons_type).flatten()
        self.axons_y = MCH.master_broadcasts_array_to_all(axons_y).flatten()
        self.axons_z = MCH.master_broadcasts_array_to_all(axons_z).flatten()
        self.N = MCH.master_broadcasts_array_to_all(N)

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
        self.y_vertices += y
        self.z_vertices += z
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
        self.y_vertices += (
            np.cos(theta) * (self.y_vertices - y_c)
            - np.sin(theta) * (self.z_vertices - z_c)
        ) + y_c
        self.z_vertices += (
            np.sin(theta) * (self.y_vertices - y_c)
            + np.cos(theta) * (self.z_vertices - z_c)
        ) + z_c
        self.rotate_axons(theta, y_c=y_c, z_c=z_c)

    def remove_axons_electrode_overlap(self, electrode):
        """
        Remove the axons that could overlap an electrode

        Parameters
        ----------
        electrode : object
            electrode instance, see electrodes for more details
        """
        y, z, D = 0, 0, 0
        if is_LIFE_electrode(electrode):
            D = electrode.D
            y = electrode.y
            z = electrode.z
        elif is_analytical_electrode(electrode):
            y = electrode.y
            z = electrode.z
        else:
            # CUFF electrodes should not affect intrafascicular state
            return 0
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
                "From Fascicle level: Electrode/Axons overlap, "
                + str(len(colapse))
                + " axons will be removed from the fascicle"
            )
        self.N -= len(colapse)
        pass_info(self.N, "axons remaining")
        self.axons_diameter = self.axons_diameter[mask]
        self.axons_type = self.axons_type[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]

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
                    self.unmyelinated_param["model"] = kwargs[key]
                if not unmyelinated_only and key in self.myelinated_param:
                    self.myelinated_param["model"] = kwargs[key]

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

    def remove_unmyelinated_axons(self):
        """
        Remove all unmyelinated fibers from the fascicle
        """
        mask = self.axons_type.astype(bool)
        self.axons_diameter = self.axons_diameter[mask]
        self.axons_y = self.axons_y[mask]
        self.axons_z = self.axons_z[mask]
        self.axons_type = self.axons_type[mask]
        self.N = len(self.axons_diameter)
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
        self.N = len(self.axons_diameter)
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
        self.N = len(self.axons_diameter)
        if len(self.NoR_relative_position) != 0:
            # almost useless but here for coherence
            self.NoR_relative_position = self.NoR_relative_position[mask]

    ## Representation methods
    def plot(
        self, fig, axes, contour_color="k", myel_color="r", unmyel_color="b", num=False
    ):
        """
        plot the fascicle in the Y-Z plane (transverse section)

        Parameters
        ----------
        fig     : matplotlib.figure
            figure to display the fascicle
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
        if MCH.do_master_only_work():
            ## plot contour
            axes.plot(
                self.y_vertices, self.z_vertices, linewidth=2, color=contour_color
            )
            ## plot axons
            circles = []
            for k in range(self.N):
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
            if self.extra_stim is not None:
                for electrode in self.extra_stim.electrodes:
                    if electrode.type == "LIFE":
                        circles.append(
                            plt.Circle(
                                (electrode.y, electrode.z),
                                electrode.D / 2,
                                color="gold",
                                fill=True,
                            )
                        )
                    elif not is_FEM_electrode(electrode):
                        axes.scatter(electrode.y, electrode.z, color="gold")
            for circle in circles:
                axes.add_patch(circle)
            if num:
                for k in range(self.N):
                    axes.text(self.axons_y[k], self.axons_z[k], str(k))

    def plot_x(
        self, fig, axes, myel_color="r", unmyel_color="b", Myelinated_model="MRG"
    ):
        """
        plot the fascicle's axons along Xline (longitudinal)

        Parameters
        ----------
        fig     : matplotlib.figure
            figure to display the fascicle
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        myel_color      : str
            matplotlib color string applied to the myelinated axons. Red by default
        unmyel_color    : str
            matplotlib color string applied to the myelinated axons. Blue by default
        Myelinated_model : str
            model use for myelinated axon (use to calulated node position)
        """
        if MCH.do_master_only_work():
            if self.L is None or self.NoR_relative_position != []:
                drange = [
                    min(self.axons_diameter.flatten()),
                    max(self.axons_diameter.flatten()),
                ]
                polysize = np.poly1d(np.polyfit(drange, [0.5, 5], 1))
                for k in range(self.N):
                    relative_pos = self.NoR_relative_position[k]
                    d = round(self.axons_diameter.flatten()[k], 2)
                    if self.axons_type.flatten()[k] == 0.0:
                        color = unmyel_color
                        size = polysize(d)
                        axes.plot([0, self.L], np.ones(2) + k - 1, color=color, lw=size)
                    else:
                        color = myel_color
                        size = polysize(d)
                        axon = myelinated(
                            0,
                            0,
                            d,
                            self.L,
                            model=Myelinated_model,
                            node_shift=self.NoR_relative_position[k],
                        )
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
                                electrode.x * np.ones(2), [0, self.N - 1], color="gold"
                            )
                axes.set_xlabel("x (um)")
                axes.set_ylabel("axon ID")
                axes.set_yticks(np.arange(self.N))
                axes.set_xlim(0, self.L)
                plt.tight_layout()

    ## Context handeling methods
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

        parameters:
        ----------
            stimulation  : stimulation object, see Extracellular.stimulation help for more details
        """
        if is_extra_stim(stimulation):
            self.extra_stim = stimulation
        # remove everlaping axons
        for electrode in stimulation.electrodes:
            self.remove_axons_electrode_overlap(electrode)

    def change_stimulus_from_elecrode(self, ID_elec, stimulus):
        """
        Change the stimulus of the ID_elec electrods

        parameters:
        ----------
            ID_elec  : int
                ID of the electrode which should be changed
            stimulus  : stimulus
                new stimulus to set
        """
        if self.extra_stim is not None:
            self.extra_stim.change_stimulus_from_elecrode(ID_elec, stimulus)
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

    ## RECORDING MECHANIMS
    def attach_extracellular_recorder(self, rec):
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

        for i in range(self.N):
            if self.axons_type.flatten()[i] == 0.0:
                self.NoR_relative_position += [0.0]
            else:
                d = round(self.axons_diameter.flatten()[i], 2)
                node_length = get_MRG_parameters(d)[5]
                self.NoR_relative_position += [(x - 0.5) % node_length / node_length]
                # -0.5 to be at the node of Ranvier center as a node is 1um long

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
        mp_computation = False
        if is_FEM_extra_stim(self.extra_stim):
            mp_computation = (
                self.extra_stim.fenics and self.extra_stim.model.is_multi_proc
            )

            if MCH.do_master_only_work() or mp_computation:
                self.extra_stim.run_model()

        if MCH.do_master_only_work() or mp_computation:
            self.set_axons_parameters(**kwargs)
            for k in range(len(self.axons_diameter)):
                if self.axons_type[k] == 0:
                    axon = unmyelinated(
                        self.axons_y[k],
                        self.axons_z[k],
                        round(self.axons_diameter[k], 2),
                        self.L,
                        ID=k,
                        **self.unmyelinated_param,
                    )
                else:
                    axon = myelinated(
                        self.axons_y[k],
                        self.axons_z[k],
                        round(self.axons_diameter[k], 2),
                        self.L,
                        ID=k,
                        **self.myelinated_param,
                    )
                axon.attach_extracellular_stimulation(self.extra_stim)
                footprints[k] = axon.get_electrodes_footprints_on_axon(
                    save_ftp_only=save_ftp_only, filename=filename
                )
                del axon
            if save_ftp_only:
                json_dump(footprints, filename)
        else:
            pass
        synchronize_processes()
        if not mp_computation:
            self.footprints = MCH.master_broadcasts_array_to_all(footprints)
        else:
            self.footprints = footprints
        self.is_footprinted = True
        return footprints

    def get_electrodes_footprints_on_axons(
        self, save_ftp_only=False, filename="electrodes_footprint.ftpt", **kwargs
    ):
        rise_warning(
            "Deprecation method get_electrodes_footprints_on_axons",
            "\nuse get_electrodes_footprints_on_axons instead",
        )
        self.compute_electrodes_footprints(
            save_ftp_only=save_ftp_only, filename=filename, **kwargs
        )

    def __sim_axon(
        self,
        k,
        is_master_slave=False,
        **kwargs,
    ):
        """
        Internal use only simumlated one axon of the fascicle

        Parameters
        ----------
        k       : int
            ID of the axon to simulate
        """
        ## test axon axons_type[k]
        assert self.axons_type[k] in [0, 1]
        if self.axons_type[k] == 0:
            axon = unmyelinated(
                self.axons_y[k],
                self.axons_z[k],
                round(self.axons_diameter[k], 2),
                self.L,
                ID=k,
                **self.unmyelinated_param,
            )
        else:
            axon = myelinated(
                self.axons_y[k],
                self.axons_z[k],
                round(self.axons_diameter[k], 2),
                self.L,
                ID=k,
                **self.myelinated_param,
            )
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
        if is_master_slave:
            ## perform simulation
            # loaded_footprints is suppose to be false
            # Request to server instantiate in FEM_stimulation.compute_electrodes_footprints
            # (called by axon.get_electrodes_footprints_on_axon)
            axon.get_electrodes_footprints_on_axon()
            axon_ftpt = None
        else:
            if self.loaded_footprints == True and self.is_footprinted:
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
        del axon
        return axon_sim

    def simulate(
        self,
        PostProc_Filtering=None,
        save_V_mem = False,
        **kwargs,
    ):
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
        if self.postproc_script is not None:
            import nrv  # not ideal at all but gives direct acces to nrv in the postprocessing script
        fasc_sim = super().simulate(**kwargs)
        if not MCH.do_master_only_work():
            fasc_sim = sim_results({})
        # disable the result storage only if results are fully return
        # To use with caution (mostly for optimisatino)
        if not self.save_results:
            if self.return_parameters_only:
                rise_warning(
                    "Fascicle's simulation parameters are misused",
                    "results are neither saved or return", 
                    "save anyway")
                self.save_results = True

        if len(self.NoR_relative_position) == 0:
            self.generate_random_NoR_position()
        # create folder and save fascicle config
        folder_name = self.save_path + "Fascicle_" + str(self.ID)
        if MCH.do_master_only_work() and self.save_results:
            create_folder(folder_name)
            self.config_filename = folder_name + "/00_Fascicle_config.json"
            fasc_sim.save(save=True, fname=self.config_filename)
        else:
            pass
        # impose myelinated_nseg_per_sec if footprint are loaded
        self.loaded_footprints = self.loaded_footprints and self.is_footprinted
        if self.loaded_footprints:
            kwargs["myelinated_nseg_per_sec"] = self.myelinated_param["Nseg_per_sec"]
            kwargs["unmyelinated_nseg"] = self.unmyelinated_param["Nseg_per_sec"]
        self.set_axons_parameters(**kwargs)
        self.processes_status = ["computing" for _ in range(MCH.size)]
        # Check if FEM should be done in parallel and do it if required
        mp_computation = False
        if is_FEM_extra_stim(self.extra_stim):
            mp_computation = (
                self.extra_stim.fenics and self.extra_stim.model.is_multi_proc
            )
        if mp_computation and not self.loaded_footprints:
            self.compute_electrodes_footprints()
            self.loaded_footprints = True
        # create ID for all axons
        axons_ID = np.arange(len(self.axons_diameter))

        # FEM STIMULATION IN PARALLEL: master computes FEM (only one COMSOL licence, other computes axons)
        if (
            self.extra_stim is not None
            and self.loaded_footprints == False
            and not is_analytical_extra_stim(self.extra_stim)
            and not MCH.is_alone()
            and not mp_computation
        ):
            is_master_slave = True
            # master solves FEM model
            if MCH.do_master_only_work():
                self.extra_stim.run_model()
            else:
                if self.extra_stim.fenics:
                    self.extra_stim.run_model()
            # synchronize all process
            synchronize_processes()
            # split the job
            this_core_mask = MCH.split_job_from_arrays_to_slaves(
                len(self.axons_diameter)
            )
            ## Axons simulation handle with Master/Slaves configuration:
            # Master: acts as a server, accepting request to compute external potential
            #   Also, update status of slaves when simulations complete
            # Slaves: computes neurons sending requests to the master
            #   (see FEM_stimulation.compute_electrodes_footprints)
            #   When simulations completed or interupted by an error,
            #   send status update ('success' or 'error') to Master
            ## MASTER ##
            if MCH.do_master_only_work():
                self.processes_status = ["server"] + [
                    "computing" for _ in range(MCH.size - 1)
                ]
                while "computing" in self.processes_status:
                    data = MCH.recieve_data_from_slave()
                    if "status" in data:
                        self.processes_status[data["rank"]] = data["status"]
                    else:
                        this_core_mask[data["ID"]] = True
                        V = self.extra_stim.model.get_potentials(
                            data["x"], data["y"], data["z"]
                        )
                        back_data = {"V": V}
                        MCH.send_back_array_to_dest(back_data, data["rank"])
                if "error" in self.processes_status:
                    errors_rank = [
                        i for i, x in enumerate(self.processes_status) if x == "error"
                    ]
                    errors_ax = [i for i, x in enumerate(this_core_mask) if x == False]
                    if len(errors_ax) > 0:
                        rise_warning(
                            "an issue occured during the simulation in rank: ",
                            errors_rank,
                            "\nThe following axons could not be computed: ",
                            errors_ax,
                        )
                    self.processes_status[data["rank"]]
                    self.processes_status[0] = ["error"]
                else:
                    self.processes_status[0] = ["success"]
            else:
                ## SLAVES ##
                try:
                    for k in this_core_mask:
                        axon_sim = self.__sim_axon(k,is_master_slave)
                        # postprocessing and data reduction
                        # (cannot be added to __sim.axon beceause nrv would not be global anymore)
                        if self.postproc_script.lower() in OTF_PP_library:
                            self.postproc_script = OTF_PP_path + self.postproc_script.lower()
                        elif self.postproc_script.lower() + ".py" in OTF_PP_library:
                            self.postproc_script = (
                                OTF_PP_path + self.postproc_script.lower() + ".py"
                            )
                        with open(self.postproc_script) as f:
                            code = compile(f.read(), self.postproc_script, "exec")
                            exec(code, globals(), locals())
                        if self.save_results:
                            ## store results
                            ax_fname = "sim_axon_" + str(k) + ".json"
                            #save_axon_results_as_json(axon_sim, folder_name + "/" + ax_fname)
                            axon_sim.save(save=True, fname=folder_name + "/" + ax_fname)
                        if not self.return_parameters_only:
                            fasc_sim.update({"axon"+str(k):axon_sim})
                    data = {"rank": MCH.rank, "status": "success"}
                    MCH.send_data_to_master(data)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                except:
                    data = {"rank": MCH.rank, "status": "error"}
                    MCH.send_data_to_master(data)
                    rise_error(
                        traceback.format_exc()
                    )
                # sum up all recorded extracellular potential if applicable
            synchronize_processes()
            if self.record:
                self.recorder.gather_all_recordings(master_computed=False)
        ###### NO STIM OR ANALYTICAL STIM: all in parallel, OR FEM STIM NO PARALLEL
        else:
            is_master_slave = False
            ## split the job between Cores/Computation nodes
            this_core_mask = MCH.split_job_from_arrays(len(self.axons_diameter))
            ## perform simulations
            if MCH.is_alone() and self.verbose:
                pass_info("Simulating axons in fascicle " + str(self.ID))
            for k in this_core_mask:
                if MCH.is_alone() and self.verbose:
                    pass_info("\t Axon " + f"{k+1}" + "/" + str(self.N), end="\r")
                axon_sim = self.__sim_axon(k, is_master_slave)
                # postprocessing and data reduction
                # (cannot be added to __sim.axon beceause nrv would not be global anymore)
                if self.postproc_script.lower() in OTF_PP_library:
                    self.postproc_script = OTF_PP_path + self.postproc_script.lower()
                elif self.postproc_script.lower() + ".py" in OTF_PP_library:
                    self.postproc_script = OTF_PP_path + self.postproc_script.lower() + ".py"
                with open(self.postproc_script) as f:
                    code = compile(f.read(), self.postproc_script, "exec")
                    exec(code, globals(), locals())
                ## store results
                if self.save_results:
                    ax_fname = "sim_axon_" + str(k) + ".json"
                    #save_axon_results_as_json(axon_sim, folder_name + "/" + ax_fname)
                    axon_sim.save(save=True, fname=folder_name + "/" + ax_fname)
                if not self.return_parameters_only:
                    fasc_sim.update({"axon"+str(k):axon_sim})
            # sum up all recorded extracellular potential if applicable
            synchronize_processes()
            if self.record:
                self.recorder.gather_all_recordings()
        if not self.return_parameters_only:
            synchronize_processes()
            fasc_sim = MCH.gather_jobs(fasc_sim)
        if MCH.is_alone() and self.verbose:
            pass_info("... Simulation done")
            fasc_sim["is_simulated"] = True
        self.is_simulated = True
        return fasc_sim
