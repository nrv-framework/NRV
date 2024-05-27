"""
NRV-:class:`.axon_results` handling.
"""

import numpy as np
from numba import jit

from ...backend.NRV_Results import sim_results
from ...backend.file_handler import json_dump
from ...backend.log_interface import rise_warning, rise_error
from ...utils.units import to_nrv_unit, from_nrv_unit, convert, nm
from ...utils.misc import distance_point2line, membrane_capacitance_from_model, compute_complex_admitance

def max_spike_position(blocked_spike_positionlist, position_max, spike_begin="down"):
    if spike_begin == "down":
        while blocked_spike_positionlist[
            position_max + 1
        ] >= blocked_spike_positionlist[position_max] and position_max < (
            len(blocked_spike_positionlist) - 2
        ):
            position_max = position_max + 1
        return position_max
    else:
        while blocked_spike_positionlist[
            position_max + 1
        ] <= blocked_spike_positionlist[position_max] and position_max < (
            len(blocked_spike_positionlist) - 2
        ):
            position_max = position_max + 1
        return position_max


#@jit(nopython=True, fastmath=True)
def count_spike(onset_position):
    """
    spike counting, just in time compiled. For internal use only.
    """
    if len(onset_position) == 0:
        spike_number = 0
        return 0
    else:
        spike_number = 1
        for i in range(len(onset_position) - 1):
            if onset_position[i] == min(onset_position):
                if onset_position[i] == onset_position[i + 1]:
                    spike_number = spike_number + 1
    return spike_number


class axon_results(sim_results):
    """

    """

    def __init__(self, context=None):
        super().__init__(context)


    def is_recruited(self) -> bool:
        if not ("V_mem_raster_position") in  self:
            self.rasterize("V_mem")
        if len(self["V_mem_raster_position"]) == 0:
            return(False)
        else:
            return(True)

    def rasterize(
        self, my_key, t_start=0, t_stop=0, t_min_spike=0.1, t_refractory=2, threshold=0
    ):
        """
        Rasterize a membrane potential (or filtered or any quantity processed from membrane voltage), with spike detection.
        This function adds 4 items to the dictionnary, with the key termination '_raster_position', '_raster_x_position', '_raster_time_index', '_raster_time' concatenated to the original key.
        These keys correspond to:
        _raster_position    : spike position as the indice of the original key
        _raster_x_position  : spike position as geometrical position in um
        _raster_time_index  : spike time as the indice of the original key
        _raster_time        : spike time as ms

        Parameters
        ----------
        key     : str
            name of the key to rasterize
        t_start         : float
            time at which the spike detection should start, in ms. By default 0
        t_stop          : float
            maximum time to apply spike detection, in ms. If zero is specified, the spike detection is applied to the full signal duration. By default set to 0.
        t_min_spike     : float
            minimum duration of a spike over its threshold, in ms. By default set to 0.1 ms
        t_refractory    : float
            refractory period for a spike, in ms. By default set to 2 ms.
        threshold       : float
            threshold for spike dection, in mV. If 0 is specified the threshold associated with the axon is automatically chosen. By default set to 0.
            Note that if a 0 value is wanted as threshold, a insignificat value (eg. 1e-12) should be specified.
        """
        if t_stop == 0:
            t_stop = int(self["t_sim"] / self["dt"])
        else:
            t_stop = int(t_stop / self["dt"])
        if threshold == 0:
            thr = self["threshold"]
        else:
            thr = threshold
        ## selecting the list of position considering what has been recorded
        if self["myelinated"] == True:
            if self["rec"] == "all":
                list_to_parse = self["node_index"]
                x = self["x"]
            else:
                list_to_parse = np.arange(len(self["x_rec"]))  # self[my_key]
                x = self["x_rec"]
        else:
            list_to_parse = np.arange(len(self["x_rec"]))  # self[my_key]
            x = self["x_rec"]
        # spike detection
        (
            self[my_key + "_raster_position"],
            self[my_key + "_raster_x_position"],
            self[my_key + "_raster_time_index"],
            self[my_key + "_raster_time"],
        ) = self.spike_detection(
            my_key,
            self["t"],
            x,
            list_to_parse,
            thr,
            self["dt"],
            t_start,
            t_stop,
            t_refractory,
            t_min_spike,
        )

    #@jit(nopython=True, fastmath=True)
    def spike_detection(
        self, my_key, t, x, list_to_parse, thr, dt, t_start, t_stop, t_refractory, t_min_spike
    ):
        """
        Internal use only, spike detection just in time compiled to speed up the process
        """
        Voltage = self[my_key]
        raster_position = []
        raster_x_position = []
        raster_time_index = []
        raster_time = []
        # parsing to find spikes
        for i in list_to_parse:
            t_last_spike = t_start - t_refractory
            for j in range(int(t_start * (1 / dt)), t_stop):
                if (
                    Voltage[i][j] <= thr
                    and Voltage[i][j + 1] >= thr
                    and Voltage[i][min((j + int(t_min_spike * (1 / dt))), t_stop)] >= thr
                    and (j * dt - t_last_spike) > t_refractory
                ):  # 1st line: threshold crossing, 2nd: minimum time above threshold,3rd: refractory period
                    # there was a spike, get time and position
                    raster_position.append(i)
                    raster_x_position.append(x[i])
                    raster_time_index.append(j)
                    raster_time.append(t[j])
                    # memorize the time in ms, to evaluate refractory period
                    t_last_spike = j * dt
        # return results
        return (
            np.asarray(raster_position),
            np.asarray(raster_x_position),
            np.asarray(raster_time_index),
            np.asarray(raster_time),
        )

    def find_spike_origin(
        self, my_key=None, t_start=0, t_stop=0, x_min=None, x_max=None
    ):
        """
        Find the start time and position of a spike or a spike train. Only work on rasterized keys

        Parameters
        ----------
        key     : str
            name of the key to consider, if None is specified, the rasterized is automatically chose with preference for filtered-rasterized keys.
        t_start : float
            time at which the spikes are processed, in ms. By default 0
        t_stop  : float
            maximum time at which the spikes are processed, in ms. If zero is specified, the spike detection is applied to the full signal duration. By default set to 0.
        x_min   : float
            minimum position for spike processing, in um. If none is specified, the spike are processed starting at the 0 position. By default set to None.
        x_max   : float
            minimum position for spike processing, in um. If None is specified, spikes are processed on the full axon length . By default set to 0.

        Returns
        -------
        start_time          : float
            first occurance time in ms
        start_x_position    : float
            first occurance position in um
        """
        # define max timing if not already defined
        if t_stop == 0:
            t_stop = self["t_sim"]
        # find the best raster plot
        if my_key == None:
            if "V_mem_filtered_raster_position" in self:
                good_key_prefix = "V_mem_filtered_raster"
            elif "V_mem_raster_position" in self:
                good_key_prefix = "V_mem_raster"
            else:
                # there is no rasterized voltage, nothing to find
                return False
        else:
            good_key_prefix = my_key
        # get data only in time windows
        sup_indexes = np.where(self[good_key_prefix + "_time"] > t_start)
        inf_indexes = np.where(self[good_key_prefix + "_time"] < t_stop)
        good_indexes = np.intersect1d(sup_indexes, inf_indexes)
        good_spike_times = self[good_key_prefix + "_time"][good_indexes]
        good_spike_positions = self[good_key_prefix + "_x_position"][good_indexes]
        # get data only in the z window if applicable
        if x_min != None:
            sup_xmin_indexes = np.where(good_spike_positions > x_min)
        else:
            sup_xmin_indexes = np.arange(len(good_spike_positions))
        if x_max != None:
            inf_xmax_indexes = np.where(good_spike_positions < x_max)
        else:
            inf_xmax_indexes = np.arange(len(good_spike_positions))
        good_x_indexes = np.intersect1d(sup_xmin_indexes, inf_xmax_indexes)
        considered_spike_times = good_spike_times[good_x_indexes]
        considered_spike_positions = good_spike_positions[good_x_indexes]
        # fin the minimum time corresponding to spike initiation
        start_index = np.where(considered_spike_times == np.amin(considered_spike_times))
        start_time = considered_spike_times[start_index]
        start_x_position = considered_spike_positions[start_index]
        return start_time, start_x_position


    def find_spike_last_occurance(
        self, my_key=None, t_start=0, t_stop=0, direction="up", x_start=0
    ):
        """
        Find the last position of a spike occurance for rasterized data

        Parameters
        ----------
        key         : str
            name of the key to consider, if None is specified, the rasterized is automatically chose with preference for filtered-rasterized keys.
        t_start     : float
            time at which the spikes are processed, in ms. By default 0
        t_stop      : float
            maximum time at which the spikes are processed, in ms. If zero is specified, the spike detection is applied to the full signal duration. By default set to 0.
        direction   : str
            Direction of the spike propagation, chose between:
                'up'    -> spike propagating to higher x-coordinate values
                'down'  -> spike propagating to lower x-coordinate values
        x_start     : float
            minimum position for spike processing, in um. If None is specified, spikes are processed on the full axon length . By default set to 0.

        Returns
        -------
        t_last      : float
            last occurance time in ms
        x_last  : float
            last occurance position in um
        """
        # define max timing if not already defined
        if t_stop == 0:
            t_stop = self["t_sim"]
        # find the best raster plot
        if my_key == None:
            if "V_mem_filtered_raster_position" in self:
                good_key_prefix = "V_mem_filtered_raster"
            elif "V_mem_raster_position" in self:
                good_key_prefix = "V_mem_raster"
            else:
                # there is no rasterized voltage, nothing to find
                return False
        else:
            good_key_prefix = my_key
        # get x_start, eventually t_start
        if x_start == 0:
            t_start, x_start = self.find_spike_origin(
                my_key=good_key_prefix, t_start=t_start, t_stop=t_stop
            )
        # get data only in time windows
        sup_indexes = np.where(self[good_key_prefix + "_time"] > t_start)
        inf_indexes = np.where(self[good_key_prefix + "_time"] < t_stop)
        good_indexes = np.intersect1d(sup_indexes, inf_indexes)
        considered_spike_times = self[good_key_prefix + "_time"][good_indexes]
        considered_spike_positions = self[good_key_prefix + "_x_position"][good_indexes]
        if direction == "up":
            # find the spike in the upper region of the start
            upper_spike_index = np.where(considered_spike_positions > x_start)
            upper_spike_times = considered_spike_times[upper_spike_index]
            upper_spike_positions = considered_spike_positions[upper_spike_index]
            # find the last occurance
            last_spike_index = np.where(upper_spike_times == np.amax(upper_spike_times))
            t_last = upper_spike_times[last_spike_index]
            x_last = upper_spike_positions[last_spike_index]
        elif direction == "down":
            # find the spike in the upper region of the start
            lower_spike_index = np.where(considered_spike_positions < x_start)
            lower_spike_times = considered_spike_times[lower_spike_index]
            lower_spike_positions = considered_spike_positions[lower_spike_index]
            # find the last occurance
            last_spike_index = np.where(lower_spike_times == np.amax(lower_spike_times))
            t_last = lower_spike_times[last_spike_index]
            x_last = lower_spike_positions[last_spike_index]
        else:
            # find the spike in the upper region of the start
            upper_spike_index = np.where(considered_spike_positions > x_start)
            upper_spike_times = considered_spike_times[upper_spike_index]
            upper_spike_positions = considered_spike_positions[upper_spike_index]
            # find the spike in the upper region of the start
            lower_spike_index = np.where(considered_spike_positions < x_start)
            lower_spike_times = considered_spike_times[lower_spike_index]
            lower_spike_positions = considered_spike_positions[lower_spike_index]
            # find the last occurances
            last_upper_spike_index = np.where(
                upper_spike_times == np.amax(upper_spike_times)
            )
            last_lower_spike_index = np.where(
                lower_spike_times == np.amax(lower_spike_times)
            )
            t_last = np.asarray(
                [
                    lower_spike_times[last_lower_spike_index][0],
                    lower_spike_times[last_upper_spike_index],
                ][0]
            )
            x_last = np.asarray(
                [
                    lower_spike_positions[last_lower_spike_index][0],
                    lower_spike_positions[last_upper_spike_index],
                ][0]
            )
        return t_last, x_last


    def speed(self, position_key=None, t_start=0, t_stop=0, x_start=0, x_stop=0):
        """
        Compute the velocity of a spike from rasterized data in a dictionary. The speed can be either positive or negative depending on the propagation direction.

        Parameters
        ----------
        key         : str
            name of the key to consider, if None is specified, the rasterized is automatically chose with preference for filtered-rasterized keys.
        t_start     : float
            time at which the spikes are processed, in ms. By default 0
        t_stop      : float
            maximum time at which the spikes are processed, in ms. If zero is specified, the spike detection is applied to the full signal duration. By default set to 0.
        x_start     : float
            minimum position for spike processing, in um. By default set to 0.
        x_stop      : float
            maximum position for spike processing, in um. If 0 is specified, spikes are processed on the full axon length . By default set to 0.

        Returns
        -------
        speed   : float
            velocity.

        Note
        ----
        the velocity is computed with first and last occurance of a spike, be careful specifying the computation window if multiple spikes. This function will not see velocity variation.
        """
        # define max timing if not already defined
        if t_stop == 0:
            t_stop = self["t_sim"]
        if t_start == 0:
            if "intra_stim_starts" in self and self["intra_stim_starts"] != []:
                t_start = self["intra_stim_starts"][0]
        if x_start == 0:
            x_stop = self["L"]
        elif x_stop == 0:
            x_start = self["L"]
        # find the best raster plot
        if position_key == None:
            if "V_mem_filtered_raster_position" in self:
                good_key_prefix = "V_mem_filtered_raster"
            elif "V_mem_raster_position" in self:
                good_key_prefix = "V_mem_raster"
            else:
                # there is no rasterized voltage, nothing to find
                return False
        else:
            good_key_prefix = position_key
        # get data only in time windows
        sup_time_indexes = np.where(self[good_key_prefix + "_time"] > t_start)
        inf_time_indexes = np.where(self[good_key_prefix + "_time"] < t_stop)
        good_indexes_time = np.intersect1d(sup_time_indexes, inf_time_indexes)
        sup_position_indexes = np.where(
            self[good_key_prefix + "_x_position"][good_indexes_time] >= x_start
        )
        inf_position_indexes = np.where(
            self[good_key_prefix + "_x_position"][good_indexes_time] <= x_stop
        )
        good_indexes_position = np.intersect1d(sup_position_indexes, inf_position_indexes)
        good_indexes = np.intersect1d(good_indexes_position, good_indexes_time)
        good_spike_times = self[good_key_prefix + "_time"][good_indexes]
        good_spike_positions = self[good_key_prefix + "_x_position"][good_indexes]
        max_time = np.argmax(good_spike_times)
        min_time = np.argmin(good_spike_times)
        speed = (
            (good_spike_positions[max_time] - good_spike_positions[min_time])
            * 10**-3
            / (good_spike_times[max_time] - good_spike_times[min_time])
        )
        return speed


    def block(self, position_key=None, t_start=0, t_stop=0):
        """
        check if an axon is blocked or not. The simulation has to include the test spike. This function will look for the test spike initiation and check the propagation

        Parameters
        ----------
        key 		: str
            name of the key to consider, if None is specified, the rasterized is automatically chose with preference for filtered-rasterized keys.
        t_start		: float
            time at which the test spikes can occur, in ms. By default 0
        t_stop		: float
            maximum time at which the spikes are processed, in ms. If zero is specified, the spike detection is applied to the full signal duration. By default set to 0.

        Returns
        -------
        flag 	: bool or None
            True if the axon is blocked, False if not blocked and None if the test spike does not cross the stimulation near point in the simulation (no possibility to check for the axon state)
        """
        position_max = 0
        blocked_spike_positionlist = []
        if t_stop == 0:
            t_stop = self["t_sim"]
        if t_start == 0:
            if "intra_stim_starts" in self and self["intra_stim_starts"] != []:
                t_start = self["intra_stim_starts"][0]

        if position_key == None:
            if "V_mem_filtered_raster_position" in self:
                good_key_prefix = "V_mem_filtered_raster"
            elif "V_mem_raster_position" in self:
                good_key_prefix = "V_mem_raster"
            else:
                # there is no rasterized voltage, nothing to find
                return False
        sup_time_indexes = np.where(self[good_key_prefix + "_time"] > t_start)
        inf_time_indexes = np.where(self[good_key_prefix + "_time"] < t_stop)
        good_indexes_time = np.intersect1d(sup_time_indexes, inf_time_indexes)
        good_spike_times = self[good_key_prefix + "_time"][good_indexes_time]
        blocked_spike_positionlist = self[good_key_prefix + "_x_position"][
            good_indexes_time
        ]
        if len(blocked_spike_positionlist) == 0:
            return None
        if "intra_stim_positions" in self:
            if self["intra_stim_positions"] < self["extracellular_electrode_x"]:
                position_max = max_spike_position(
                    blocked_spike_positionlist, position_max, spike_begin="down"
                )

                if blocked_spike_positionlist[position_max] < 9.0 / 10 * self["L"]:
                    return True
                else:
                    for i in range(position_max - 1):
                        if (
                            blocked_spike_positionlist[i + 1]
                            - blocked_spike_positionlist[i]
                            > self["L"] / 5
                        ):
                            return True
                    else:
                        return False
            else:
                position_max = max_spike_position(
                    blocked_spike_positionlist, position_max, spike_begin="up"
                )
                if min(blocked_spike_positionlist) > 1.0 / 10 * self["L"]:
                    return True
                else:
                    for i in range(position_max - 1):
                        if (
                            blocked_spike_positionlist[i]
                            - blocked_spike_positionlist[i + 1]
                            > self["L"] / 5
                        ):
                            return True
                    else:
                        return False
        else:
            rise_error("intra_stim_positions is not in dictionnary")



    def check_test_AP(self):
        """
        Check if a test AP is correctely triggered during an axon simulation and if so return the\
        trigger time

        Parameters
        ----------
        self     : dict
            results of axon.simulate method

        Returns
        -------
        test_AP     : float or None
            time in ms of the first test AP during the simulation. None if no test AP found
        """
        if type(self) == str:
            self = self.load_simulation_from_json()
        if "intra_stim_starts" not in self:
            return None
        else:
            mask = False
            test_AP = self["intra_stim_starts"]
            if len(test_AP):
                if np.iterable(test_AP):
                    test_AP = test_AP[0]
                i_first_pos = np.where(self["V_mem_raster_x_position"] == 0)
                for i in i_first_pos[0]:
                    if (
                        self["V_mem_raster_time"][i] >= test_AP - 0.01
                        and self["V_mem_raster_time"][i] <= test_AP + 0.7
                    ):
                        mask = True
                if not mask:
                    test_AP = None
            else:
                test_AP = None
            return test_AP


    def detect_start_extrastim(self, threshold=None):
        """
        Returns the starting time of extracellular stimulation from axon simulation results

        Parameters
        ----------
        self     : dict
            results of axon.simulate method
        threshold       : float
            Current threshold (uA) to consider the stimulation started, if None take the time of second point of the\
            stimulation, by default None

        Returns
        -------
        t_start     : list or float or None
            list of stimulation starting time in ms, float if only one stimulation and None if no stimulation
        """
        t_start = []
        if "extracellular_stimuli" in self:
            for i in range(len(self["extracellular_stimuli"])):
                s = self["extracellular_stimuli"][i]
                t = self["extracellular_stimuli_t"][i]
                if threshold is None:
                    t_start += [t[1]]
                else:
                    for i in reversed(range(len(s))):
                        if abs(s[i]) > threshold:
                            t_start += [t[i]]
        if len(t_start) == 0:
            t_start = None
        elif len(t_start) == 1:
            t_start = t_start[0]
        return t_start


    def extra_stim_properties(self):
        """
        Return elect caracteristics (blocked, Onset response, ...)

        Returns
        -------
        electrode       : dict
            dictonry containing the position (x, y, z), the stimulation start (ms) and maximum value (uA)
            for each electrodes
        """

        electrode = {}

        if "extracellular_electrode_y" in self:
            electrode["x"] = self["extracellular_electrode_x"]
            electrode["y"] = self["extracellular_electrode_y"]
            electrode["z"] = self["extracellular_electrode_z"]
            electrode["start"] = self.detect_start_extrastim(self)
            electrode["max amplitude"] = [
                max(s) for s in self["extracellular_stimuli"]
            ]

        return electrode


    def axon_state(self, save=False, saving_file="axon_state.json"):
        """
        Return axon caracteristics (blocked, Onset response, ...) from axon simulation results

        Parameters
        ----------
        self       : dict or str
            simulation results dictionary or path and name of the saving file
        save        : bool
            if True save result in json file
        saving_file : str
            if save is True path and name of the saving file

        Returns
        -------
        axon_state       : dict
            dictionary containing axon caracteristics
        """
        ID = self["ID"]

        # Axon parameter
        parameters = {}

        if "diameter" in self:
            parameters["diameter"] = self["diameter"]

        if "myelinated" in self and self["myelinated"]:
            parameters["node"] = len(self["x_nodes"])

        if (
            "extracellular_electrode_y" in self
            and len(self["extracellular_electrode_y"]) == 1
        ):
            parameters["distance electrod"] = distance_point2line(
                self["y"],
                self["z"],
                self["extracellular_electrode_y"][0],
                self["extracellular_electrode_z"][0],
            )
            if self["myelinated"]:
                x_elec = self["extracellular_electrode_x"][0]
                elec_node = np.argmin(abs(self["x_nodes"] - x_elec))
                elec_ali = (self["x_nodes"][elec_node] - x_elec) / (
                    self["x_nodes"][1] - self["x_nodes"][0]
                )
                parameters["electrod node"] = int(elec_node)
                parameters["electrod alignment"] = float(elec_ali)

        # Check Block
        test_AP = self.check_test_AP()
        if test_AP is None:
            block_state = None
        else:
            if "extracellular_electrode_x" not in self:
                self["extracellular_electrode_x"] = 0
            block_state = self.block(
                t_start=test_AP - 0.001
            )  # , t_stop=test_AP+1) # Gerer le delay
        # Check Onset Response

        onset_state = False
        t_start_stim = self.detect_start_extrastim()

        pos = self["V_mem_raster_position"]
        if self["myelinated"]:
            M = len(["x_nodes"])
        else:
            M = len(["x_rec"])
        i_first_pos = np.where(pos == 0)
        i_last_pos = np.where(pos == M)

        # Count Onset response
        N_AP = (len(i_first_pos[0]) + len(i_last_pos[0])) / 2
        if test_AP is not None:
            if block_state:
                N_AP -= 0.5
            else:
                N_AP -= 1

        if N_AP > 0:
            onset_state = True

        axon_state = {
            "ID": ID,
            "parameters": parameters,
            "block_state": block_state,
            "onset_state": onset_state,
            "onset number": N_AP,
        }
        if save:
            json_dump(axon_state, saving_file)

        return axon_state

    ##############################
    ## Impedance properties methods ##
    ##############################

    def compute_f_mem(self):
        """
        compute the cutoff frequency of the axon's membrane and add it to the simulation self dictionnary
        NB: The frequency is computed in [kHz]

        Parameters
        ----------
        self_sim     : dict
            self of axon.simulate method

        Returns
        -------
        f_mem              : np.ndarray
            value of the cutoff frequency of the axon's membrane
        """

        if "g_mem" not in self:
            rise_warning("f_mem cannot be computed computed without membrane conductivity")
            return None
        if "f_mem" not in self:
            ax = self.generate_axon()
            self["c_mem"] = ax.get_membrane_capacitance()
            del ax
        N_x, N_t = np.shape(self["g_mem"])
        f_mem = np.zeros((N_x, N_t))
        for i_t in range(N_t):
            f_mem[:, i_t] = self["g_mem"][:, i_t] / (2 * np.pi * self["c_mem"])

        # in [MHz] as g_mem in [S/cm^{2}] and c_mem [uF/cm^{2}]
        # [MHz] to convert to [kHz]
        self["f_mem"] = to_nrv_unit(f_mem, "MHz")
        return self["f_mem"]


    def get_membrane_conductivity(self, x:float=0, t:float=0, unit:str="S/cm**2", mem_th:float=7*nm)->float:
        """
        get the membrane conductivity at a position x and a time t
    

        Parameters
        ----------
        x : float, optional
            x-position in um where to get the conductivity, by default 0
        t : float, optional
            simulation time in ms when to get the conductivity, by default 0
        unit : str, optional
            unit of the returned conductivity see `units`, by default "S/cm**2"
        mem_th : float, optional
            membrane thickness in um, by default 7*nm

        Note
        ----
        depending of the unit parameter this function either return :

            - the surface conductivity in [S]/([m]*[m]): from neuron simulation
            - the conductivity in [S]/[m]:  by multiplying surface conductivity by membrane thickness
        """
        if "g_mem" not in self:
            rise_warning("to get membrane conductivity the ")
            return None

        n_t = len(self["g_mem"][0])
        i_t = int(n_t*t/self["t_sim"])
        i_x = np.argmin(abs(self["x_rec"] - x))
        g = self["g_mem"][i_x, i_t]

        # Surface conductivity in [S]/([m]*[m])
        if "2" in unit:
            return convert(g, "S/cm**2", unit)
        # conductivity in [S]/[m]
        else:
            g *= from_nrv_unit(mem_th, "cm")
            return convert(g, "S/cm", unit)


    def get_membrane_capacitance(self, unit:str="uF/cm**2", mem_th:float=7*nm)->float:
        """
        get the axon membrane capacitance or permitivity

        Parameters
        ----------
        unit : str, optional
            unit of the returned conductivity see `units`, by default "S/cm**2"
        mem_th : float, optional
            membrane thickness in um, by default 7*nm

        Note
        ----
        depending of the unit parameter this function either return :

            - the surface conductivity in [S]/([m]*[m]): from neuron simulation
            - the conductivity in [S]/[m]:  by multiplying surface conductivity by membrane thickness
        """
        c_mem = membrane_capacitance_from_model(self.model)

        # Surface capacity in [F]/([m]*[m])
        if "2" in unit:
            return convert(c_mem, "S/cm**2", unit)
        # permitivity in [F]/[m]
        else:
            c_mem *= from_nrv_unit(mem_th, "cm")
            return convert(c_mem, "S/cm", unit)

    def get_membrane_complexe_admitance(self, f:float=1., x:float=0, t:float=0, unit:str="S/m", mem_th:float=7*nm)->np.array:
        """
        get the membran complexe admitance of each axon at a position x and a time t for a given frequency

        Parameters
        ----------
        f : float or np.array, optional
            effective frequency in kHz, by default 1
        x : float, optional
            x-position in um where to get the conductivity, by default 0
        t : float, optional
            simulation time in ms when to get the conductivity, by default 0
        unit : str, optional
            unit of the returned conductivity see `units`, by default "S/cm**2"
        mem_th : float, optional
            membrane thickness in um, by default 7*nm
        """
        c = self.get_membrane_capacitance(mem_th=mem_th)
        g = self.get_membrane_conductivity(x=x, t=t, mem_th=mem_th)
        f_mem = g/(2*np.pi*c)

        # in [MHz] as g_mem in [S/cm^{2}] and c_mem [uF/cm^{2}]
        # [MHz] to convert to [kHz]
        f_mem = to_nrv_unit(f_mem, "MHz")

        Y = compute_complex_admitance(f=f, g=g, fc=f_mem)

        if "2" in unit:
            return convert(Y, "S/cm**2", unit)
        # permitivity in [F]/[m]
        else:
            Y *= from_nrv_unit(mem_th, "cm")
            return convert(Y, "S/cm", unit)