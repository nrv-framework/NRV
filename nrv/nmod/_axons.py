"""
NRV-:class:`.axon` handling.
"""

import faulthandler
import os
import time
import traceback
from abc import abstractmethod

import neuron
import numpy as np

from .results._axons_results import axon_results
from ..backend._file_handler import json_dump
from ..backend._log_interface import rise_error, rise_warning
from ..backend._NRV_Simulable import NRV_simulable
from ..backend._parameters import parameters
from ..fmod._electrodes import *
from ..fmod._extracellular import *
from ..fmod._recording import *
from ..utils._units import sci_round

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()

# instructions for Neuron, find mod files and hide GUI
dir_path = parameters.nrv_path + "/_misc"
neuron.load_mechanisms(dir_path + "/mods")
neuron.h.load_file("stdrun.hoc")

# list of supported models
unmyelinated_models = [
    "HH",
    "Rattay_Aberham",
    "Sundt",
    "Tigerholm",
    "Schild_94",
    "Schild_97",
]
myelinated_models = [
    "MRG",
    "Gaines_motor",
    "Gaines_sensory",
]


##############################
## Usefull Neuron functions ##
##############################
def purge_neuron():
    """
    This function clears all the sections declared in neuron.h
    """
    for section in neuron.h.allsec():
        section = None


def d_lambda_rule(L, d_lambda, f, sec):
    """
    :meta private:
    computes the d_lambda rule for a sections and returns the number of segments.

    Parameters
    ----------
    L           : int
        length of the section (um)
    d_lambda    : float
        d_lambda value, usually between 0.1 and 0.3
    f           : float
        maximal ionic current frequency (Hz)
    sec         : neuron section
        current neuron section on which to compute dlambda rule

    Returns
    -------
    Nseg        : int
        number of segment recommended to the section
    """
    return int((L / (d_lambda * neuron.h.lambda_f(f, sec=sec)) + 0.999) / 2) * 2 + 1


def create_Nseg_freq_shape(N_sec, shape, freq, freq_min, alpha_max):
    """
    creates a vector with the size of N_sec, a number of section to create an axon,
    and creates a shape of frequency to use with the d-lambda rule along the axon.

    Parameters
    ----------
    Nsec        : int
        the number of sections that will be used to implement the axon
    shape       : str
        shape of the output vector, pick between:
            "pyramidal"         -> min frequencies on both sides and linear increase up to the middle at the maximum frequency
            "sigmoid"           -> same a befor with sigmoid increase instead of linear
            "plateau"           -> sale as pyramidal except the max frequency is holded on a central plateau
            "plateau_sigmoid"   -> same as previous with sigmoid increase
    freq        : float
        maximum value of the frequency for the d-lambda rule
    freq_min    : float
        minimum value of the frequency for the d-lambda rule
    alpha_max   : float
        proportion of the axon at the maximum frequency for plateau shapes

    Returns
    -------
    freqs   : np.array
        vector of frequency to apply to a multi-sections axon
    """
    if shape == "pyramidal":
        if (N_sec % 2) == 0:
            X = np.concatenate(
                [
                    np.linspace(0, 1, num=int(N_sec / 2)),
                    np.linspace(1, 0, num=int(N_sec / 2)),
                ]
            )
        else:
            X = np.concatenate(
                [
                    np.linspace(0, 1, num=int(N_sec / 2)),
                    np.asarray([1]),
                    np.linspace(1, 0, num=int(N_sec / 2)),
                ]
            )
    elif shape == "sigmoid":
        if (N_sec % 2) == 0:
            x_1 = np.linspace(-6, 6, num=int(N_sec / 2))
            x_2 = np.linspace(6, -6, num=int(N_sec / 2))
            X = np.concatenate(
                [
                    (1 / (1 + np.exp(-x_1))),
                    (1 / (1 + np.exp(-x_2))),
                ]
            )
        else:
            x_1 = np.linspace(-6, 6, num=int(N_sec / 2))
            x_2 = np.linspace(6, -6, num=int(N_sec / 2))
            X = np.concatenate(
                [
                    (1 / (1 + np.exp(-x_1))),
                    np.asarray([1]),
                    (1 / (1 + np.exp(-x_2))),
                ]
            )
    elif shape == "plateau_sigmoid":
        length = int(N_sec * (1.0 - alpha_max) / 2)
        x_1 = np.linspace(-6, 6, num=length)
        x_2 = np.linspace(6, -6, num=length)
        X = np.concatenate(
            [
                (1 / (1 + np.exp(-x_1))),
                np.ones(int(N_sec) - 2 * length),
                (1 / (1 + np.exp(-x_2))),
            ]
        )
    else:
        # pyramid with plateau shape
        length = int(N_sec * (1.0 - alpha_max) / 2)
        X = np.concatenate(
            [
                np.linspace(0, 1, num=length),
                np.ones(N_sec - 2 * length),
                np.linspace(1, 0, num=length),
            ]
        )
    # applying the shape to the number of sections between the two specified frequencies
    freqs = X * (freq - freq_min) + freq_min
    return freqs


def rotate_list(l, n):
    """
    rotate a list with a defined number of indexes to shift

    Parameters
    ----------
    l   : list
        list to rotate
    n   : int
        number of indexes to r

    Returns
    -------
    l   : list
    """
    return l[-n:] + l[:-n]


#############################
## Generic class for axons ##
#############################
class axon(NRV_simulable):
    """
    A generic object to describe an axonal fiber
    (soma and interconnection are not taken into account, all axons are independant from others).

    Note
    ----
    -   :class:`axon` is an abstract class so it cannot be used directly. From the user's point of view,
        only the child classes :class:`.myelinated` and :class:`.unmyelinated` should be used.
    -   All axons are assumed to be along the x-axis, as Neuron would do when creatnig a basic longitudinal geometry.

    Parameters
    ----------
    y               : float
        y-axis coordinate of the axon (um)
    z               : float
        z-axis coordinate of the axon (um)
    d               : float
        axon diameter (um)
    L               : float
        axon length (um)
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

    Warning
    -------
    do not create more than one axon at a time for one process, to prevent from parameters overlaps in Neuron
    """

    @abstractmethod
    def __init__(
        self,
        y=0,
        z=0,
        d=1,
        L=100,
        dt=0.001,
        Nseg_per_sec=0,
        freq=100,
        freq_min=0,
        mesh_shape="plateau_sigmoid",
        alpha_max=0.3,
        d_lambda=0.1,
        v_init=None,
        T=None,
        ID=0,
        threshold=-40,
        **kwargs,
    ):
        """
        initialisation of the axon,
        """
        super().__init__(**kwargs)
        self.type = "axon"
        ## Given by user
        self.x = []
        self.y = y
        self.z = z
        self.d = d
        self.L = L
        self.dt = dt
        self.Nseg_per_sec = Nseg_per_sec
        self.freq = freq
        self.freq_min = freq_min
        self.mesh_shape = mesh_shape
        self.alpha_max = alpha_max
        self.d_lambda = d_lambda
        self.v_init = v_init
        self.T = T
        self.ID = ID
        self.threshold = threshold
        self.model = None
        self.t_sim = 0
        self.sim_time = 0
        self.timeVector = None
        self.t_len = 0
        ## internal use
        self.created = False
        self.Nsec = 0
        self.Nseg = 0
        self.myelinated = ""

        self.set_parameters(**kwargs)

        ## Contexts
        # Intra stims
        self.intra_current_stim = []
        self.intra_current_stim_positions = []
        self.intra_current_stim_starts = []
        self.intra_current_stim_durations = []
        self.intra_current_stim_amplitudes = []
        self.intra_voltage_stim = None
        self.intra_voltage_stim_position = []
        self.intra_voltage_stim_stimulus = None

        # Extra stims
        self.extra_stim = None
        self.footprints = None
        ## recording mechanism
        self.record = False
        self.recorder = None
        ## abstract parameters
        self.x_rec = np.asarray([])
        self.rec = "all"
        self.node_index = None
        ## required for generate_axon_from_results
        if "diameter" in kwargs:
            self.d = kwargs["diameter"]

    def __del__(self):
        for section in neuron.h.allsec():
            section = None
        super().__del__()

    def __clear_reclists(self):
        keys = list(self.__dict__.keys())
        for key in keys:
            if "reclist" in key:
                del self.__dict__[key]

    def save(
        self,
        save=False,
        fname="axon.json",
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        blacklist=[],
    ):
        """
        Return axon as dictionary and eventually save it as json file
        WARNING to use BEFORE stimulation, (for post simulation savings use
        save_axon_results_as_json on results dictionary

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "axon.json"

        Returns
        -------
        ax_dic : dict
            dictionary containing all information
        """
        bc = [i for i in blacklist]
        bc += ["extra_stim", "intra_current_stim", "intra_voltage_stim"]
        if not intracel_context:
            bc += [
                "intra_current_stim_positions",
                "intra_current_stim_starts",
                "intra_current_stim_durations",
                "intra_current_stim_amplitudes",
                "intra_voltage_stim_position",
                "intra_voltage_stim_stimulus",
                "intra_voltage_stim_stimulus",
                "intra_voltage_stim_stimulus",
            ]
        if not extracel_context:
            bc += [
                "footprints",
            ]
        if not rec_context:
            bc += [
                "record",
                "recorder",
            ]

        key_dict = super().save(blacklist=bc)

        # As to be done separatly because mph object cannot be deep copied
        if extracel_context:
            key_dict["extra_stim"] = self.extra_stim.save()

        if save:
            json_dump(key_dict, fname)
        return key_dict

    def load(
        self,
        data,
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        blacklist=[],
    ):
        """
        Load all axon properties from a dictionary or a json file

        Parameters
        ----------
        data    : str or dict
            json file path or dictionary containing axon information
        """
        bc = [i for i in blacklist]
        if not intracel_context:
            bc += [
                "intra_current_stim_positions",
                "intra_current_stim_starts",
                "intra_current_stim_durations",
                "intra_current_stim_amplitudes",
                "intra_voltage_stim_position",
                "intra_voltage_stim_stimulus",
                "intra_voltage_stim_stimulus",
                "intra_voltage_stim_stimulus",
            ]
        if not extracel_context:
            bc += ["footprints", "extra_stim"]
        if not rec_context:
            bc += [
                "record",
                "recorder",
            ]

        super().load(data=data, blacklist=bc)
        com = "self._" + self.nrv_type + "__compute_axon_parameters()"
        eval(com)
        if intracel_context:
            for i in range(len(self.intra_current_stim_positions)):
                position = self.intra_current_stim_positions[i]
                stim_start = self.intra_current_stim_starts[i]
                duration = self.intra_current_stim_durations[i]
                amplitude = self.intra_current_stim_amplitudes[i]
                self.insert_I_Clamp(position / self.L, stim_start, duration, amplitude)
            if self.intra_voltage_stim_stimulus is not None:
                position = self.intra_voltage_stim_position[0]
                self.insert_V_Clamp(position / self.L, self.intra_voltage_stim_stimulus)

    def save_axon(
        self,
        save=False,
        fname="axon.json",
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
    ):
        rise_warning("save_axon is a deprecated method use save")
        self.save(
            save=save,
            fname=fname,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )

    def load_axon(
        self,
        data,
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
    ):
        rise_warning("load_axon is a deprecated method use load")
        self.save(data, extracel_context, intracel_context, rec_context)

    def plot(
        self, axes: plt.axes, color: str = "blue", elec_color="gold", **kwgs
    ) -> None:

        alpha = 1
        if "alpha" in kwgs:
            alpha = kwgs["alpha"]

        axes.add_patch(
            plt.Circle(
                (self.y, self.z),
                self.d / 2,
                color=color,
                fill=True,
                alpha=alpha,
            )
        )
        if self.extra_stim is not None:
            self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.d)

    def __define_shape(self):
        """
        Define the shape of the axon after all sections creation
        """
        neuron.h.define_shape()

    def topology(self):
        """
        call the neuron topology function to plot the current topology on prompt
        """
        neuron.h.topology()

    def __get_allseg_positions(self):
        """
        get the positions of all segments define by neuron using allsec()
        WARNING: for internal use only, this is used to get all  position for external field computation
        in extracellular stimulation methods. This methods ensures to take into accounts all segments in the
        simulation

        Returns
        -------
        x   : np.array
            array of x coordinates of the computation points, in um
        y   : float
            y coordinate of the axon, in um
        z   : float
            z coordinate of the axon, in um
        """
        y = self.y
        z = self.z
        x = []
        for sec in neuron.h.allsec():
            offset = sec.x3d(0)
            for seg in sec:
                x.append(offset + seg.x * sec.L)
        return np.asarray(x), y, z

    def __set_allseg_vext(self, vext):
        """
        set the external potential of all segments accordingly to a vector

        Parameters
        ----------
        vext    : list or array of values to give to all segments e_extracellular in all segment of all sections in the simulation, in mV
        """
        k = 0
        for sec in neuron.h.allsec():
            for seg in sec:
                seg.e_extracellular = vext[k]
                k += 1

    def attach_extracellular_stimulation(self, stim):
        """
        attach a extracellular context of simulation for an axon

        Parameters
        ----------
        stim     : stimulation object
            see Extracellular.stimulation help for more details
        """
        if is_extra_stim(stim):
            self.extra_stim = stim

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
            rise_warning("Cannot be changed: no extrastim in the axon")

    def get_electrodes_footprints_on_axon(
        self, save_ftp_only=False, filename="electrodes_footprint.ftpt"
    ):
        """
        get electrodes footprints on each axon segment

        Parameters
        ----------
        save_ftp_only        :bool
            if true save_ftp_only result in a .ftpt file
        filename    :str
            saving file name and path

        Returns
        -------
        footprints   :dict
        Dictionnary composed of extracellular footprint array, the keys are int value
        of the corresponding electrode ID
        """
        footprints = {}
        x, y, z = self.__get_allseg_positions()
        # self.extra_stim.synchronise_stimuli()
        self.extra_stim.compute_electrodes_footprints(x, y, z, self.ID)
        for i in range(len(self.extra_stim.electrodes)):
            elec = self.extra_stim.electrodes[i]
            footprints[i] = elec.footprint
        if save_ftp_only:
            json_dump(footprints, filename)
        self.footprints = footprints
        self.extra_stim.clear_electrodes_footprints()
        return footprints

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

    def simulate(
        self,
        **kwargs,
    ) -> axon_results:
        """
        Simulates the axon using neuron framework

        Parameters
        ----------
        t_sim               : float
            total simulation time (ms), by default 20 ms
        self.record_V_mem        : bool
            if true, the membrane voltage is recorded, set to True by default
                see unmyelinated/myelinated to see where recording occur
                results stored with the key "V_mem"
        self.record_I_mem        : bool
            if true, the membrane current is recorded, set to False by default
        self.record_I_ions       : bool
            if true, the ionic currents are recorded, set to False by default
        record_particules   : bool
            if true, the particule states are recorded, set to False by default
        self.loaded_footprints           :dict or bool
            Dictionnary composed of extracellular footprint array, the keys are int value
            of the corresponding electrode ID, if None, footprints calculated during the simulation,
            set to None by default

        Returns
        -------
        axon_sim    : dictionnary
            all informations on neuron, segment position and all simulation results
        """
        axon_sim = super().simulate(**kwargs)
        axon_sim["diameter"] = self.d
        axon_sim["tstop"] = self.t_sim
        axon_sim.update(self.__add_extrastim_to_res())
        t_sim = self.t_sim
        # set recorders arrays - KEEP THIS CODE BEFORE INITIALISATION
        self.__set_time_recorder()
        if self.record_V_mem:
            self.set_membrane_voltage_recorders()
        if self.record_I_mem or self.record:
            self.set_membrane_current_recorders()
        if self.record_I_ions:
            self.set_ionic_current_recorders()
        if self.record_g_mem or self.record_g_ions:
            self.set_conductance_recorders()
        if self.record_particles:
            self.set_particules_values_recorders()
            if hasattr(self, "Markov_Nav_modeled_NoR"):
                self.set_Nav_recorders()

        ## initialisation and parameters for neuron - KEEP THIS CODE JUST BEFORE SIMULATION
        neuron.h.tstop = t_sim
        neuron.h.celsius = self.T  # set temperature in celsius
        neuron.h.finitialize(self.v_init)  # initialize voltage state
        neuron.h.v_init = self.v_init
        if self.dt == 0:
            rise_warning(
                "Warning: for Axon "
                + str(self.ID)
                + ", the ODE resolution is with adaptive step, atol set to 0.001 in Neuron"
            )
            neuron.h("cvode_active(1)")
            neuron.h("cvode.atol(0.001)")
        else:
            neuron.h.dt = self.dt  # set time step (ms)

        try:
            start_time = time.time()
            neuron.h.frecord_init()
            ###########################################
            #### THIS IS WHERE SIMULATION IS HANDLED ##
            ###########################################
            if self.extra_stim is not None:
                # setup extracellular stimulation
                x, y, z = self.__get_allseg_positions()
                self.extra_stim.synchronise_stimuli()

                if self.loaded_footprints is None:
                    if self.footprints is None:
                        self.get_electrodes_footprints_on_axon()
                elif self.loaded_footprints:
                    if self.footprints is None:
                        rise_warning(
                            "no loaded footprints: computation will be done anyway"
                        )
                        self.get_electrodes_footprints_on_axon()
                elif not self.loaded_footprints:
                    self.get_electrodes_footprints_on_axon()
                self.extra_stim.set_electrodes_footprints(self.footprints)
                # compute the minimum time between stimuli changes, checks it"s not smaller than the computation dt, if so, there should be a warning to the user
                Delta_T_min = np.amin(np.diff(self.extra_stim.global_time_serie))
                if sci_round(Delta_T_min, 5) < sci_round(self.dt, 5):
                    ## WARNING: the stimulus is over sampled compared to the neuron dt:
                    if Delta_T_min / self.dt < 1:  # HERE!! FOr dt test only
                        # if the stimulus minimal change time is more than 10% of user specified dt, change it to avoid problem
                        # prints a warning as computation time will increase !
                        new_dt = self.dt / np.ceil(self.dt / Delta_T_min)
                        axon_sim["dt"] = new_dt
                        rise_warning("Specified dt is too low")
                        rise_warning(
                            "... automatically changing the user specified dt from "
                            + str(self.dt)
                            + " to "
                            + str(new_dt)
                            + " ms"
                        )
                        self.dt = new_dt
                        neuron.h.dt = self.dt
                    else:
                        rise_warning(
                            "Neuron will undersample the stimulus... \
                            this may be unfortunate, consider to undersample your stimuli yourself,\
                            or chose a smaller dt"
                        )
                        rise_warning(
                            "... dt is "
                            + str(Delta_T_min / self.dt)
                            + " times bigger \
                            than the stimulus minimum time step difference"
                        )
                # loop on stimuli time serie
                for i in range(1, len(self.extra_stim.global_time_serie)):
                    t_step = min(self.extra_stim.global_time_serie[i], t_sim)
                    vext = self.extra_stim.compute_vext(i - 1)
                    self.__set_allseg_vext(vext)
                    neuron.h.continuerun(t_step)
                # finish simulation if needed
                if neuron.h.t < t_sim:
                    vext = self.extra_stim.compute_vext(
                        len(self.extra_stim.global_time_serie) - 1
                    )
                    self.__set_allseg_vext(vext)
                    neuron.h.continuerun(neuron.h.tstop)
            elif self.intra_voltage_stim is not None:
                # init if first point is at 0
                if self.intra_voltage_stim_stimulus.t[0] == 0:
                    self.intra_voltage_stim.amp[0] = self.intra_voltage_stim_stimulus.s[
                        0
                    ]
                # run simulation with a loop on the voltage clamp times
                for i in range(1, len(self.intra_voltage_stim_stimulus.t)):
                    t_step = min(self.intra_voltage_stim_stimulus.t[i], t_sim)
                    # run simulation
                    neuron.h.continuerun(t_step)
                    # apply new voltage clamp value
                    self.intra_voltage_stim.amp[0] = self.intra_voltage_stim_stimulus.s[
                        i
                    ]
                # finish simulation if needed
                if neuron.h.t < t_sim:
                    neuron.h.continuerun(neuron.h.tstop)
            else:
                neuron.h.continuerun(neuron.h.tstop)
            ###########################################
            ###########################################
            ###########################################
            self.sim_time = time.time() - start_time
            # simulation done, store results
            axon_sim["Simulation_state"] = "Successful"
            axon_sim["sim_time"] = self.sim_time
            axon_sim["t"] = self.__get_time_vector()
            axon_sim["x_rec"] = self.x_rec
            if self.myelinated and self.rec != "nodes":
                axon_sim["node_index"] = self.node_index
            if self.record_V_mem:
                axon_sim["V_mem"] = self.get_membrane_voltage()
            if self.record_I_mem or self.record:
                axon_sim["I_mem"] = self.get_membrane_current()
            if self.record_g_mem:
                axon_sim["g_mem"] = self.get_membrane_conductance()
            if self.record_g_ions:
                if not self.myelinated:
                    if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
                        g_na_ax, g_k_ax, g_l_ax = self.get_ionic_conductance()
                        axon_sim["g_na"] = g_na_ax
                        axon_sim["g_k"] = g_k_ax
                        axon_sim["g_l"] = g_l_ax
                    elif self.model == "Tigerholm":
                        (
                            axon_sim["g_nav17"],
                            axon_sim["g_nav18"],
                            axon_sim["g_nav19"],
                            axon_sim["g_kA"],
                            axon_sim["g_kM"],
                            axon_sim["g_kdr"],
                            axon_sim["g_kna"],
                            axon_sim["g_h"],
                            axon_sim["g_naleak"],
                            axon_sim["g_kleak"],
                        ) = self.get_ionic_conductance()
                    else:
                        (
                            axon_sim["g_naf"],
                            axon_sim["g_nas"],
                            axon_sim["g_kd"],
                            axon_sim["g_ka"],
                            axon_sim["g_kds"],
                            axon_sim["g_kca"],
                            axon_sim["g_can"],
                            axon_sim["g_cat"],
                        ) = self.get_ionic_conductance()
                else:
                    if self.model == "MRG":
                        (
                            g_na_ax,
                            g_nap_ax,
                            g_k_ax,
                            g_l_ax,
                            g_i_ax,
                        ) = self.get_ionic_conductance()
                        axon_sim["g_na"] = g_na_ax
                        axon_sim["g_nap"] = g_nap_ax
                        axon_sim["g_k"] = g_k_ax
                        axon_sim["g_l"] = g_l_ax
                        axon_sim["g_i"] = g_i_ax
                    elif self.model in ["Gaines_motor", "Gaines_sensory"]:
                        (
                            g_na_ax,
                            g_nap_ax,
                            g_k_ax,
                            g_l_ax,
                            g_kf_ax,
                            g_q_ax,
                        ) = self.get_ionic_conductance()
                        axon_sim["g_na"] = g_na_ax
                        axon_sim["g_nap"] = g_nap_ax
                        axon_sim["g_k"] = g_k_ax
                        axon_sim["g_kf"] = g_kf_ax
                        axon_sim["g_l"] = g_l_ax
                        axon_sim["g_q"] = g_q_ax
                    else:
                        rise_warning(
                            "g_ions recorder not implemented for "
                            + self.model
                            + " model "
                        )
            if self.record_I_ions:
                if not self.myelinated:
                    if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
                        I_na_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_l"] = I_l_ax
                    else:
                        I_na_ax, I_k_ax, I_ca_ax = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_ca"] = I_ca_ax
                else:
                    if self.model == "MRG":
                        I_na_ax, I_nap_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_nap"] = I_nap_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_l"] = I_l_ax
                    elif self.model in ["Gaines_motor", "Gaines_sensory"]:
                        (
                            I_na_ax,
                            I_nap_ax,
                            I_k_ax,
                            I_kf_ax,
                            I_q_ax,
                            I_l_ax,
                        ) = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_nap"] = I_nap_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_kf"] = I_kf_ax
                        axon_sim["I_q"] = I_q_ax
                        axon_sim["I_l"] = I_l_ax
                    elif self.model in ["Extended_Gaines"]:
                        (
                            I_na_ax,
                            I_nap_ax,
                            I_k_ax,
                            I_kf_ax,
                            I_l_ax,
                        ) = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_nap"] = I_nap_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_kf"] = I_kf_ax
                        axon_sim["I_l"] = I_l_ax
                    else:  # should be RGK
                        I_na_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim["I_na"] = I_na_ax
                        axon_sim["I_k"] = I_k_ax
                        axon_sim["I_l"] = I_l_ax
            if self.record_particles:
                if not self.myelinated:
                    if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
                        m_ax, n_ax, h_ax = self.get_particles_values()
                        axon_sim["m"] = m_ax
                        axon_sim["n"] = n_ax
                        axon_sim["h"] = h_ax
                    elif self.model in ["Tigerholm"]:
                        (
                            m_nav18_ax,
                            h_nav18_ax,
                            s_nav18_ax,
                            u_nav18_ax,
                            m_nav19_ax,
                            h_nav19_ax,
                            s_nav19_ax,
                            m_nattxs_ax,
                            h_nattxs_ax,
                            s_nattxs_ax,
                            n_kdr_ax,
                            m_kf_ax,
                            h_kf_ax,
                            ns_ks_ax,
                            nf_ks_ax,
                            w_kna_ax,
                            ns_h_ax,
                            nf_h_ax,
                        ) = self.get_particles_values()
                        axon_sim["m_nav18"] = m_nav18_ax
                        axon_sim["h_nav18"] = h_nav18_ax
                        axon_sim["s_nav18"] = s_nav18_ax
                        axon_sim["u_nav18"] = u_nav18_ax
                        axon_sim["m_nav19"] = m_nav19_ax
                        axon_sim["h_nav19"] = h_nav19_ax
                        axon_sim["s_nav19"] = s_nav19_ax
                        axon_sim["m_nattxs"] = m_nattxs_ax
                        axon_sim["h_nattxs"] = h_nattxs_ax
                        axon_sim["s_nattxs"] = s_nattxs_ax
                        axon_sim["n_kdr"] = n_kdr_ax
                        axon_sim["m_kf"] = m_kf_ax
                        axon_sim["h_kf"] = h_kf_ax
                        axon_sim["ns_ks"] = ns_ks_ax
                        axon_sim["nf_ks"] = nf_ks_ax
                        axon_sim["w_kna"] = w_kna_ax
                        axon_sim["ns_h"] = ns_h_ax
                        axon_sim["nf_h"] = nf_h_ax
                    elif self.model in ["Schild_94"]:
                        (
                            d_can_ax,
                            f1_can_ax,
                            f2_can_ax,
                            d_cat_ax,
                            f_cat_ax,
                            p_ka_ax,
                            q_ka_ax,
                            c_kca_ax,
                            n_kd_ax,
                            x_kds_ax,
                            y1_kds_ax,
                            m_naf_ax,
                            h_naf_ax,
                            l_naf_ax,
                            m_nas_ax,
                            h_nas_ax,
                        ) = self.get_particles_values()
                        axon_sim["d_can"] = d_can_ax
                        axon_sim["f1_can"] = f1_can_ax
                        axon_sim["f2_can"] = f2_can_ax
                        axon_sim["d_cat"] = d_cat_ax
                        axon_sim["f_cat"] = f_cat_ax
                        axon_sim["p_ka"] = p_ka_ax
                        axon_sim["q_ka"] = q_ka_ax
                        axon_sim["c_ka"] = c_kca_ax
                        axon_sim["n_kd"] = n_kd_ax
                        axon_sim["x_kds"] = x_kds_ax
                        axon_sim["y1_kds"] = y1_kds_ax
                        axon_sim["m_naf"] = m_naf_ax
                        axon_sim["h_naf"] = h_naf_ax
                        axon_sim["l_naf"] = l_naf_ax
                        axon_sim["m_nas"] = m_nas_ax
                        axon_sim["h_nas"] = h_nas_ax
                    else:  # should be "Schild_97"
                        (
                            d_can_ax,
                            f1_can_ax,
                            f2_can_ax,
                            d_cat_ax,
                            f_cat_ax,
                            p_ka_ax,
                            q_ka_ax,
                            c_kca_ax,
                            n_kd_ax,
                            x_kds_ax,
                            y1_kds_ax,
                            m_naf_ax,
                            h_naf_ax,
                            m_nas_ax,
                            h_nas_ax,
                        ) = self.get_particles_values()
                        axon_sim["d_can"] = d_can_ax
                        axon_sim["f1_can"] = f1_can_ax
                        axon_sim["f2_can"] = f2_can_ax
                        axon_sim["d_cat"] = d_cat_ax
                        axon_sim["f_cat"] = f_cat_ax
                        axon_sim["p_ka"] = p_ka_ax
                        axon_sim["q_ka"] = q_ka_ax
                        axon_sim["c_ka"] = c_kca_ax
                        axon_sim["n_kd"] = n_kd_ax
                        axon_sim["x_kds"] = x_kds_ax
                        axon_sim["y1_kds"] = y1_kds_ax
                        axon_sim["m_naf"] = m_naf_ax
                        axon_sim["h_naf"] = h_naf_ax
                        axon_sim["m_nas"] = m_nas_ax
                        axon_sim["h_nas"] = h_nas_ax
                else:
                    if self.model == "MRG":
                        m_ax, mp_ax, h_ax, s_ax = self.get_particles_values()
                        axon_sim["m"] = m_ax
                        axon_sim["mp"] = mp_ax
                        axon_sim["h"] = h_ax
                        axon_sim["s"] = s_ax
                    elif self.model in ["Gaines_motor", "Gaines_sensory"]:
                        (
                            m_ax,
                            mp_ax,
                            h_ax,
                            s_ax,
                            n_ax,
                            q_ax,
                        ) = self.get_particles_values()
                        axon_sim["m"] = m_ax
                        axon_sim["mp"] = mp_ax
                        axon_sim["h"] = h_ax
                        axon_sim["s"] = s_ax
                        axon_sim["n"] = n_ax
                        axon_sim["q"] = q_ax
                    elif self.model in ["Extended_Gaines"]:
                        m_ax, mp_ax, s_ax, h_ax, n_ax = self.get_particles_values()
                        axon_sim["m"] = m_ax
                        axon_sim["mp"] = mp_ax
                        axon_sim["s"] = s_ax
                        axon_sim["h"] = h_ax
                        axon_sim["n"] = n_ax
                    else:  # Should be RGK
                        (
                            RGK_m_nav1p9_ax,
                            RGK_h_nav1p9_ax,
                            RGK_s_nav1p9_ax,
                            RGK_m_nax_ax,
                            RGK_h_nax_ax,
                            RGK_ns_ks_ax,
                            RGK_nf_ks_ax,
                        ) = self.get_particles_values()
                        axon_sim["m_nav19"] = RGK_m_nav1p9_ax
                        axon_sim["h_nav19"] = RGK_h_nav1p9_ax
                        axon_sim["s_nav19"] = RGK_s_nav1p9_ax
                        axon_sim["m_nax"] = RGK_m_nax_ax
                        axon_sim["h_nax"] = RGK_h_nax_ax
                        axon_sim["ns_ks"] = RGK_ns_ks_ax
                        axon_sim["nf_ks"] = RGK_nf_ks_ax
                if hasattr(self, "Markov_Nav_modeled_NoR"):
                    (
                        I_nav11_ax,
                        C1_nav11_ax,
                        C2_nav11_ax,
                        O1_nav11_ax,
                        O2_nav11_ax,
                        I1_nav11_ax,
                        I2_nav11_ax,
                        I_nav16_ax,
                        C1_nav16_ax,
                        C2_nav16_ax,
                        O1_nav16_ax,
                        O2_nav16_ax,
                        I1_nav16_ax,
                        I2_nav16_ax,
                    ) = self.get_Nav_values()
                    axon_sim["I_Nav11"] = I_nav11_ax
                    axon_sim["C1_nav11"] = C1_nav11_ax
                    axon_sim["C2_nav11"] = C2_nav11_ax
                    axon_sim["O1_nav11"] = O1_nav11_ax
                    axon_sim["O2_nav11"] = O2_nav11_ax
                    axon_sim["I1_nav11"] = I1_nav11_ax
                    axon_sim["I2_nav11"] = I2_nav11_ax
                    axon_sim["I_Nav16"] = I_nav16_ax
                    axon_sim["C1_nav16"] = C1_nav16_ax
                    axon_sim["C2_nav16"] = C2_nav16_ax
                    axon_sim["O1_nav16"] = O1_nav16_ax
                    axon_sim["O2_nav16"] = O2_nav16_ax
                    axon_sim["I1_nav16"] = I1_nav16_ax
                    axon_sim["I2_nav16"] = I2_nav16_ax
            # check for extracellular potential Recording, initialize, compute footprint and get potential
            if self.record:
                # init the potential, if already done by another axon nothing should be performed
                self.recorder.init_recordings(len(axon_sim["t"]))
                # compute footprints
                if self.myelinated == True:
                    self.recorder.compute_footprints(
                        axon_sim["x_nodes"],
                        self.y,
                        self.z,
                        self.d,
                        self.ID,
                        self.myelinated,
                    )
                    # compute extra-cellular potential and add it to already computed ones
                else:
                    self.recorder.compute_footprints(
                        axon_sim["x_rec"],
                        self.y,
                        self.z,
                        self.d,
                        self.ID,
                        self.myelinated,
                    )
                    # compute extra-cellular potential and add it to already computed ones
                self.recorder.set_time(axon_sim["t"])
                if self.myelinated and self.rec == "all":
                    self.recorder.add_axon_contribution(
                        axon_sim["I_mem"][axon_sim["node_index"]], self.ID
                    )
                else:
                    self.recorder.add_axon_contribution(axon_sim["I_mem"], self.ID)
                axon_sim["recorder"] = self.recorder.save()

        except KeyboardInterrupt:
            rise_error(
                KeyboardInterrupt,
                "\n Caught KeyboardInterrupt, simulation stoped by user, stopping process...",
            )
        except:
            axon_sim["Simulation_state"] = "Unsuccessful"
            axon_sim["Error_from_prompt"] = traceback.format_exc()
            rise_warning(
                "Simulation induced an error while using neuron: \n"
                + axon_sim["Error_from_prompt"]
            )
            axon_sim["Neuron_t_max"] = neuron.h.t
        self.__clear_reclists()
        return axon_sim

    ##############################
    ## Result recording methods ##
    ##############################
    def __set_time_recorder(self):
        """
        internal use: set recorders in neuron for the time vector
        """
        self.timeVector = neuron.h.Vector().record(neuron.h._ref_t)

    def __get_time_vector(self):
        """
        internal use: get the time vector and stor its length for further use

        Returns
        -------
        t   : np.array
            time vector of the previous simulation, numpy array
        """
        t = np.array(self.timeVector)
        self.t_len = len(t)
        return t

    ##############################
    ## Result handleling method ##
    ##############################
    def __add_extrastim_to_res(self):
        """ """
        axon_sim = {}
        axon_sim["intra_stim_positions"] = self.intra_current_stim_positions
        axon_sim["intra_stim_starts"] = self.intra_current_stim_starts
        axon_sim["intra_stim_durations"] = self.intra_current_stim_durations
        axon_sim["intra_stim_amplitudes"] = self.intra_current_stim_amplitudes
        if self.extra_stim != None:
            if is_analytical_extra_stim(self.extra_stim):
                # save material
                axon_sim["extracellular_context"] = "analytical"
                axon_sim["extracellular_material"] = self.extra_stim.material.name
                # save electrode positions
                electrodes_x = []
                electrodes_y = []
                electrodes_z = []
                for elec in self.extra_stim.electrodes:
                    electrodes_x.append(elec.x)
                    electrodes_y.append(elec.y)
                    electrodes_z.append(elec.z)
                axon_sim["extracellular_electrode_x"] = electrodes_x
                axon_sim["extracellular_electrode_y"] = electrodes_y
                axon_sim["extracellular_electrode_z"] = electrodes_z
                # save stimuli
                stimuli_list = []
                stimuli_time_list = []
                for stim in self.extra_stim.stimuli:
                    stimuli_list.append(stim.s)
                    stimuli_time_list.append(stim.t)
                axon_sim["extracellular_stimuli"] = stimuli_list
                axon_sim["extracellular_stimuli_t"] = stimuli_time_list
            else:
                axon_sim["extracellular_context"] = "FEM"
                axon_sim["model_name"] = self.extra_stim.model_fname
                axon_sim["endoneurium_material"] = self.extra_stim.endoneurium.name
                axon_sim["perineurium_material"] = self.extra_stim.perineurium.name
                axon_sim["epineurium_material"] = self.extra_stim.epineurium.name
                axon_sim["external_material"] = self.extra_stim.external_material.name
                # save electrode positions
                electrodes_x = []
                electrodes_type = []
                electrodes_y = []
                electrodes_z = []
                for electrode in self.extra_stim.electrodes:
                    if is_CUFF_electrode(electrode):
                        electrodes_x.append(electrode.x)
                        electrodes_y.append(0)
                        electrodes_z.append(0)
                        electrodes_type.append("CUFF")
                    else:
                        if is_LIFE_electrode(electrode):
                            electrodes_x.append(electrode.x + electrode.length / 2)
                            electrodes_type.append("LIFE")
                        electrodes_y.append(electrode.y)
                        electrodes_z.append(electrode.z)
                axon_sim["extracellular_electrode_type"] = electrodes_type
                axon_sim["extracellular_electrode_x"] = electrodes_x
                axon_sim["extracellular_electrode_y"] = electrodes_y
                axon_sim["extracellular_electrode_z"] = electrodes_z
                # save stimuli
                stimuli_list = []
                stimuli_time_list = []
                for stimulus in self.extra_stim.stimuli:
                    stimuli_list.append(stimulus.s)
                    stimuli_time_list.append(stimulus.t)
                axon_sim["extracellular_stimuli"] = stimuli_list
                axon_sim["extracellular_stimuli_t"] = stimuli_time_list
        return axon_sim

    def clear_I_Clamp(self):
        """
        Clear any I-clamp attached to the axon
        """
        self.intra_current_stim = []
        self.intra_current_stim_positions = []
        self.intra_current_stim_starts = []
        self.intra_current_stim_durations = []
        self.intra_current_stim_amplitudes = []

    def clear_V_Clamp(self):
        """
        Clear any V-clamp attached to the axon
        """
        self.intra_voltage_stim = None
        self.intra_voltage_stim_position = []
        self.intra_voltage_stim_stimulus = None

    ###########################
    ## Axon abstract methods ##
    ###########################
    @abstractmethod
    def insert_I_Clamp(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def insert_V_Clamp(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def set_membrane_voltage_recorders(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def set_membrane_current_recorders(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def set_ionic_current_recorders(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def set_conductance_recorders(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def set_particules_values_recorders(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def get_membrane_voltage(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def get_membrane_current(self):
        """
        :meta private:
        """
        pass

    @abstractmethod
    def get_ionic_current(self):
        """
        :meta private:
        """
        pass

    def get_membrane_conductance(self):
        """
        :meta private:
        """
        pass

    def get_membrane_capacitance(self):
        """
        :meta private:
        """
        pass

    def get_particules_values(self):
        """
        :meta private:
        """
        pass


class axon_test(axon):
    """
    :meta private:
    """

    def __init__(
        self,
        y,
        z,
        d,
        L,
        dt=0.001,
        Nseg_per_sec=0,
        freq=100,
        freq_min=0,
        mesh_shape="plateau_sigmoid",
        alpha_max=0.3,
        d_lambda=0.1,
        v_init=None,
        T=None,
        ID=0,
        threshold=-40,
    ):
        super().__init__(
            y,
            z,
            d,
            L,
            dt=0.001,
            Nseg_per_sec=0,
            freq=100,
            freq_min=0,
            mesh_shape="plateau_sigmoid",
            alpha_max=0.3,
            d_lambda=0.1,
            v_init=None,
            T=None,
            ID=0,
            threshold=-40,
        )

    def insert_I_Clamp(self):
        pass

    def insert_V_Clamp(self):
        pass

    def set_membrane_voltage_recorders(self):
        pass

    def set_membrane_current_recorders(self):
        pass

    def set_ionic_current_recorders(self):
        pass

    def set_conductance_recorders(self):
        pass

    def set_particules_values_recorders(self):
        pass

    def get_membrane_voltage(self):
        pass

    def get_membrane_current(self):
        pass

    def get_ionic_current(self):
        pass
