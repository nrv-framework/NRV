"""
NRV-:class:`.axon_results` handling.
"""

import numpy as np
from numpy.typing import NDArray
from itertools import combinations
import matplotlib.pyplot as plt
from copy import deepcopy
from scipy.signal import find_peaks

from ...fmod.FEM.fenics_utils._f_materials import f_material, mat_from_interp
from ...backend._NRV_Results import sim_results, abstractmethod
from ...backend._file_handler import json_dump
from ...backend._log_interface import rise_warning, rise_error
from ...utils._units import to_nrv_unit, from_nrv_unit, convert, nm
from ...utils._misc import (
    distance_point2line,
    membrane_capacitance_from_model,
    compute_complex_admitance,
    nearest_greater_idx,
)


def max_spike_position(blocked_spike_positionlist, position_max, spike_begin="down"):
    rise_warning("DeprecationWarning: ", "max_spike_position is obsolete")
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


def AP_detection(
    Voltage, t, x, list_to_parse, thr, dt, t_start, t_stop, t_refractory, t_min_spike
):
    """
    Internal use only, detects an AP
    """

    rise_warning("DeprecationWarning: ", "AP_detection is obsolete")
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


# @jit(nopython=True, fastmath=True)
def count_spike(onset_position):
    """
    spike counting, just in time compiled. For internal use only.
    """

    rise_warning("DeprecationWarning: ", "AP_detection is obsolete")
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


def rasterize(
    y_data: np.array,
    x_data: np.array,
    t_data: np.array,
    threshold: np.float64,
    t_min_AP=0.1,
    t_refractory=0.5,
    t_start: np.float64 = None,
    t_stop: np.float64 = None,
) -> np.array:
    """
    Rasterize a membrane potential (or filtered or any quantity processed from membrane voltage), with AP detection.

    Parameters
    ----------
    y_data : np.array
        Data to rasterize (membrane potential, or anything else)
    x_data : np.array
        x coordinates of y_data
    t_data : np.array
        t coordinates of y_data
    threshold : np.float64
        threshold for AP detection
    t_min_AP : float, optional
        Mininum AP duration, in ms, by default 0.1ms
    t_refractory : int, optional
        inter-AP duration, in ms. Default is 2ms, by default 2
    t_start : np.float64, optional
        start time for rasterize, in ms. Default is 0ms, by default None
    t_stop : np.float64, optional
        stop time for rasterize, in ms. Default is simulation time., by default None
    """

    if t_start is not None:
        t_start_idx = np.where(t_data >= t_start)[0][0]
    else:
        t_start_idx = 0

    if t_stop is not None:
        t_stop_idx = np.where(t_data <= t_stop)[0][0]
    else:
        t_stop_idx = -1

    t_idx_AP = np.array([], np.int32)
    x_idx_AP = np.array([], np.int32)

    dt = t_data[1] - t_data[0]
    dis = int(t_refractory / dt)
    width = int(t_min_AP / dt)
    # width = None
    height = [-20, 70]  # min/max heigh of AP

    for x_val, v in enumerate(y_data):
        data = v[t_start_idx:t_stop_idx]
        peak_idxs, _ = find_peaks(data, height=height, distance=dis, width=width)
        t_idx_AP = np.concatenate([t_idx_AP, peak_idxs])
        x_idx_AP = np.concatenate([x_idx_AP, np.ones(np.size(peak_idxs)) * x_val])

    t_idx_AP = np.int32(t_idx_AP)
    x_idx_AP = np.int32(x_idx_AP)

    if len(t_data):
        return (x_idx_AP, x_data[x_idx_AP], t_idx_AP, t_data[t_idx_AP])
    else:
        return (np.array([]), np.array([]), np.array([]), np.array([]))


def get_first_AP(
    x_APs: np.array,
    x_idx_APs: np.array,
    t_APs: np.array,
    t_idx_APs: np.array,
    t_refract: np.float64 = 0.5,
) -> NDArray | NDArray | NDArray:
    """
    Extract time and position of the first rasterized AP

    Parameters
    ----------
    x_APs : np.array
        x position of the rasterized APs
    x_idx_APs : np.array
        x position index of the rasterized APs
    t_APs : np.array
        t position of the rasterized APs
    t_idx_APs : np.array
        t position index of the rasterized APs
    t_refract: np.float64
        fiber refractory time, in ms, default is .5ms

    Returns
    -------
    np.array
        x positions of the first AP
    np.array
        x positions index of the first AP
    np.array
        t positions of the first AP
    np.array
        t positions index of the first AP
    np.array
        index position of the AP
    """

    if len(t_APs) == 1:
        return (np.array(x_APs), [0], np.array(t_APs), [0], [0])

    if len(t_APs) < 1:
        return (np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

    ordered_t_idx = np.argsort(t_APs)  # sort time indexes

    x_ordered = x_APs[ordered_t_idx]  # sort x positions accordingly
    t_ordered = t_APs[ordered_t_idx]  # sort t positions accordingly
    x_idx_ordered = x_idx_APs[ordered_t_idx]  # sort x positions idx accordingly
    t_idx_ordered = t_idx_APs[ordered_t_idx]  # sort t positions idx accordingly

    x_0 = x_ordered[0]  # get x-position of the first AP in time
    idx_unique = np.sort(np.unique(x_ordered, return_index=True, axis=0)[1])
    t_min = t_refract
    x_ordered_unique = x_ordered[idx_unique]
    x_ordered_unique.sort()
    if len(x_ordered_unique) < 2:
        return (np.array([]), np.array([]), np.array([]), np.array([]), np.array([]))

    x_min = np.min(np.abs(np.diff(x_ordered_unique))) * 5

    msk_unique = np.arange(len(t_ordered) - 1)
    msk_unique = [i for i in msk_unique if i not in idx_unique]

    # get upward APs
    idx_up = []
    idx_up.append(0)  # add the first one
    mask = np.full(x_ordered.shape, False)
    mask[msk_unique] = True
    mask[np.where(x_ordered < x_0)[0]] = True  # mask downward APs

    mask[0] = True  # mask first AP
    x_ordered_cpy = x_ordered.copy()  # copy data
    x_ordered_cpy[mask] = np.nan  # add nan where mask is true
    keep_going = True

    while keep_going:
        if (np.isnan(x_ordered_cpy).sum()) == len(
            x_ordered_cpy
        ):  # check if array is full of nan
            keep_going = False
        else:
            idx = np.nanargmin((x_ordered_cpy - x_0))  # get closest value
            x_ordered_cpy[idx] = np.nan  # mask it

            if (
                t_ordered[idx] - t_ordered[idx_up[-1]] >= 0
            ):  # if time val is greater than previous then we reached of end of the AP
                if (
                    t_ordered[idx] - t_ordered[idx_up[-1]] < t_min
                ):  # if time than the AP refractory period then it doesn't belong to the AP
                    if (
                        np.abs(x_ordered[idx] - x_ordered[idx_up[-1]]) < x_min
                    ):  # if it "jumps" to far then it doesn't belong to the AP
                        idx_up.append(idx)

    # get downward APs
    mask = np.full(x_ordered.shape, False)
    idx_neg = np.where(x_ordered > x_0)[0]
    mask[idx_neg] = True
    mask[0] = True
    mask[msk_unique] = True
    x_ordered_cpy = x_ordered.copy()
    x_ordered_cpy[mask] = np.nan
    idx_down = []
    idx_down.append(0)
    keep_going = True
    while keep_going:
        if (np.isnan(x_ordered_cpy).sum()) == len(x_ordered_cpy):
            keep_going = False
        else:
            idx = np.nanargmin(-(x_ordered_cpy - x_0))
            x_ordered_cpy[idx] = np.nan
            if (t_ordered[idx] - t_ordered[idx_down[-1]]) >= 0:
                if (t_ordered[idx] - t_ordered[idx_down[-1]]) <= t_min:
                    if np.abs(x_ordered[idx] - x_ordered[idx_down[-1]]) < x_min:
                        idx_down.append(idx)

    idx_APs = idx_up + idx_down
    AP_indexes = np.int32(idx_APs)
    AP_indexes = np.unique(idx_APs)

    return (
        x_ordered[AP_indexes],
        x_idx_ordered[AP_indexes],
        t_ordered[AP_indexes],
        t_idx_ordered[AP_indexes],
        ordered_t_idx[AP_indexes],
    )


class axon_results(sim_results):
    """"""

    def __init__(self, context=None):
        super().__init__(context)

    def generate_axon(self):
        """
        generate from the results new version of the simulated axon. Axon generated has the same parameters but is not simulated yet.

        Note
        ----
        This function is not defined in ``axon_results`` but in ``unmyelinated_results`` and ``myelinated_results``.
        """
        pass

    def is_recruited(self, vm_key: str = "V_mem", t_start: float = None) -> bool:
        """
        Return True if an AP is detected, else False.

        Returns
        -------
        is_recruited                : bool
            Return True if an AP is detected, else False.
        """
        if not "recruited" in self:
            n_aps = self.count_APs(vm_key) != 0
            if n_aps:
                if t_start is None:
                    self["recruited"] = n_aps
                else:
                    _, t_starts = self.get_start_APs(vm_key=vm_key)
                    # print(t_start)
                    # print(t_starts)
                    # print(t_starts[t_starts>=t_start])
                    # print(len(t_starts[t_starts>=t_start])>0)
                    self["recruited"] = len(t_starts[t_starts >= t_start]) > 0
            else:
                self["recruited"] = n_aps
        return self["recruited"]

    def is_blocked(
        self, AP_start: float, freq: float = None, t_refractory: float = 1
    ) -> bool | None:
        """
        check if the axon is blocked or not.

        Warning
        -------
        A test pulse must be added to generate an AP propagating through the axon. This test AP is used to
        validate or not the neural conduction of the axon.

        Parameters
        ----------
        AP_start : float
            timestamp of the test pulse start, in ms.
        freq : float, optional
            Frequency of the stimulation, for KES block, by default None
        t_refractory : float, optional
            Axon refractory period, by default 1

        Returns
        -------
        bool
            True is the axon is blocked (the test AP doesn't propagate through), else false.
        """
        if not "blocked" in self:
            vm_key = "V_mem"
            if freq is not None:
                self.filter_freq("V_mem", freq, Q=2)
                vm_key += "_filtered"
            self.rasterize(
                vm_key=vm_key, clear_artifacts=False
            )  # artifacts clearing produces strange results :(
            _, t_starts = self.get_start_APs(vm_key)
            n_APs = len(t_starts[t_starts >= AP_start])

            t_AP_start = None
            if n_APs > 0:
                test_AP_idx = nearest_greater_idx(
                    t_starts, AP_start
                )  # get idx of test AP in the APs list
                x_APs, _, t_APs, _ = self.split_APs(vm_key)
                x_AP_test = x_APs[test_AP_idx]
                t_AP_test = t_APs[test_AP_idx]
                _, t_AP_start = self.get_start_AP(x_AP_test, t_AP_test)

            delta = 1

            if n_APs == 0 or (
                t_AP_start is not None and t_AP_start >= AP_start + delta
            ):
                rise_warning(
                    f"is_blocked in Axon {self.ID}: No AP detected after the test pulse. Make sure the stimulus is strong enough, attached to the axon or not colliding with onset response. \n ... Fiber considered as blocked."
                )
                self["blocked"] = False
                return self["blocked"]
            if n_APs > 2:
                rise_warning(
                    f"is_blocked in Axon {self.ID}: More than two APs are detected after the test pulse, likely due to onset response. This can cause erroneous block state estimation. \n ... Consider increasing axon's spatial discretization."
                )
                self["blocked"] = False
                return self["blocked"]

            if self.has_AP_reached_end(
                x_AP_test, t_AP_test
            ):  # test AP has reached the end --> is not blocked
                self["blocked"] = False
                return self["blocked"]
            else:
                if not self.is_AP_in_timeframe(x_AP_test, t_AP_test):  #
                    rise_warning(
                        f"is_blocked in Axon {self.ID}: Test AP didn't not reach axon ends within the simulation timeframe. Consider increasing simulation time or start the test stimulus earlier. "
                    )
                    return None
                _, _, coll_list = self.get_collision_pts(vm_key)
                if coll_list[test_AP_idx]:
                    rise_warning(
                        f"is_blocked in Axon {self.ID}: Test AP is colliding with an other AP, probably onset response. Consider increasing the duration between start of block stimulus and test stimulus."
                    )
                    return None

                t_AP_test_max = np.max(t_AP_test)  # test AP last time position:

                if len(t_starts[t_starts < AP_start]):
                    if (
                        np.min(np.abs(t_starts[t_starts < AP_start] - t_AP_test_max))
                        < t_refractory
                    ):  # check if test AP is during refractory period
                        rise_warning(
                            f"is_blocked in Axon{self.ID}: Test AP occures during axon's refractory period, probably due to onset response. Consider increasing the duration between start of block stimulus and test stimulus."
                        )
                        return None

                if len(t_starts[t_starts > t_AP_start]):  # AP jump
                    if (
                        np.min(np.abs(t_starts[t_starts > AP_start] - t_AP_test_max))
                        < t_refractory
                    ):
                        # todo: make sure that the jumping AP is reaching the over side of the axon
                        self["blocked"] = False
                        return self["blocked"]
                self["blocked"] = True
                return self["blocked"]
        return self["blocked"]

    def split_APs(
        self, vm_key: str = "V_mem"
    ) -> list[np.array] | list[np.array] | list[np.array] | list[np.array]:
        """
        Detects individual Action potential in vm_key and split them in lists

        Parameters
        ----------
        vm_key : str, optional
             vmembrane key, by default "V_mem"

        Returns
        -------
        list[np.array]
            list of the x_pos of each AP
        list[np.array]
            list of the x index of each AP
        list[np.array]
            list of the time of each AP
        list[np.array]
            list of the time index of each AP
        """
        # if not vm_key + "_raster_x_position" in self:
        if not vm_key + "_raster_x_position" in self:
            self.rasterize(vm_key=vm_key, clear_artifacts=False)
        x_APs = []
        x_idx_APs = []
        t_APs = []
        t_idx_APs = []
        x_raster = self[vm_key + "_raster_x_position"].copy()
        t_raster = self[vm_key + "_raster_time"].copy()
        x_idx_raster = self[vm_key + "_raster_position"].copy()
        t_idx_raster = self[vm_key + "_raster_time_index"].copy()

        min_size = self._get_min_AP_length()
        # plt.figure()
        if len(x_raster) > min_size:
            while len(x_raster) > min_size:
                x_AP, x_idx_AP, t_AP, t_idx_AP, AP_idx = get_first_AP(
                    x_raster, x_idx_raster, t_raster, t_idx_raster
                )
                if len(x_AP) == 0:
                    AP_len = 0
                else:
                    AP_len = np.max(
                        [
                            self.get_AP_upward_len(x_AP, t_AP),
                            self.get_AP_downward_len(x_AP, t_AP),
                        ]
                    )
                # print(f"upward: {self.get_AP_upward_len(x_AP, t_AP)} - downward: {self.get_AP_downward_len(x_AP, t_AP)}")
                # plt.scatter(t_AP,x_AP)
                if AP_len >= min_size:
                    x_APs.append(x_AP)
                    t_APs.append(t_AP)
                    x_idx_APs.append(x_idx_AP)
                    t_idx_APs.append(t_idx_AP)
                if len(AP_idx):
                    x_raster = np.delete(x_raster, AP_idx)
                    t_raster = np.delete(t_raster, AP_idx)
                    x_idx_raster = np.delete(x_idx_raster, AP_idx)
                    t_idx_raster = np.delete(t_idx_raster, AP_idx)
                else:
                    x_raster = np.array([])
                    t_raster = np.array([])
                    x_idx_raster = np.array([])
                    t_idx_raster = np.array([])

        # plt.show()
        # exit()
        return (x_APs, x_idx_APs, t_APs, t_idx_APs)

    def count_APs(self, vm_key: str = "V_mem") -> int:  # **kwargs
        """
        Count number of APs detected in vm_key

        Parameters
        ----------
        vm_key : str, optional
            Vmembrane key, by default "V_mem"

        Returns
        -------
        int
            number of APs detected
        """
        x, _, _, _ = self.split_APs(vm_key)
        return len(x)

    def _get_min_AP_length(self, min_size: float = 0.1) -> int:
        """
        Returns the minimum propation length of an AP, set to 10% of the axon length by default

        Parameters
        ----------
        min_size : float, optional
            minimum AP length, with respect to the fiber length, by default .1

        Returns
        -------
        int
            return the minimum AP length pts
        """
        if self.myelinated == True and self.rec == "all":
            n_x = len(self.node_index)
        else:
            n_x = len(self.x_rec)
        return int(n_x * min_size)

    def get_start_AP(self, x_AP: np.array, t_AP: np.array) -> float | float:
        """
        Returns the x,t start values of the AP

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        float
            x start value of the AP
        float
            t start value of the AP
        """
        start_idx = t_AP.argmin()
        return (x_AP[start_idx], t_AP[start_idx])

    def get_start_APs(self, vm_key: str = "V_mem") -> NDArray | NDArray:
        """
        Return list of (x,t) start positions of each detected APs

        Parameters
        ----------
        vm_key : str, optional
            Vmembrane key, by default "V_mem", by default "V_mem"

        Returns
        -------
        Returns
        -------
        NDArray
            Array of the start x-position of each APs
        NDArray
            Array of the start t-position of each APs
        """
        x_APs, _, t_APs, _ = self.split_APs(vm_key)
        x_AP_start = []
        t_AP_start = []
        for x_AP, t_AP in zip(x_APs, t_APs):
            x_AP_s, t_AP_s = self.get_start_AP(x_AP, t_AP)
            x_AP_start.append(x_AP_s)
            t_AP_start.append(t_AP_s)
        return (np.array(x_AP_start), np.array(t_AP_start))

    def get_xmax_AP(self, x_AP: np.array, t_AP: np.array) -> float | float:
        """
        Returns the x,t values the maximum AP x-position

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        float
            x value of the maximum AP x-position
        float
            t value of the maximum AP x-position
        """
        max_idx = x_AP.argmax()
        return (x_AP[max_idx], t_AP[max_idx])

    def get_xmin_AP(self, x_AP: np.array, t_AP: np.array) -> float | float:
        """
        Returns the x,t values the minimum AP x-position

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        float
            x value of the minimum AP x-position
        float
            t value of the minimum AP x-position
        """
        min_idx = x_AP.argmin()
        return (x_AP[min_idx], t_AP[min_idx])

    def get_AP_upward_len(self, x_AP: np.array, t_AP: np.array) -> int:
        """
        Returns the length (number of x pts) of the AP in the upward direction

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        int
            number of AP x-pos points in the upward direction
        """
        x_start, _ = self.get_start_AP(x_AP, t_AP)
        x_max, _ = self.get_xmax_AP(x_AP, t_AP)
        len_upward = x_AP[((x_AP >= x_start) & (x_AP <= x_max))]
        return len(len_upward)

    def get_AP_downward_len(self, x_AP: np.array, t_AP: np.array) -> int:
        """
        Returns the length (number of x pts) of the AP in the downward direction

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        int
            number of AP x-pos points in the downward direction
        """
        x_start, _ = self.get_start_AP(x_AP, t_AP)
        x_min, _ = self.get_xmin_AP(x_AP, t_AP)
        len_downward = x_AP[((x_AP <= x_start) & (x_AP >= x_min))]
        return len(len_downward)

    def has_AP_reached_end(self, x_AP: np.array, t_AP: np.array) -> bool:
        """
        Return true if the AP has reached the end of the axon in both direction, else false

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        bool
            is true if the AP has reached the end of the axon in both direction, else false
        """
        x = self.get_axon_xrec()
        x_max = np.max(x)
        x_min = np.min(x)
        x_max_AP, _ = self.get_xmax_AP(x_AP, t_AP)
        x_min_AP, _ = self.get_xmin_AP(x_AP, t_AP)
        return x_max == x_max_AP and x_min_AP == x_min

    def APs_reached_end(self, vm_key: str = "V_mem") -> bool:
        """
        Return true if ALL APs have reached the both ends of the axon

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        bool
            True if ALL APs have reached the both ends of the axon, else False
        """

        x_APs, _, t_APs, _ = self.split_APs(vm_key=vm_key)
        if len(x_APs):
            for x_AP, t_AP in zip(x_APs, t_APs):
                if not self.has_AP_reached_end(x_AP, t_AP):
                    return False
        return True

    def is_AP_in_timeframe(self, x_AP: np.array, t_AP: np.array) -> bool:
        """
        Return true if AP has reached it's last position (in both direction) within the simulation timeframe, else False

        Parameters
        ----------
        x_AP : np.array
            x positions of the AP
        t_AP : np.array
            time values of the AP

        Returns
        -------
        bool
            true if AP has reached its last position (in both direction) within the simulation timeframe, else False
        """
        if self.has_AP_reached_end(x_AP, t_AP):
            return True
        else:
            up_len = self.get_AP_upward_len(x_AP, t_AP)
            down_len = self.get_AP_downward_len(x_AP, t_AP)
            _, t_start = self.get_start_AP(x_AP, t_AP)
            if up_len > down_len:
                _, t_stop = self.get_xmax_AP(x_AP, t_AP)
                dt_AP = (t_stop - t_start) / up_len
            else:
                _, t_stop = self.get_xmin_AP(x_AP, t_AP)
                dt_AP = (t_stop - t_start) / down_len

            if dt_AP < 0.5:
                dt_AP = 0.5
            _, t_xmax_AP = self.get_xmax_AP(x_AP, t_AP)
            _, t_xmin_AP = self.get_xmin_AP(x_AP, t_AP)
            tmax = np.max(self.t)
            if (t_xmax_AP + dt_AP > tmax) or (t_xmin_AP + dt_AP > 10 * tmax):
                return False
            return True

    def APs_in_timeframe(self, vm_key: str = "V_mem") -> bool:
        """
        Return true if ALL APs have reached their last position (in both direction) within the simulation timeframe, else False

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        bool
            True if ALL APs have reached their last position (in both direction) within the simulation timeframe, else False
        """
        x_APs, _, t_APs, _ = self.split_APs(vm_key=vm_key)
        if len(x_APs):
            for x_AP, t_AP in zip(x_APs, t_APs):
                if not self.is_AP_in_timeframe(x_AP, t_AP):
                    return False
        return True

    def get_collision_pts(self, vm_key: str = "V_mem") -> list[float] | list[float]:
        """
        Returns three lists: - two containing the x,t coordinates of the interAPs colliding coordinates
                             - one boolean list where true means the AP is colliding, else false

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        list[float]
            x coordinates of the interAPs collision point
        list[float]
            t coordinates of the interAPs collision point
        list[bool]
            list of colliding APs: true when colliding else false
        """
        x_APs, _, t_APs, _ = self.split_APs(vm_key=vm_key)
        x_APs_coll = []
        t_APs_coll = []
        idx_coll = []
        colliding_list = [False for i in range(len(x_APs))]
        idx_APs = np.arange(len(x_APs))

        for x_AP, t_AP, idx_AP in zip(x_APs, t_APs, idx_APs):
            if not self.has_AP_reached_end(x_AP, t_AP):
                x_APs_coll.append(x_AP)
                t_APs_coll.append(t_AP)
                idx_coll.append(idx_AP)
        if len(x_APs_coll) <= 1:  # need at least 2 APs to get a collision
            return ([], [], colliding_list)
        ids = np.arange(len(x_APs_coll))
        comb_list = list(combinations(ids, 2))
        x_coll_l = []
        t_coll_l = []
        for idx_comb in comb_list:
            x_inter, t_inter = self.get_interAPs_collision(
                x_APs_coll[idx_comb[0]],
                t_APs_coll[idx_comb[0]],
                x_APs_coll[idx_comb[1]],
                t_APs_coll[idx_comb[1]],
            )
            if (x_inter and t_inter) > 0:
                x_coll_l.append(x_inter)
                t_coll_l.append(t_inter)
                colliding_list[idx_coll[idx_comb[1]]] = True
                colliding_list[idx_coll[idx_comb[0]]] = True

        return (x_coll_l, t_coll_l, colliding_list)

    def detect_AP_collisions(self, vm_key: str = "V_mem") -> bool:
        """
        Return True is at least one collision between two APs is detected, else False

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        bool
            True if an interAP collision is detected, else False
        """
        _, t_coll, _ = self.get_collision_pts(vm_key)
        if len(t_coll):
            return True
        return False

    def get_interAPs_collision(
        self, x_AP1: NDArray, t_AP1: NDArray, x_AP2: NDArray, t_AP2: NDArray
    ) -> float | float:
        """
        Returns the estimated collision coordinates of two APs. Returns (0,0) if the collision is out of scope.

        Parameters
        ----------
        x_AP1 : NDArray
            x positions of the first AP
        t_AP1 : NDArray
            t positions of the first AP
        x_AP2 : NDArray
            x positions of the seconc AP
        t_AP2 : NDArray
            t positions of the second AP
        Returns
        -------
        float
            x position of the intersection (collision) point. Is 0 is the position is out of scope
        float
            t position of the intersection (collision) point. Is 0 is the position is out of scope
        """
        poly_up_1, poly_down_1 = self.linfit_AP(x_AP1, t_AP1)
        poly_up_2, poly_down_2 = self.linfit_AP(x_AP2, t_AP2)
        x_inter1, t_inter1 = self.get_1dpoly_intersec(poly_up_1, poly_down_2)
        x_inter2, t_inter2 = self.get_1dpoly_intersec(poly_up_2, poly_down_1)

        x1_max, t1_max = self.get_xmax_AP(x_AP1, t_AP1)
        x1_min, t1_min = self.get_xmin_AP(x_AP1, t_AP1)

        x2_max, t2_max = self.get_xmax_AP(x_AP2, t_AP2)
        x2_min, t2_min = self.get_xmin_AP(x_AP2, t_AP2)

        if self._pts_in_sim_range(x_inter1, t_inter1) and self._pts_in_sim_range(
            x_inter2, t_inter2
        ):
            if t_inter2 > t_inter1:
                if self._AP_pt_in_range(
                    x1_max, t1_max, x_inter2, t_inter2
                ) and self._AP_pt_in_range(x2_min, t2_min, x_inter2, t_inter2):
                    if t_inter2 > (t1_max and t2_min):
                        return x_inter2, t_inter2
                if self._AP_pt_in_range(
                    x1_min, t1_min, x_inter2, t_inter2
                ) and self._AP_pt_in_range(x2_max, t2_max, x_inter2, t_inter2):
                    if t_inter2 > (t1_min and t2_max):
                        return x_inter2, t_inter2
            else:
                if self._AP_pt_in_range(
                    x1_max, t1_max, x_inter1, t_inter1
                ) and self._AP_pt_in_range(x2_min, t2_min, x_inter1, t_inter1):
                    if t_inter1 > (t1_max and t2_min):
                        return x_inter1, t_inter1
                if self._AP_pt_in_range(
                    x1_min, t1_min, x_inter1, t_inter1
                ) and self._AP_pt_in_range(x2_max, t2_max, x_inter1, t_inter1):
                    if t_inter1 > (t1_min and t2_max):
                        return x_inter1, t_inter1
        return 0, 0

    def _pts_in_sim_range(self, x: float, t: float) -> bool:
        """
        Returns true if the (x,t) point is within the simulation range

        Parameters
        ----------
        x : float
            x coordinate of the point
        t : float
            t coordinate of the point

        Returns
        -------
        bool
            true if the (x,t) point is within the simulation range, else false
        """
        x_max = np.max(self.get_axon_xrec())
        t_max = np.max(self.t)
        return (x < x_max) and (x > 0) and (t > 0) and (t < t_max)

    def _AP_pt_in_range(
        self, x1: float, t1: float, x2: float, t2: float, tol: float = 0.12
    ) -> bool:
        """
        Return true is the point (x1,t1) and (x2,t2) are within a range, set by tol

        Parameters
        ----------
        x1 : float
            x coordinate of the (x1,t1) point
        t1 : float
            t coordinate of the (x1,t1) point
        x2 : float
            x coordinate of the (x2,t2) point
        t2 : float
            t coordinate of the (x2,t2) point
        tol : float, optional
            range tolerance, expressed as a fraction of the (x1,t1) pts. by default 0.1

        Returns
        -------
        bool
            True if the two points are within the range
        """
        return np.abs(x1 - x2) <= tol * x1 and np.abs(t1 - t2) <= tol * t1

    def get_1dpoly_intersec(self, poly1: np.poly1d, poly2: np.poly1d) -> float | float:
        """
        Returns the intersection points of two 1D poly

        Parameters
        ----------
        poly1 : np.poly1d
            First 1D poly
        poly2 : np.poly1d
            Second 1D poly

        Returns
        -------
        float
            y intersection point
        float
            x intersection point
        """
        x_inter = (poly2.c[1] - poly1.c[1]) / (poly1.c[0] - poly2.c[0])
        return (poly1(x_inter), x_inter)

    def linfit_AP(self, x_AP: NDArray, t_AP: NDArray) -> np.poly1d | np.poly1d:
        """
        Fit the AP with two 1D polynomial equations: one for the upward propagation, one for the downward propagation

        Parameters
        ----------
        x_AP : NDArray
            x positions of the AP
        t_AP : NDArray
            t positions of the AP

        Returns
        -------
        np.poly1d
            AP upward direction 1D poly fit
        np.poly1d
            AP downward direction 1D poly fit
        """
        x_max, _ = self.get_xmax_AP(x_AP, t_AP)
        x_min, _ = self.get_xmin_AP(x_AP, t_AP)
        x_start, _ = self.get_start_AP(x_AP, t_AP)

        # fit upward AP
        upward_idx = np.argwhere((x_AP >= x_start) & (x_AP <= x_max))
        upward_idx = [x[0] for x in upward_idx]
        x_AP_up = x_AP[upward_idx]
        t_AP_up = t_AP[upward_idx]
        idx_sorted = np.argsort(t_AP_up)
        t_AP_up = t_AP_up[idx_sorted]
        x_AP_up = x_AP_up[idx_sorted]
        p_up = np.poly1d(np.polyfit(t_AP_up, x_AP_up, 1))

        # fit downward AP
        downward_idx = np.argwhere((x_AP <= x_start) & (x_AP >= x_min))
        downward_idx = [x[0] for x in downward_idx]
        x_AP_down = x_AP[downward_idx]
        t_AP_down = t_AP[downward_idx]
        idx_sorted = np.argsort(t_AP_down)
        t_AP_down = t_AP_down[idx_sorted]
        x_AP_down = x_AP_down[idx_sorted]
        p_down = np.poly1d(np.polyfit(t_AP_down, x_AP_down, 1))
        return (p_up, p_down)

    def get_axon_xrec(self) -> NDArray:
        """
        Return the  x-position recorded array

        Returns
        -------
        NDArray
            x-position recorded array
        """

        if self["myelinated"] == True:
            if self["rec"] == "All":
                x_idx = self["node_index"]
                x = self["x"][x_idx]
            else:
                x = self["x_rec"]
        else:
            x = self["x_rec"]
        return x

    def get_avg_AP_speed(self, vm_key: str = "V_mem") -> float:
        """
        Returns the averaged propagtion speed of each APs, in m/s.

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        float
            averaged propagation speed of each APs, in m/s. Returns 0.0 if no AP is detected for speed evaluation.
        """
        ap_speed = self.getAPspeed(vm_key)
        if len(ap_speed):
            return np.round(np.mean(ap_speed), 3)
        else:
            rise_warning("No AP detected, can't evaluate AP propagation speed.")
            return 0.0

    def getAPspeed(self, vm_key: str = "V_mem") -> list[float]:
        """
        Return the propagtion speed of each APs, in m/s

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        Returns
        -------
        list[float]
            list of propagation speed of each APs, in m/s
        """
        x_APs, _, t_APs, _ = self.split_APs(vm_key=vm_key)
        APspeed = []
        if len(x_APs):
            for x_AP, t_AP in zip(x_APs, t_APs):
                APspeed.append(np.round(self._APspeed(x_AP, t_AP), 3))
        if len(APspeed):
            return APspeed
        else:
            rise_warning("No AP detected, can't evaluate AP propagation speed.")
            return []

    def _APspeed(self, x_AP: NDArray, t_AP: NDArray) -> float:
        """
        Evaluate the propagation speed of one AP, in m/s

        Parameters
        ----------
        x_AP : NDArray
            x positions of the AP
        t_AP : NDArray
            t positions of the AP

        Returns
        -------
        float
            propagation of the AP, in m/s
        """
        x_start, t_start = self.get_start_AP(x_AP, t_AP)
        # if self.get_AP_upward_len(x_AP,t_AP) > self.get_AP_downward_len(x_AP,t_AP):
        x_stop, t_stop = self.get_xmax_AP(x_AP, t_AP)
        # else:
        #    x_stop,t_stop  = self.get_xmin_AP(x_AP,t_AP)
        speed = np.abs(x_stop - x_start) / (t_stop - t_start)
        return speed * 1e-3

    def remove_raster_artifacts(self, vm_key: str = "V_mem") -> None:  # **kwargs
        """
        Remove artifacts (non-APs) rasterized points.

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"
        """
        x_APs, x_idx, t_APs, t_idx = self.split_APs(vm_key)
        x_clean = []
        x_idx_clean = []
        t_clean = []
        t_idx_clean = []

        for i, _ in enumerate(x_APs):
            x_clean += list(x_APs[i])
            x_idx_clean += list(x_idx[i])
            t_clean += list(t_APs[i])
            t_idx_clean += list(t_idx[i])

        self[vm_key + "_raster_position"] = np.array(x_idx_clean)
        self[vm_key + "_raster_x_position"] = np.array(x_clean)
        self[vm_key + "_raster_time_index"] = np.array(t_idx_clean)
        self[vm_key + "_raster_time"] = np.array(t_clean)

    def rasterize(
        self, vm_key: str = "V_mem", clear_artifacts: bool = True, **kwargs
    ) -> None:
        """
        Rasterize a membrane potential (or filtered or any quantity processed from membrane voltage), with AP detection.
        This function adds 4 items to the class, with the key termination '_raster_position', '_raster_x_position', '_raster_time_index', '_raster_time' concatenated to the original key.
        These keys correspond to:

            - _raster_position    : AP position as the indice of the original key
            - _raster_x_position  : AP position as geometrical position in um
            - _raster_time_index  : AP time as the indice of the original key
            - _raster_time        : AP time as ms

        Parameters
        ----------
        vm_key : str, optional
            Rasterized Vmembrane key , by default "V_mem"

        clear_artifacts : bool
            if True, remove artifacts (non-APs) rasterized points. By default True.

        **kwargs:
            - threshold: (float) threshold for AP detection, in mV. Default value is taken from axon model
            - t_min_AP: (float) minimum AP duration, in ms. Default is 0.1ms
            - t_refractory: (float) inter-AP duration, in ms. Default is 0.5ms
            - t_start: (float) start time for rasterize, in ms. Default is 0ms
            - t_stop: (float) stop time for rasterize, in ms. Default is simulation time.
        """

        # clear_artifacts = False
        if not vm_key + "_raster_position" in self:

            if "threshold" in kwargs:
                threshold = kwargs["threshold"]
            elif "threshold" in self:
                threshold = self["threshold"]
            else:
                threshold = 0

            if "t_min_AP" in kwargs:
                t_min_AP = kwargs["t_min_AP"]
            else:
                t_min_AP = 0.1

            if "t_refractory" in kwargs:
                t_refractory = kwargs["t_refractory"]
            else:
                t_refractory = 0.5

            t_start = None
            if "t_start" in kwargs:
                t_start = kwargs["t_start"]

            t_stop = None
            if "t_stop" in kwargs:
                t_start = kwargs["t_stop"]

            ## selecting the list of position considering what has been recorded
            vm = self[vm_key].copy()
            if self["myelinated"] == True:
                if self["rec"] == "all":
                    x_idx = self["node_index"]
                    x = self["x"][x_idx]
                    vm = vm[x_idx]
                else:
                    x = self["x_rec"]
            else:
                x = self["x_rec"]

            (
                self[vm_key + "_raster_position"],
                self[vm_key + "_raster_x_position"],
                self[vm_key + "_raster_time_index"],
                self[vm_key + "_raster_time"],
            ) = rasterize(
                y_data=vm,
                x_data=x,
                t_data=self.t,
                threshold=threshold,
                t_min_AP=t_min_AP,
                t_refractory=t_refractory,
                t_start=t_start,
                t_stop=t_stop,
            )
            if clear_artifacts:
                self.remove_raster_artifacts(vm_key)

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

        rise_warning(
            "DeprecationWarning: ",
            "speed is obsolete, please use get_avg_AP_speed() instead",
        )
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
        good_indexes_position = np.intersect1d(
            sup_position_indexes, inf_position_indexes
        )
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

        # rise_warning(
        # "DeprecationWarning: ",
        # "block is obsolete, please used isBlocked() instead"
        # )
        if "blocked" in self:
            return self["blocked"]
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
                self["blocked"] = False
                return self["blocked"]
        sup_time_indexes = np.where(self[good_key_prefix + "_time"] > t_start)
        inf_time_indexes = np.where(self[good_key_prefix + "_time"] < t_stop)
        good_indexes_time = np.intersect1d(sup_time_indexes, inf_time_indexes)
        good_spike_times = self[good_key_prefix + "_time"][good_indexes_time]
        blocked_spike_positionlist = self[good_key_prefix + "_x_position"][
            good_indexes_time
        ]
        if len(blocked_spike_positionlist) == 0:
            self["blocked"] = None
            return self["blocked"]
        if "intra_stim_positions" in self:
            if self["intra_stim_positions"] < self["extracellular_electrode_x"]:
                position_max = max_spike_position(
                    blocked_spike_positionlist, position_max, spike_begin="down"
                )

                if blocked_spike_positionlist[position_max] < 9.0 / 10 * self["L"]:
                    self["blocked"] = True
                    return self["blocked"]
                else:
                    for i in range(position_max - 1):
                        if (
                            blocked_spike_positionlist[i + 1]
                            - blocked_spike_positionlist[i]
                            > self["L"] / 5
                        ):
                            self["blocked"] = True
                            return self["blocked"]
                    else:
                        self["blocked"] = False
                        return self["blocked"]
            else:
                position_max = max_spike_position(
                    blocked_spike_positionlist, position_max, spike_begin="up"
                )
                if min(blocked_spike_positionlist) > 1.0 / 10 * self["L"]:
                    self["blocked"] = True
                    return self["blocked"]
                else:
                    for i in range(position_max - 1):
                        if (
                            blocked_spike_positionlist[i]
                            - blocked_spike_positionlist[i + 1]
                            > self["L"] / 5
                        ):
                            self["blocked"] = True
                            return self["blocked"]
                    else:
                        self["blocked"] = False
                        return self["blocked"]
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

        rise_warning("DeprecationWarning: ", "check_test_AP is obsolete")
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

        rise_warning("DeprecationWarning: ", "detect_start_extrastim is obsolete")
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

    def extra_stim_properties(self) -> dict:
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
            electrode["max amplitude"] = [max(s) for s in self["extracellular_stimuli"]]

        return electrode

    def block_summary(
        self, AP_start: float, freq: float = None, t_refractory: float = 1
    ) -> dict:
        """
        Return axon block characteristics: blocked, onset response, number of APs)

        Parameters
        ----------
        AP_start : float
            timestamp of the test pulse start, in ms.
        freq : float, optional
            Frequency of the stimulation, for KES block, by default None
        t_refractory : float, optional
            Axon refractory period, by default 1

        Returns
        -------
        axon_state       : dict
            tuple containing the block characteristics: is_blocked (bool), has_onset (bool), n_onset (int)
        """

        if {"is_blocked", "has_onset", "n_onset"} not in self:
            vm_key = "V_mem"
            # if freq is not None:
            #     vm_key += "_filtered"
            # required_keys = {f"{vm_key}_raster_position",
            #                 f"{vm_key}_raster_x_position",
            #                 f"{vm_key}_raster_time_index",
            #                 f"{vm_key}_raster_time"}
            required_keys = {vm_key}

            if required_keys in self:
                # vm_key = "V_mem"
                # if freq is not None:
                #    self.filter_freq("V_mem", freq, Q=2)
                #    vm_key += "_filtered"

                blocked = self.is_blocked(AP_start, freq, t_refractory)
                n_APs = self.count_APs(vm_key) - 1
                if n_APs < 0:
                    n_APs = 0
                onset = n_APs > 0

                axon_state = {
                    "is_blocked": blocked,
                    "has_onset": onset,
                    "n_onset": n_APs,
                }
                self.update(axon_state)
            else:
                rise_warning(
                    "The following keys are missing.",
                    required_keys - set(self.keys()),
                    " Please check the simulation parameters",
                )
                return None

        else:
            axon_state = {
                "is_blocked": self.is_blocked,
                "has_onset": self.has_onset,
                "n_onset": self.n_onset,
            }
        return axon_state

    def find_central_index(self) -> int:
        """
        Returns the index of the closer node from the center

        Returns
        -------
        int
            index of `x_rec` of the closer node from the center
        """
        n_center = len(self["x_rec"]) // 2
        return n_center

    ##################################
    ## Impedance properties methods ##
    ##################################

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
            rise_warning(
                "f_mem cannot be computed computed without membrane conductivity"
            )
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

    def get_membrane_conductivity(
        self,
        x: float | None = None,
        t: float | None = None,
        i_x: int | np.ndarray | None = None,
        i_t: int | np.ndarray | None = None,
        unit: str = "S/cm**2",
        mem_th: float = 7 * nm,
    ) -> float:
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
        n_x = len(self["g_mem"][:, 0])
        if t is None:
            if i_t is None:
                i_t = np.arange(n_t)
        else:
            i_t = int(n_t * t / self["t_sim"])
        if x is None:
            if i_x is None:
                i_x = np.arange(n_x)
        else:
            i_x = np.argmin(abs(self["x_rec"] - x))

        if np.iterable(i_x) and np.iterable(i_t):
            g = self["g_mem"][np.ix_(i_x, i_t)]
        else:
            g = self["g_mem"][i_x, i_t]

        # Surface conductivity in [S]/([m]*[m])
        if "2" in unit:
            return convert(g, "S/cm**2", unit)
        # conductivity in [S]/[m]
        else:
            g *= from_nrv_unit(mem_th, "cm")
            return convert(g, "S/cm", unit)

    def get_membrane_capacitance(
        self, unit: str = "uF/cm**2", mem_th: float = 7 * nm
    ) -> float:
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

    def get_membrane_complexe_admitance(
        self,
        f: float = 1.0,
        x: float | None = None,
        t: float | None = None,
        i_x: int | np.ndarray | None = None,
        i_t: int | np.ndarray | None = None,
        unit: str = "S/m",
        mem_th: float = 7 * nm,
    ) -> np.array:
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
        g = self.get_membrane_conductivity(x=x, t=t, i_x=i_x, i_t=i_t, mem_th=mem_th)
        f_mem = g / (2 * np.pi * c)

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

    def get_membrane_material(
        self, t: float = 0, unit: str = "S/m", mem_th: float = 7 * nm, **interp_kwargs
    ) -> f_material:

        n_t = len(self["g_mem"][0])
        i_t = int(n_t * t / self["t_sim"])
        x_ = self["x_rec"]
        g_ = deepcopy(self["g_mem"][:, i_t])

        # Surface conductivity in [S]/([m]*[m])
        if "2" in unit:
            g_ = convert(g_, "S/cm**2", unit)
        # conductivity in [S]/[m]
        else:
            g_ *= from_nrv_unit(mem_th, "cm")
            g_ = convert(g_, "S/cm", unit)
        return mat_from_interp(x_, g_, **interp_kwargs)

    #####################
    ## Ploting methods ##
    #####################

    def raster_plot(self, axes: plt.axes, key: str = "V_mem", **kwgs) -> None:
        required_keys = {key, "tstop", "L"}
        if required_keys in self:
            self.rasterize(key)
            axes.scatter(
                self[key + "_raster_time"], self[key + "_raster_x_position"], **kwgs
            )
            axes.set_xlim(0, self["tstop"])
            axes.set_ylim(0, self["L"])
        else:
            rise_warning(
                "The following keys are missing.",
                required_keys - set(self.keys()),
                " Please check the simulation parameters",
            )

    def colormap_plot(
        self, axes: plt.axes, key: str = "V_mem", switch_axes: bool = False, **kwgs
    ) -> plt.colorbar:
        required_keys = {key, "tstop", "L", "t"}
        if required_keys in self:
            x_ = self["t"]
            y_ = self.get_axon_xrec()
            c_ = self[key]

            if switch_axes:
                x_, y_, c_ = y_, x_, c_.T
                axes.set_ylabel("Time (ms)")
                axes.set_xlabel("Position (µm)")
                axes.set_ylim(0, self["tstop"])
                axes.set_xlim(0, self["L"])
            else:
                axes.set_xlabel("Time (ms)")
                axes.set_ylabel("Position (µm)")
                axes.set_xlim(0, self["tstop"])
                axes.set_ylim(0, self["L"])
            map = axes.pcolormesh(x_, y_, c_, shading="auto", **kwgs)

            cbar = plt.colorbar(map)
            cbar.set_label(key)
            return cbar
        else:
            rise_warning(
                "The following keys are missing.",
                required_keys - set(self.keys()),
                " Please check the simulation parameters",
            )
        return None

    @abstractmethod
    def plot_x_t(
        self,
        axes: plt.Axes,
        x_index: np.ndarray,
        x_pos: np.ndarray,
        key: str = "V_mem",
        color: str = "k",
        switch_axes=False,
        norm=None,
        **kwgs,
    ) -> None:
        """
        Plot `key` in time at various position.

        Warning
        -------
        This method should only internally called by either `myelinated.plot_x_t` or `unmyelinated.plot_x_t`. Therefore, `x_index`, `x_pos` arguments are automatically set by the daughter class methods

        Parameters
        ----------
        axes : plt.Axes
            axes of the figure to display the fascicle
        x_index : np.ndarray
            list of index to plot
        x_pos : np.ndarray
            x position that should be ploted
        key : str, optional
            key of the results' signal that should be ploted, by default "V_mem"
        color : str, optional
            color of the line plot, by default "k"
        switch_axes : bool, optional
            _description_, by default False
        """
        dx = np.abs(x_pos[1] - x_pos[0])
        if norm is not None:
            norm_fac = norm
        else:
            norm_fac = dx / abs(np.max(self[key] - np.min(self[key])) * 1.1)
        offset = np.abs(np.min(self[key][0] * norm_fac))
        for x, x_idx in zip(x_pos, x_index):
            x_ = self["t"]
            y_ = self[key][x_idx] * norm_fac + x + offset
            if switch_axes:
                x_, y_ = y_, x_[::-1]
            axes.plot(x_, y_, color=color, **kwgs)
