"""
NRV-Cellular Level postprocessing.
.. warning::

    CL_postprocessing functions are deprecated. Use axon_results and associated methods instead.
"""

import faulthandler
from collections.abc import Iterable

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

from ..backend._log_interface import pass_info, rise_warning, rise_error
from ..utils._units import MHz
from ..utils._misc import distance_point2line
from ..nmod._unmyelinated import unmyelinated
from ..nmod._myelinated import myelinated
from ..nmod.results._axons_results import axon_results


# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()


##############################################
## HANDLE THE SIMULATION RESULT DICTIONNARY ##
##############################################
def remove_key(my_dict, key, verbose=False):
    """
    Remove an item from a dictionary, usefull before saving files, as some results maybe heavy and are potentially useless after some steps of postprocessing.

    Parameters
    ----------
    my_dict : dictionary
        dictionary where an item should be deleted
    key     : str
        name of the key to delete
    """
    
    rise_warning(
        "DeprecationWarning: ",
        "remove_key is obsolete use method from axon_result objects instead"
    )
    # if isinstance(key, Iterable):
    #    for k in key:
    #        del my_dict[k]
    # else:
    del my_dict[key]
    pass_info("removed the following key from results: ", key, verbose=verbose)


def remove_non_NoR_zones(my_dict, key):
    """
    Automatically remove values out of nodes of Ranvier for membrane voltage and associated quantities.
    This function is helpfull for large simulation before saving results

    Parameters
    ----------
    my_dict : dictionary
        dictionary where the quantity should be cleaned
    key     : str
        name of the key to clean
    """

    rise_warning(
            "DeprecationWarning: ",
            "remove_non_NoR_zones is obsolete use method from axon_result objects instead"
        )
    if "V_mem" in key:
        if my_dict["Axon_type"] == "Myelinated":
            new_entry = []
            for i in my_dict["Nodes_of_Ranvier_indexes"]:
                new_entry.append(my_dict[key][i, :])
            my_dict[key] = np.asarray(new_entry)
        else:
            rise_warning(
                "Warning, remove_non_NoR_zones only applicable to Myelinated axons"
            )
    else:
        rise_warning(
            "Warning, remove_non_NoR_zones only applicable to membrane voltage or current"
        )


def generate_axon_from_results(results):
    """
    generate a blank axon with the same dimensions as in the results

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method

    Returns
    -------
    ax              : unmyelinated or myelinated
        blank axon with the same dimensions as in the results
    """

    # rise_warning(
    #     "DeprecationWarning: ",
    #     "generate_axon_from_results property is obsolete use method from axon_result objects instead"
    # )
    if not results["myelinated"]:
        ax = unmyelinated(**results)
    else:
        ax = myelinated(**results)
    return ax


############################
## AXON SIGNAL PROCESSING ##
############################
def filter_freq(my_dict, my_key, freq, Q=10):
    """
    Basic Filtering of quantities. This function design a notch filter (scipy IIR-notch).
    Adds an item to the specified dictionary, with the key termination '_filtered' concatenated to the original key.

    Parameters
    ----------
    my_dict : dictionary
        dictionary where the quantity should be filtered
    key     : str
        name of the key to filter
    freq    : float or array, list, np.array
        frequecy or list of frequencies to filter in kHz, as time is defined in ms in NRV2.
        If multiple frequencies, they are filtered sequencially, with as may filters as frequencies, in the specified order
    Q       : float
        quality factor of the filter, by default set to 10
    """

    rise_warning(
        "DeprecationWarning: ",
        "filter_freq is obsolete use method from axon_result objects instead"
    )
    if isinstance(freq, Iterable):
        f0 = np.asarray(freq)
    else:
        f0 = freq
    if my_dict["dt"] == 0:
        rise_warning(
            "Warning: filtering aborted, variable time step used for differential equation solving"
        )
        return False
    else:
        fs = 1 / my_dict["dt"]
        if isinstance(f0, Iterable):
            new_sig = np.zeros(my_dict[my_key].shape)
            for k in range(len(my_dict[my_key])):
                new_sig[k, :] = my_dict[my_key][k]
                for f in f0:
                    b_notch, a_notch = signal.iirnotch(f, Q, fs)
                    new_sig[k, :] = signal.lfilter(b_notch, a_notch, new_sig[k, :][k])
        else:
            ##  NOTCH at the stimulation frequency
            b_notch, a_notch = signal.iirnotch(f0, Q, fs)
            new_sig = np.zeros(my_dict[my_key].shape)
            for k in range(len(my_dict[my_key])):
                new_sig[k, :] = signal.lfilter(b_notch, a_notch, my_dict[my_key][k])
        my_dict[my_key + "_filtered"] = new_sig


def rasterize(
    my_dict, my_key, t_start=0, t_stop=0, t_min_spike=0.1, t_refractory=2, threshold=0
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
    my_dict : dictionary
        dictionary where the quantity should be rasterized
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

    rise_warning(
        "DeprecationWarning: ",
        "rasterize is obsolete use method from axon_result objects instead"
    )
    if t_stop == 0:
        t_stop = int(my_dict["t_sim"] / my_dict["dt"])
    else:
        t_stop = int(t_stop / my_dict["dt"])
    if threshold == 0:
        thr = my_dict["threshold"]
    else:
        thr = threshold
    ## selecting the list of position considering what has been recorded
    if my_dict["myelinated"] == True:
        if my_dict["rec"] == "all":
            list_to_parse = my_dict["node_index"]
            x = my_dict["x"]
        else:
            list_to_parse = np.arange(len(my_dict["x_rec"]))  # my_dict[my_key]
            x = my_dict["x_rec"]
    else:
        list_to_parse = np.arange(len(my_dict["x_rec"]))  # my_dict[my_key]
        x = my_dict["x_rec"]
    # spike detection
    (
        my_dict[my_key + "_raster_position"],
        my_dict[my_key + "_raster_x_position"],
        my_dict[my_key + "_raster_time_index"],
        my_dict[my_key + "_raster_time"],
    ) = AP_detection(
        my_dict[my_key],
        my_dict["t"],
        x,
        list_to_parse,
        thr,
        my_dict["dt"],
        t_start,
        t_stop,
        t_refractory,
        t_min_spike,
    )


#@jit(nopython=True, fastmath=True)
def AP_detection(
    Voltage, t, x, list_to_parse, thr, dt, t_start, t_stop, t_refractory, t_min_spike
):
    """
    Internal use only, spike detection just in time compiled to speed up the process
    """

    rise_warning(
        "DeprecationWarning: ",
        "AP_detection is obsolete use method from axon_result objects instead"
    )
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



def speed(my_dict, position_key=None, t_start=0, t_stop=0, x_start=0, x_stop=0):
    """
    Compute the velocity of a spike from rasterized data in a dictionary. The speed can be either positive or negative depending on the propagation direction.

    Parameters
    ----------
    my_dict     : dictionary
        dictionary where the quantity should be rasterized
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

    rise_warning(
        "DeprecationWarning: ",
        "speed is obsolete use method from axon_result objects instead"
    )
    # define max timing if not already defined
    if t_stop == 0:
        t_stop = my_dict["t_sim"]
    if t_start == 0:
        if "intra_stim_starts" in my_dict and my_dict["intra_stim_starts"] != []:
            t_start = my_dict["intra_stim_starts"][0]
    if x_start == 0:
        x_stop = my_dict["L"]
    elif x_stop == 0:
        x_start = my_dict["L"]
    # find the best raster plot
    if position_key == None:
        if "V_mem_filtered_raster_position" in my_dict:
            good_key_prefix = "V_mem_filtered_raster"
        elif "V_mem_raster_position" in my_dict:
            good_key_prefix = "V_mem_raster"
        else:
            # there is no rasterized voltage, nothing to find
            return False
    else:
        good_key_prefix = position_key
    # get data only in time windows
    sup_time_indexes = np.where(my_dict[good_key_prefix + "_time"] > t_start)
    inf_time_indexes = np.where(my_dict[good_key_prefix + "_time"] < t_stop)
    good_indexes_time = np.intersect1d(sup_time_indexes, inf_time_indexes)
    sup_position_indexes = np.where(
        my_dict[good_key_prefix + "_x_position"][good_indexes_time] >= x_start
    )
    inf_position_indexes = np.where(
        my_dict[good_key_prefix + "_x_position"][good_indexes_time] <= x_stop
    )
    good_indexes_position = np.intersect1d(sup_position_indexes, inf_position_indexes)
    good_indexes = np.intersect1d(good_indexes_position, good_indexes_time)
    good_spike_times = my_dict[good_key_prefix + "_time"][good_indexes]
    good_spike_positions = my_dict[good_key_prefix + "_x_position"][good_indexes]
    max_time = np.argmax(good_spike_times)
    min_time = np.argmin(good_spike_times)
    speed = (
        (good_spike_positions[max_time] - good_spike_positions[min_time])
        * 10**-3
        / (good_spike_times[max_time] - good_spike_times[min_time])
    )
    return speed


def block(my_dict, position_key=None, t_start=0, t_stop=0):
    """
    check if an axon is blocked or not. The simulation has to include the test spike. This function will look for the test spike initiation and check the propagation

    Parameters
    ----------
    my_dict 	: dictionary
        dictionary where the quantity should be rasterized
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

    rise_warning(
        "DeprecationWarning: ",
        "block is obsolete use method from axon_result objects instead"
    )
    position_max = 0
    blocked_spike_positionlist = []
    if t_stop == 0:
        t_stop = my_dict["t_sim"]
    if t_start == 0:
        if "intra_stim_starts" in my_dict and my_dict["intra_stim_starts"] != []:
            t_start = my_dict["intra_stim_starts"][0]

    if position_key == None:
        if "V_mem_filtered_raster_position" in my_dict:
            good_key_prefix = "V_mem_filtered_raster"
        elif "V_mem_raster_position" in my_dict:
            good_key_prefix = "V_mem_raster"
        else:
            # there is no rasterized voltage, nothing to find
            return False
    sup_time_indexes = np.where(my_dict[good_key_prefix + "_time"] > t_start)
    inf_time_indexes = np.where(my_dict[good_key_prefix + "_time"] < t_stop)
    good_indexes_time = np.intersect1d(sup_time_indexes, inf_time_indexes)
    good_spike_times = my_dict[good_key_prefix + "_time"][good_indexes_time]
    blocked_spike_positionlist = my_dict[good_key_prefix + "_x_position"][
        good_indexes_time
    ]
    if len(blocked_spike_positionlist) == 0:
        return None
    if "intra_stim_positions" in my_dict:
        if my_dict["intra_stim_positions"] < my_dict["extracellular_electrode_x"]:
            position_max = max_spike_position(
                blocked_spike_positionlist, position_max, spike_begin="down"
            )

            if blocked_spike_positionlist[position_max] < 9.0 / 10 * my_dict["L"]:
                return True
            else:
                for i in range(position_max - 1):
                    if (
                        blocked_spike_positionlist[i + 1]
                        - blocked_spike_positionlist[i]
                        > my_dict["L"] / 5
                    ):
                        return True
                else:
                    return False
        else:
            position_max = max_spike_position(
                blocked_spike_positionlist, position_max, spike_begin="up"
            )
            if min(blocked_spike_positionlist) > 1.0 / 10 * my_dict["L"]:
                return True
            else:
                for i in range(position_max - 1):
                    if (
                        blocked_spike_positionlist[i]
                        - blocked_spike_positionlist[i + 1]
                        > my_dict["L"] / 5
                    ):
                        return True
                else:
                    return False
    else:
        pass_info("intra_stim_positions is not in dictionnary")


def max_spike_position(blocked_spike_positionlist, position_max, spike_begin="down"):
    rise_warning(
        "DeprecationWarning: ",
        "max_spike_position is obsolete use method from axon_result objects instead"
    )
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

    rise_warning(
        "DeprecationWarning: ",
        "count_spike is obsolete use method from axon_result objects instead"
    )
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


def check_test_AP(results_sim):
    """
    Check if a test AP is correctely triggered during an axon simulation and if so return the\
    trigger time

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method

    Returns
    -------
    test_AP     : float or None
        time in ms of the first test AP during the simulation. None if no test AP found
    """

    rise_warning(
        "DeprecationWarning: ",
        "check_test_AP is obsolete use method from axon_result objects instead"
    )
    if type(results_sim) == str:
        results_sim = load_simulation_from_json(results_sim)
    if "intra_stim_starts" not in results_sim:
        return None
    else:
        mask = False
        test_AP = results_sim["intra_stim_starts"]
        if len(test_AP):
            if is_iterable(test_AP):
                test_AP = test_AP[0]
            i_first_pos = np.where(results_sim["V_mem_raster_x_position"] == 0)
            for i in i_first_pos[0]:
                if (
                    results_sim["V_mem_raster_time"][i] >= test_AP - 0.01
                    and results_sim["V_mem_raster_time"][i] <= test_AP + 0.7
                ):
                    mask = True
            if not mask:
                test_AP = None
        else:
            test_AP = None
        return test_AP


def detect_start_extrastim(results_sim, threshold=None):
    """
    Returns the starting time of extracellular stimulation from axon simulation results

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method
    threshold       : float
        Current threshold (uA) to consider the stimulation started, if None take the time of second point of the\
        stimulation, by default None

    Returns
    -------
    t_start     : list or float or None
        list of stimulation starting time in ms, float if only one stimulation and None if no stimulation
    """

    rise_warning(
        "DeprecationWarning: ",
        "detect_start_extrastim is obsolete use method from axon_result objects instead"
    )
    if type(results_sim) == str:
        results_sim = load_simulation_from_json(results_sim)

    t_start = []
    if "extracellular_stimuli" in results_sim:
        for i in range(len(results_sim["extracellular_stimuli"])):
            s = results_sim["extracellular_stimuli"][i]
            t = results_sim["extracellular_stimuli_t"][i]
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


def extra_stim_properties(results_sim):
    """
    Return elect caracteristics (blocked, Onset response, ...)

    Parameters
    ----------
    results_sim       : dict or str
        simulation results dictionary or path and name of the file containing it
    Returns
    -------
    electrode       : dict
        dictonry containing the position (x, y, z), the stimulation start (ms) and maximum value (uA)
        for each electrodes
    """

    rise_warning(
        "DeprecationWarning: ",
        "extra_stim_properties is obsolete use method from axon_result objects instead"
    )
    if type(results_sim) == str:
        results_sim = load_simulation_from_json(results_sim)

    electrode = {}

    if "extracellular_electrode_y" in results_sim:
        electrode["x"] = results_sim["extracellular_electrode_x"]
        electrode["y"] = results_sim["extracellular_electrode_y"]
        electrode["z"] = results_sim["extracellular_electrode_z"]
        electrode["start"] = detect_start_extrastim(results_sim)
        electrode["max amplitude"] = [
            max(s) for s in results_sim["extracellular_stimuli"]
        ]

    return electrode


def axon_state(results_sim, save=False, saving_file="axon_state.json"):
    """
    Return axon caracteristics (blocked, Onset response, ...) from axon simulation results

    Parameters
    ----------
    results_sim       : dict or str
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

    rise_warning(
        "DeprecationWarning: ",
        "axon_state is obsolete use method from axon_result objects instead"
    )
    if type(results_sim) == str:
        results_sim = load_simulation_from_json(results_sim)

    ID = results_sim["ID"]

    # Axon parameter
    parameters = {}

    if "diameter" in results_sim:
        parameters["diameter"] = results_sim["diameter"]

    if "myelinated" in results_sim and results_sim["myelinated"]:
        parameters["node"] = len(results_sim["x_nodes"])

    if (
        "extracellular_electrode_y" in results_sim
        and len(results_sim["extracellular_electrode_y"]) == 1
    ):
        parameters["distance electrod"] = distance_point2line(
            results_sim["y"],
            results_sim["z"],
            results_sim["extracellular_electrode_y"][0],
            results_sim["extracellular_electrode_z"][0],
        )
        if results_sim["myelinated"]:
            x_elec = results_sim["extracellular_electrode_x"][0]
            elec_node = np.argmin(abs(results_sim["x_nodes"] - x_elec))
            elec_ali = (results_sim["x_nodes"][elec_node] - x_elec) / (
                results_sim["x_nodes"][1] - results_sim["x_nodes"][0]
            )
            parameters["electrod node"] = int(elec_node)
            parameters["electrod alignment"] = float(elec_ali)

    # Check Block
    test_AP = check_test_AP(results_sim)
    if test_AP is None:
        block_state = None
    else:
        if "extracellular_electrode_x" not in results_sim:
            results_sim["extracellular_electrode_x"] = 0
        block_state = block(
            results_sim, t_start=test_AP - 0.001
        )  # , t_stop=test_AP+1) # Gerer le delay
    # Check Onset Response

    onset_state = False
    t_start_stim = detect_start_extrastim(results_sim)

    pos = results_sim["V_mem_raster_position"]
    if results_sim["myelinated"]:
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
        save_axon_results_as_json(axon_state, saving_file)

    return axon_state


##############################
## Axon properties function ##
##############################
def get_index_myelinated_sequence(results, n):
    """
    Returns the sequence

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method

    Returns
    -------
    n_center              : int
        value of the cutoff frequency of the axon's membrane
    """

    rise_warning(
        "DeprecationWarning: ",
        "get_index_myelinated_sequence is obsolete use method from axon_result objects instead"
    )
    if not results["myelinated"] or results["rec"] == "node":
        return "node"
    else:
        if n > len(results["x_rec"]):
            rise_warning("index not in axon")
        # +1 required because nbr of computation point = nbr seg/sec + 1
        # see if it's a bug
        Nseg_per_sec = results["Nseg_per_sec"] + 1
        N_sec_type = 11
        seq_types = results["axon_path_type"]
        if n == 0:
            return seq_types[0]
        else:
            return seq_types[((n - 1) // Nseg_per_sec) % N_sec_type]


def find_central_node_index(results:axon_results)->int:
    """
    Returns the index of the closer node from the center from a dictionnary results

    Parameters
    ----------
    axon_results     : dict
        results of axon.simulate method

    Returns
    -------
    n_center              : int
        value of the cutoff frequency of the axon's membrane
    """

    rise_warning(
        "DeprecationWarning: ",
        "find_central_node_index is obsolete use method from axon_result objects instead"
    )
    return results.find_central_index()


def compute_f_mem(results):
    """
    compute the cutoff frequency of the axon's membrane and add it to the simulation results dictionnary
    NB: The frequency is computed in [kHz]

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method

    Returns
    -------
    f_mem              : np.ndarray
        value of the cutoff frequency of the axon's membrane
    """

    rise_warning(
        "DeprecationWarning: ",
        "compute_f_mem is obsolete use method from axon_result objects instead"
    )
    if "g_mem" not in results:
        rise_warning("f_mem cannot be computed computed without membrane conductivity")
        return None
    if "f_mem" not in results:
        ax = generate_axon_from_results(results)
        results["c_mem"] = ax.get_membrane_capacitance()
        del ax
    N_x, N_t = np.shape(results["g_mem"])
    f_mem = np.zeros((N_x, N_t))
    for i_t in range(N_t):
        f_mem[:, i_t] = results["g_mem"][:, i_t] / (2 * np.pi * results["c_mem"])

    # in [MHz] as g_mem in [S/cm^{2}] and c_mem [uF/cm^{2}]
    # * [MHz] to convert to [kHz]
    results["f_mem"] = f_mem * MHz
    return results["f_mem"]


def get_myelin_properties(results):
    """
    compute the cutoff frequency of the axon's membrane and add it to the simulation results dictionnary
    NB: The frequency is computed in [kHz]

    Parameters
    ----------
    results_sim     : dict
        results of axon.simulate method

    Returns
    -------
    f_mem              : np.ndarray
        value of the cutoff frequency of the axon's membrane
    """

    rise_warning(
        "DeprecationWarning: ",
        "get_myelin_properties is obsolete use method from axon_result objects instead"
    )
    if not results["myelinated"] or results["rec"] == "node":
        rise_warning("No myelin in the axon simulated, None returned")
        return None

    ax = generate_axon_from_results(results)
    results["g_mye"] = ax.get_myelin_conductance()
    results["c_mye"] = ax.get_myelin_capacitance()
    results["f_mye"] = results["g_mye"] / (2 * np.pi * results["c_mye"])

    # in [MHz] as g_mem in [S/cm^{2}] and c_mem [uF/cm^{2}]
    # * [MHz] to convert to [kHz]
    results["f_mem"] *= MHz
    return results["f_mem"]


#############################
## VISUALIZATION FUNCTIONS ##
#############################
def plot_Nav_states(ax, values, title=""):
    """
    Plot the state machine for kinetic (Markov) Nav 1.1 to 1.9 values

    Parameters
    ----------
    ax : matplotlib axis object
        axes of the figure to work on
    values : list, array, numpy array
        
    title : str, optional
        Title of the plot, by default ""
    """


    rise_warning(
        "DeprecationWarning: ",
        "plot_Nav_states is obsolete use method from axon_result objects instead"
    )
    states = [r"$I_1$", r"$I_2$", r"$C_1$", r"$C_2$", r"$O_1$", r"$O_2$"]

    X = [-1, -3, 0, 1, 0, 3]
    Y = [0, 0, 1, 0, -1, 0]
    c = ["r", "r", "b", "b", "g", "g"]

    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-1.5, 1.5)
    for i in range(len(states)):
        ax.scatter(X[i], Y[i], s=300 + values[i] * 1450, c=c[i], alpha=0.4)
        ax.text(X[i], Y[i], states[i], ha="center", va="center")
    # paths
    ax.arrow(
        -2.5, 0.03, 1, 0, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(-2, 0.2, "$I_2I_1$", ha="center", va="center", alpha=0.4)
    ax.arrow(
        -1.5, -0.03, -1, 0, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(-2, -0.2, "$I_1I_2$", ha="center", va="center", alpha=0.4)

    ax.arrow(
        -0.83, 0.25, 0.5, 0.5, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(-0.9, 0.6, "$I_1C_1$", ha="center", va="center", alpha=0.4)
    ax.arrow(
        -0.22,
        0.75,
        -0.5,
        -0.5,
        linewidth=1,
        alpha=0.5,
        head_width=0.02,
        head_length=0.02,
    )
    ax.text(-0.45, 0.25, "$C_1I_1$", ha="center", va="center", alpha=0.4)

    ax.arrow(
        0.72, 0.25, -0.5, 0.5, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(0.9, 0.6, "$C_1C_2$", ha="center", va="center", alpha=0.4)
    ax.arrow(
        0.33, 0.75, 0.5, -0.5, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(0.45, 0.25, "$C_2C_1$", ha="center", va="center", alpha=0.4)

    ax.arrow(
        0.83,
        -0.25,
        -0.5,
        -0.5,
        linewidth=1,
        alpha=0.5,
        head_width=0.02,
        head_length=0.02,
    )
    ax.text(0.9, -0.6, "$C_2O_1$", ha="center", va="center", alpha=0.4)
    ax.arrow(
        0.22, -0.75, 0.5, 0.5, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(0.45, -0.25, "$O_1C_2$", ha="center", va="center", alpha=0.4)

    ax.arrow(
        -0.33,
        -0.75,
        -0.5,
        0.5,
        linewidth=1,
        alpha=0.5,
        head_width=0.02,
        head_length=0.02,
    )
    ax.text(-0.9, -0.6, "$O_1I_1$", ha="center", va="center", alpha=0.4)

    ax.arrow(1.5, 0.03, 1, 0, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02)
    ax.text(2, 0.2, "$C_20_2$", ha="center", va="center", alpha=0.4)
    ax.arrow(
        2.5, -0.03, -1, 0, linewidth=1, alpha=0.5, head_width=0.02, head_length=0.02
    )
    ax.text(2, -0.2, "$O_2C_2$", ha="center", va="center", alpha=0.4)
    # make axes to disappear
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title)
    ax.axis("off")


################################
## usefull methods on results ##
################################

def default_PP (results:axon_results)->axon_results:
    """
    Default postprocessing function. Rasterize data and remove v_mem to alliviate RAM usage

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.

    Returns
    -------
    axon_results
        updated results of the axon simulation.
    """
    results.rasterize()
    results.remove_key("V_mem")
    return(results)

def rmv_keys(results:axon_results, keys_to_remove:str|set[str]={}, keys_to_keep:set[str]={})->axon_results:
    """
    remove most of the results key to save computing memory.

    Note
    ----
    Only the following keys kept by the fuction
     - `ID`
     - `L`
     - `V_mem_raster_position`
     - `V_mem_raster_x_position`
     - `V_mem_raster_time_index`
     - `V_mem_raster_time`
     - `myelinated`
     - `intra_stim_starts`
     - `intra_stim_positions`


    Warning
    -------
    This function removes a large amount of data from the `results` object. Some methods included in the results may not be used afterwards

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    keys_to_remove : str | list[str], optional
        key or set of key that should be removed, by default []
    keys_to_keep : str | list[str], optional
        If None only keys_to_remove are removed. Otherwise, all key exept those in this list are deleted, by default None.

    Returns
    -------
    axon_results
        updated results.
    """

    results.rasterize("V_mem")
    default_list_keys = {
    "ID",
    "L",
    "V_mem_raster_position",
    "V_mem_raster_x_position",
    "V_mem_raster_time_index",
    "V_mem_raster_time",
    "myelinated",
    "intra_stim_starts",
    "intra_stim_positions",
    "recorder"
    }

    default_list_keys.update(set(keys_to_keep))
    default_list_keys -= set(keys_to_remove)
    results.remove_key(keys_to_keep=default_list_keys)
    return results


def is_recruited(results:axon_results)->axon_results:
    """
    Evaluate if each fibre is recruited by a stimulation (see `axon_results.is_recruited`) and remove most of the `axon_results` keys to alliviate RAM usage.

    Note
    ----
    Only the following keys kept by the fuction
     - `ID`
     - `L`
     - `V_mem_raster_position`
     - `V_mem_raster_x_position`
     - `V_mem_raster_time_index`
     - `V_mem_raster_time`
     - `myelinated`
     - `y`
     - `z`
     - `diameter`
     - `intra_stim_starts`
     - `tstop`
     - `intra_stim_positions`
     - `extracellular_electrode_x`
     - `recruited`

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.

    Returns
    -------
    axon_results
        updated results.
    """
    results.is_recruited(vm_key="V_mem")

    # remove non nevessary data
    list_keys = {
    "ID",
    "L",
    "V_mem_raster_position",
    "V_mem_raster_x_position",
    "V_mem_raster_time_index",
    "V_mem_raster_time",
    "myelinated",
    "y",
    "z",
    "diameter",
    "intra_stim_starts",
    "tstop",
    "intra_stim_positions",
    "extracellular_electrode_x",
    "recruited",
    }
    results.remove_key(keys_to_keep=list_keys)
    return results

def is_blocked(results:axon_results, AP_start:float|None=None, freq:float|None=None, t_refractory:float=1)->axon_results:
    """
    Evaluate the impact od a blocking stimulation on axon (see `axon_results.block_summary`) and remove most of the `axon_results` keys to alliviate RAM usage.

    Note
    ----
    Only the following keys kept by the fuction
     - `ID`
     - `L`
     - `V_mem_raster_position`
     - `V_mem_raster_x_position`
     - `V_mem_raster_time_index`
     - `V_mem_raster_time`
     - `myelinated`
     - `y`
     - `z`
     - `diameter`
     - `intra_stim_starts`
     - `tstop`
     - `intra_stim_positions`
     - `extracellular_electrode_x`
     - `blocked`
     - `has_onset`
     - `n_onset`

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    save : bool, optional
        if true, the block status is saved as a line in a `.csv` file, by default False
    fdir : str, optional
        Path where the conductivity should be saved, the saving file will be `fdir+block_summary.csv`, by default ""

    Note
    ----
    If `save` is true, the data arranged as column of a same line in the following order:
     - `ID`
     - `y`
     - `z`
     - `diameter`
     - `myelinated`
     - `is_blocked`
     - `has_onset`
     - `n_onset`

    Returns
    -------
    axon_results
        updated results.
    """
    ## TO CHANGE WHEN is block is developped
    #results.axon_state(save=False)

    if AP_start is None :
        if "intra_stim_starts" in results and results["intra_stim_starts"] != []:
            AP_start = results["intra_stim_starts"][0]

    vm_key = "V_mem"
    if freq is not None:
        vm_key += "_filtered"

    results.block_summary(AP_start=AP_start, freq=freq, t_refractory=t_refractory)

    # remove non nevessary data
    list_keys = {
    "ID",
    "L",
    f"{vm_key}_raster_position",
    f"{vm_key}_raster_x_position",
    f"{vm_key}_raster_time_index",
    f"{vm_key}_raster_time",
    "myelinated",
    "y",
    "z",
    "diameter",
    "intra_stim_starts",
    "tstop",
    "intra_stim_positions",
    "extracellular_electrode_x",
    "is_blocked",
    "has_onset",
    "n_onset",
    }
    results.remove_key(keys_to_keep=list_keys)
    return results



def sample_keys(results:axon_results, keys_to_sample:str|set[str]={}, t_start_rec:float=0, t_stop_rec:float=-1, sample_dt:None|float=None, i_sampled_t:None|np.ndarray=None, x_bounds:None|float|tuple[float]=None, keys_to_remove:str|set[str]={}, keys_to_keep:set[str]={})->axon_results:
    """
    Undersample the membrane coductivity (``results["g_mem"]``) key and remove most of the `axon_results` keys to alliviate RAM usage.

    Note
    ----
    Only the following keys kept by the fuction
     - `g_mem`
     - `x_rec`
     - `rec`
     - `Nseg_per_sec`
     - `axon_path_type`
     - `t_sim`

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    t_start_rec : float, optional
        Lower time at whitch `g_mem` should be stored, by default 0
    t_stop_rec : float, optional
        Upper time at whitch `g_mem` should be stored, by default -1
    sample_dt : None | float, optional
        Time sample rate at which `g_mem` should be stored if None simulation dt is kept, by default None
    x_bounds : None | tuple[float], optional
        x-positions where to store `g_mem`, possible option:
         - float: The values of `g_mem` are only stored at the nearest position in `x_rec`.
         - tupple: `g_mem` values are stored for all positions included between the two boundaries.
         - None (default): `g_mem` values are stored for all positions.

    Warning
    -------
    ``sample_dt`` should be at multiple of the simulation ``dt`` to allow a correct undersampling. 
    If the not ``sample_dt`` choosen will be the closer multiple of ``dt``.

    Returns
    -------
    axon_results
        updated results.
    """
    if isinstance(keys_to_sample, str):
        keys_to_sample = {keys_to_sample}
    if len(set(keys_to_sample) - set(results.keys())):
        rise_error(set(keys_to_sample) - set(results.keys()), "keys are missing to apply postprocessing. Please check simulation parameters")
    else:
        # x - sampling array
        if x_bounds is None:
            I_x = np.arange(len(results["x_rec"]))
            x_bounds = (0, results["x_rec"][-1])
        elif np.iterable(x_bounds):
            I_x = np.argwhere((results["x_rec"]>x_bounds[0])&(results["x_rec"]<x_bounds[1]))[:,0]
        else:
            x_bounds = [x_bounds]
            I_x = np.array([np.argmin(abs(results["x_rec"]-x_bounds[0]))])
        N_x = len(I_x)

        # t - sampling array
        if i_sampled_t is not None:
            t_APs = i_sampled_t
        else:
            if t_stop_rec < 0:
                i_t_max = len(results["t"])
            else:
                i_t_max = np.argwhere(results["t"]<=t_stop_rec)[-1][0]
            if sample_dt is None:
                sample_dt=results.dt
            i_t_min = np.argwhere(results["t"]>=t_start_rec)[0][0]
             
            t_APs = [k for k in range(i_t_min,i_t_max)]
            t_APs = t_APs[::int(sample_dt/results.dt)]

        # Under sampling to reduce memory consumption
        results["x_rec"] = results["x_rec"][I_x] - x_bounds[0]
        if "t" in results:
            results["t"] = results["t"][t_APs]
        for key in keys_to_sample:
            results[key] = results[key][np.ix_(I_x, t_APs)]
        ###############################
        ## remove non nevessary data ##
        ###############################
        list_keys =  {
        "ID",
        "model",
        "x_rec",
        "rec",
        "Nseg_per_sec",
        "axon_path_type",
        "t_sim",
        "myelinated",
        "intra_stim_starts",
        "intra_stim_positions",
        "recorder"
        }

        list_keys.update(keys_to_keep)
        list_keys.update(keys_to_sample)
        if results.ID==0:
            list_keys.update({"t"})
        results.remove_key(keys_to_keep=list_keys, keys_to_remove=keys_to_remove)
    return results

def sample_g_mem(results:axon_results, t_start_rec:float=0, t_stop_rec:float=-1, sample_dt:None|float=None, x_bounds:None|float|tuple[float]=None)->axon_results:
    """
    Undersample the membrane coductivity (``results["g_mem"]``) key and remove most of the `axon_results` keys to alliviate RAM usage.

    Note
    ----
    Only the following keys kept by the fuction
     - `g_mem`
     - `x_rec`
     - `rec`
     - `Nseg_per_sec`
     - `axon_path_type`
     - `t_sim`

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    t_start_rec : float, optional
        Lower time at whitch `g_mem` should be stored, by default 0
    t_stop_rec : float, optional
        Upper time at whitch `g_mem` should be stored, by default -1
    sample_dt : None | float, optional
        Time sample rate at which `g_mem` should be stored if None simulation dt is kept, by default None
    x_bounds : None | tuple[float], optional
        x-positions where to store `g_mem`, possible option:
         - float: The values of `g_mem` are only stored at the nearest position in `x_rec`.
         - tupple: `g_mem` values are stored for all positions included between the two boundaries.
         - None (default): `g_mem` values are stored for all positions.

    Warning
    -------
    ``sample_dt`` should be at multiple of the simulation ``dt`` to allow a correct undersampling. 
    If the not ``sample_dt`` choosen will be the closer multiple of ``dt``.

    Returns
    -------
    axon_results
        updated results.
    """
    if not results["record_g_mem"]:
        rise_error("gmem not recorded nothing will be done")
    else:
        if t_stop_rec < 0:
            t_stop_rec=results.t_sim

        if sample_dt is None:
            sample_dt=results.dt

        if x_bounds is None:
            x_bounds=(0,results.L)

        if np.iterable(x_bounds):
            I_x = np.argwhere((results["x_rec"]>x_bounds[0])&(results["x_rec"]<x_bounds[1]))[:,0]
        else:
            x_bounds = [x_bounds]
            I_x = np.array([np.argmin(abs(results["x_rec"]-x_bounds[0]))])

        N_x = len(I_x)
        i_t_min = np.argwhere(results["t"]>t_start_rec)[0][0]
        i_t_max = np.argwhere(results["t"]<t_stop_rec)[-1][0]

        t_APs = [k for k in range(i_t_min,i_t_max)]
        t_APs = t_APs[::int(sample_dt/results.dt)]
        N_t = len(t_APs)


        # Under sampling to reduce memory consumption
        results["x_rec"] = results["x_rec"][I_x] - x_bounds[0]
        results["t"] = results["t"][t_APs]
        results["g_mem"] = results["g_mem"][np.ix_(I_x, t_APs)]

        ###############################
        ## remove non nevessary data ##
        ###############################
        list_keys = {
        "g_mem",
        "x_rec",
        "rec",
        "Nseg_per_sec",
        "axon_path_type",
        "t_sim",
        }
        if results.ID==0:
            list_keys.update({"t"})
        results.remove_key(keys_to_keep=list_keys)
    return results

def vmem_plot(results:axon_results, freq:float=None, save:bool=False, fdir:str=""):
    """
    Plot and save the membrane potential along each axon of the fascicle

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    freq : float, optional
            Filter vmem at the specified frequency, by default None
    save : bool, optional
        if true, the block status is saved as a line in a `.csv` file, by default False
    fdir : str, optional
        Path where the conductivity should be saved, the saving file will be `fdir+"block_summary.csv"`, by default ""

    Returns
    -------
    axon_results
        updated results.
    """
    vm_key = "V_mem"
    if (freq is not None):
        results.filter_freq("V_mem",freq , Q= 2)
        vm_key += "_filtered"
    
    fig, ax = plt.subplots()
    results.plot_x_t(ax, key=vm_key)
    if results.myelinated:
        title = f"Myelinated Axon: {np.round(results.diameter,2)} µm in diameter"
    else:       #colormap for unmyelinated fibers as plot_x_t are unreadable
        title = f"Unmyelinated Axon: {np.round(results.diameter,2)} µm in diameter"
    
    #print(fdir)
    ax.set_title(title)
    if save:
        fig.tight_layout()
        fig_name = fdir + "/Activity_axon_" + str(results.ID) + ".png"
        fig.savefig(fig_name)
        plt.close(fig)
    return results

def raster_plot(results:axon_results, freq:float=None, save:bool=False, fdir:str=""):
    """
    Plot and save the raster plot along each axon of the fascicle.

    Parameters
    ----------
    results : axon_results
        results of the axon simulation.
    freq : float, optional
            Filter vmem at the specified frequency, by default None
    save : bool, optional
        if true, the block status is saved as a line in a `.csv` file, by default False
    fdir : str, optional
        Path where the conductivity should be saved, the saving file will be `fdir+block_summary.csv`, by default ""

    Returns
    -------
    axon_results
        updated results.
    """

    vm_key = "V_mem"
    if (freq is not None):
        results.filter_freq("V_mem",freq , Q= 2)
        vm_key += "_filtered"
    fig, ax = plt.subplots()

    results.raster_plot(ax, key=vm_key)
    if results.myelinated:
        title = f"Myelinated Axon: {np.round(results.diameter,2)} µm in diameter"
    else:
        title = f"Unyelinated Axon: {np.round(results.diameter,2)} µm in diameter"

    #print(fdir)
    ax.set_title(title)
    if save:
        fig.tight_layout()
        fig_name = fdir + "/Rasterplot_axon_" + str(results.ID) + ".png"
        fig.savefig(fig_name)
        plt.close(fig)
    return results