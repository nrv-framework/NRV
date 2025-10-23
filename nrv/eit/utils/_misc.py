import numpy as np
import os
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from copy import deepcopy

from ...fmod.FEM.fenics_utils import get_sig_ap
from ...nmod.results import nerve_results, axon_results
from ...ui import sample_keys
from ...utils import sci_round, get_MRG_parameters, convert


# File handling
def touch(path):
    with open(path, "a"):
        os.utime(path, None)


# Numpy usefull
def gen_from_idx(idx: np.ndarray, n: int, add_0: bool = False) -> np.ndarray:
    _arr = np.arange(n)
    if np.sum(idx == 0) > 0:
        _arr += np.sum(idx == 0)
    _arr = np.searchsorted(idx, _arr)
    if add_0:
        _arr = np.concatenate((_arr[:1], _arr))
    return _arr


def gen_idx_arange(idx: np.ndarray, n: int, add_0: bool = False) -> np.ndarray:
    idx = np.concatenate(([0], idx, [n]))
    positions = np.arange(n)
    section = np.searchsorted(idx[1:], positions, side="right")
    # Subtract start index of that section to get counter within each segment
    _arr = positions - idx[section]
    if add_0:
        _arr[: idx[0]] += 1
        _arr = np.concatenate(([0], _arr))
    return _arr


def adjust_axes(arr1: np.ndarray, arr2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    add missing dimension to arr2 for it to be broadastable with arr1

    Warning
    -------
    Only reshape arr2 to match arr1's ndim, arr2.shape is must be included in arr1.shape

    Parameters
    ----------
    arr1 : np.ndarray
        _description_
    arr2 : np.ndarray
        _description_

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        _description_

    Raises
    ------
    ValueError
        _description_
    """
    arr2 = arr2.squeeze()
    ndim1 = arr1.ndim
    ndim2 = arr2.ndim
    # sh1 = arr1.shape
    sh1 = list(arr1.shape)
    sh2 = np.array(arr2.shape, dtype=int)
    if ndim2 > ndim1:
        raise ValueError(
            "arr2 cannot have more dimensions than arr1 under this assumption"
        )

    # Prepend singleton dims to arr2 to match arr1's ndim
    shape2_adj = np.ones(ndim1, dtype=int)  # + arr2.shape
    i_shape2 = []
    i_of = 0
    # The loop is required for cases when two axes have the same length
    for s in sh2:
        i_shape2 += [sh1.index(s) + i_of]
        sh1.pop(sh1.index(s))
        i_of += 1
    shape2_adj[i_shape2] = sh2
    arr2_broadcastable = arr2.reshape(tuple(shape2_adj))
    return arr1, arr2_broadcastable


## Misc
thr_window = lambda X, alpha=0.4: X * (X > X.max() * alpha)
in_circle = lambda x, y, xc, yc, rc: (x - xc) ** 2 + (y - yc) ** 2 < rc**2
in_bbox = lambda y, z, bbox: y > bbox[1] and y < bbox[4] and z > bbox[2] and z < bbox[3]


def iterable_gen(obj, include_none=True, include_unitary=True):
    it_ = np.iterable(obj) or (obj is None and include_none)
    if np.iterable(obj):
        it_ = len(obj) > 1 or include_unitary
    return it_


def split_job_from_arrays(len_arrays, n_split, stype="default"):
    """
    Split an array for parallel independant computing, by sharing independant sub-spaces \
    of array index

    Parameters
    ----------
    len_arrays  : int
        length of the array containing the full job to perform in parallel
    stype       : str
        method used to split the array:
            "comb": 

    Returns
    -------
    mask    : np.array
        subspace of the array indexes, specific to each instantiation of the programm
    """
    mask = np.arange(len_arrays)

    if stype == "comb":
        mask = [
            list(np.where(i_split == mask % n_split)[0]) for i_split in range(n_split)
        ]
    else:
        mask = np.array_split(mask, n_split, axis=0)
        mask = [list(m) for m in mask]
    return mask


def rotate_axes(arr: np.ndarray, axis: int, target=0) -> np.ndarray:
    """_summary_

    Parameters
    ----------
    arr : np.ndarray
        _description_
    axis : int
        _description_
    target : int, optional
        _description_, by default 0

    Returns
    -------
    np.ndarray
        _description_

    Example
    -------
    >>> a = np.ones((3,6,4,7))
    >>> a.shape
    (3, 6, 4, 7)
    >>> rotate_axes(a, axis=2).shape
    (4, 3, 6, 7)
    >>> rotate_axes(a, axis=2, target=-1).shape
    (3, 6, 7, 4)
    >>> rotate_axes(a, axis=1, target=-1).shape
    (3, 4, 7, 6)
    """
    if axis < 0:
        axis = arr.ndim + axis
    if target < 0:
        target = arr.ndim + target
    step = 1
    if target > axis:
        step = -1
    for i_ax in range(target, axis, step):
        arr = arr.swapaxes(i_ax, axis)
    return arr


def plot_array(
    ax: plt.Axes, x: np.ndarray, arr: np.ndarray, axis: int | None = None, **kwgs
):
    if arr.ndim == 1:
        if len(x) != len(arr):
            raise ValueError(
                f"Dimension mismatch (x:{len(x)}, arr:{len(arr)}), array cannot be ploted"
            )
            return None
        ax.plot(x, arr, **kwgs)
    else:
        if axis is not None:
            if len(x) != arr.shape[axis]:
                raise ValueError(
                    f"Dimension mismatch (x:{len(x)}, arr:{arr.shape[axis]}), array cannot be ploted"
                )
        else:
            for a in range(arr.ndim):
                if len(x) == arr.shape[a]:
                    axis = a
            if axis is None:
                raise ValueError(
                    f"No matching dim, (x:{len(x)}, arr:{arr.shape}), array cannot be ploted"
                )
        arr = rotate_axes(arr, axis=axis, target=-1)
        for sub_arr in arr:
            plot_array(ax, x=x, arr=sub_arr, axis=-1, **kwgs)


## Nerve conductivities methods
def compute_myelin_ppt(d, model="MRG", f=0):
    """
    Extract the apparent conductivity of the myelin sheath for a given axon diameter.

    Parameters
    ----------
    d : float
        Axon diameter in micrometers (µm).
    model : str, optional
        Model used for parameter extraction. Default is "MRG".
    f : float, optional
        Frequency in kilohertz (kHz). If greater than 0, the capacitive effect is included. Default is 0.

    Returns
    -------
    sig_mye : complex or float
        Apparent myelin conductivity in S/m². If frequency is specified, returns a complex value.
    """

    g, axonD, nodeD, paraD1, paraD2, deltax, paralength2, nl = get_MRG_parameters(d)
    mycm = 0.1  # uF/cm2/lamella membrane
    mygm = 0.001  # S/cm2/lamella membrane

    r_m = convert(d / 2, unitin="um", unitout="m")
    mygm_S_m = convert(mygm, unitin="S/cm**2", unitout="S/m**2")

    sig_mye = r_m * mygm_S_m / nl
    if f > 0:
        mycm_F_m = convert(mycm, unitin="uF/cm**2", unitout="F/m**2")
        f_hz = convert(f, unitin="kHz", unitout="Hz")
        sig_mye = sig_mye + 2j * np.pi * f_hz * r_m * mycm_F_m / nl
    return sig_mye


def compute_y_wth_uv(y: np.ndarray, R_x: np.ndarray) -> tuple[np.ndarray]:
    """
    Computes the equivalent admittance array using the provided admittance values `y` and resistance values `R_x`.
    The function performs a calculation involving the transformation of admittance to impedance, then iteratively
    computes two intermediate variables `u` and `v` for each element, which are used to determine the equivalent
    admittance for each position in the input array.

    Parameters
    ----------
    y : np.ndarray
        Array of admittance values.
    R_x : np.ndarray
        Array of resistance values. If not iterable, it is broadcasted to match the length of `y`.
    Returns
    -------
    np.ndarray
        Array of computed equivalent admittance values for each position.
    """

    z = 1 / y
    n_x = len(z)
    if not np.iterable(R_x):
        R_x *= np.ones(n_x)
    z_eq = np.zeros(n_x)

    u = np.zeros(n_x)
    v = np.zeros(n_x)
    u[0], v[0] = z[0] * 2, z[-1] * 2
    z_n = deepcopy(z)
    # TODO: find a way to do this with one loop
    for n in range(n_x):
        # z_n[k] := |z[k] for k=!n
        #           |2*z[k] for k==n
        z_n[n] = 2 * z_n[n]
        u_n = z_n[0]
        if n >= 1:
            for k in range(1, n):
                # print(k)
                u_n = z_n[k] * (R_x[k] + u_n) / (z_n[k] + R_x[k] + u_n)
        v_n = z_n[-1]
        if n <= n_x - 1:
            for k in range(1, n_x - n + 1):
                v_n = z_n[-k] * (R_x[-k] + v_n) / (z_n[-k] + R_x[-k] + v_n)
        z_eq[n] = u_n * v_n / (u_n + v_n)
        z_n[n] = z[n]
    return 1 / z_eq


def compute_y_app(
    y: np.ndarray, x_rec: np.ndarray, r_x: np.ndarray
) -> tuple[np.ndarray]:
    """
    Approximates the values of `y` based on the provided `x_rec` and `r_x` arrays.

    For each element in `y`, computes a weighted sum using the formula:
        y_app[n] = sum(y / (1 + abs(x_rec[n] - x_rec) * r_x * y))

    Warning
    -------
    For now the 2D approximation isn't well documented. Further explaination will be added to the doc in the future.

    Parameters
    ----------
    y : np.ndarray
        Input array of values to be approximated.
    x_rec : np.ndarray
        Array of reference x positions.
    r_x : np.ndarray
        Array of scaling factors for each x position.

    Returns
    -------
    y_app : np.ndarray
        Array of approximated values, same length as `y`.
    """

    n_x = len(y)
    y_app = np.zeros(n_x)
    for n in range(n_x):
        kR_x = abs(x_rec[n] - x_rec) * r_x
        y_app[n] = np.sum(y / (1 + kR_x * y))
    return y_app


def compute_mye_sigma_2D(
    sig_m_t: np.ndarray,
    x_rec: np.ndarray,
    sig_mye: float,
    sig_in: float,
    sig_out: float,
    d_ax: float,
    d_node: float,
    alpha_th: float,
    l_elec: float,
) -> float:
    """
    Computes the apparent 2D myelin conductivity (sigma_2d) at a given time for a nerve fiber segment, taking into account the presence of nodes and their properties.

    Warning
    -------
    For now the 2D approximation isn't well documented. Further explaination will be added to the doc in the future.

    Parameters
    ----------
    sig_m_t : np.ndarray
        Array of node membrane conductivities at the given time for various locations.
    x_rec : np.ndarray
        Array of node positions along the fiber.
    sig_mye : float
        Constant myelin conductivity.
    sig_in : float
        Intracellular conductivity.
    sig_out : float
        Extracellular conductivity.
    d_ax : float
        Axon diameter.
    d_node : float
        Node diameter.
    alpha_th : float
        Threshold parameter for conductivity adjustment.
    l_elec : float
        Electrode length.

    Returns
    -------
    sigma_2d : float
        Apparent 2D myelin conductivity for the simulated FEM segment.
    """
    d_node = float(sci_round(d_node, 5))
    n_nodes = len(x_rec)
    if n_nodes >= 1:
        sig_nodes = get_sig_ap(sig_in, sig_m_t, alpha_th)
        sig_nodes = get_sig_ap(sig_nodes, sig_out, (d_ax - d_node) / d_ax)
        sig_nodes_2d = np.mean(sig_nodes)
        frac_l_node = n_nodes / l_elec
        sigma_2d = frac_l_node * sig_nodes_2d + (1 - frac_l_node) * sig_mye
    else:
        sigma_2d = sig_mye
    return sigma_2d


def compute_sigma_2D(
    Y_m_t: np.ndarray,
    x_rec: np.ndarray,
    sig_in: float,
    sig_out: float,
    d_ax: np.ndarray,
    th_mem: float,
    l_elec: float,
    method="",
) -> float:
    """
    Computes the apparent 2D conductivity (sigma_2D) at a given time of a membrane using admittance measurements and geometric parameters.

    Parameters
    ----------
    Y_m_t : np.ndarray
        Array of node membrane conductivities at the given time for various locations.
    x_rec : np.ndarray
        Array of spatial positions (in micrometers) along the recording axis.
    sig_in : float
        Conductivity inside the membrane.
    sig_out : float
        Conductivity outside the membrane.
    d_ax : np.ndarray
        Array of membrane diameters (in micrometers).
    th_mem : float
        Membrane thickness (in meters).
    l_elec : float
        Electrode length (in micrometers).
    method : str, optional
        Method for computing admittance normalization. If contains "approx", uses an approximate method.

    Returns
    -------
    sigma_2d : float
        The computed 2D conductivity of the membrane.
    """
    x_rec_m = convert(x_rec, unitin="um", unitout="m")
    d_ax_m = convert(d_ax, unitin="um", unitout="m")
    l_elec_m = convert(l_elec, unitin="um", unitout="m")
    dx = np.diff(x_rec_m)
    dx = np.append(dx, dx[0])
    Y_mem_x = Y_m_t * np.pi * d_ax_m * dx / th_mem
    r_x = 1 / sig_out + 1 / sig_in
    if "approx" in method:
        # print("hello app", method)
        Y_mem_n = compute_y_app(y=Y_mem_x, x_rec=x_rec_m, r_x=r_x)
    else:
        # print("hello ex", method)
        R_x = r_x * dx
        Y_mem_n = compute_y_wth_uv(y=Y_mem_x, R_x=R_x)
    l_fem = x_rec[-1]
    e_mask = np.argwhere(
        (x_rec > (l_fem - l_elec) / 2) & (x_rec < (l_fem + l_elec) / 2)
    )
    sigma_2d = np.mean(Y_mem_n[e_mask]) * th_mem / (np.pi * d_ax_m * l_elec_m)
    # print(dx[0], Y_mem_x[0], sigma_2d)
    return sigma_2d


def compute_sigma_2D_old(
    Y_m_t: np.ndarray, x_rec: np.ndarray, sig_in: float, sig_out: float, l_elec: float
) -> np.ndarray:
    # print("hello old")
    n_x = len(x_rec)
    I = np.arange(n_x)
    Y_m_eq = np.zeros(n_x)
    x_rec_m = convert(x_rec, unitin="um", unitout="m")
    # dx = np.diff(x_rec)[0]
    r_x = 1 / sig_out + 1 / sig_in
    for n in range(n_x):
        G_n = abs(x_rec_m[n] - x_rec_m) * r_x
        Y_m_eq[n] = np.sum(Y_m_t / (1 + G_n * Y_m_t)) / n_x
    Y_ = np.mean(Y_m_eq)
    return Y_


def sum_sigma_ax(results: nerve_results) -> np.ndarray:
    """
    Computes the sum of the mean membrane conductivity across all axons in the given nerve results.

    Parameters
    ----------
    results : nerve_results
        An object containing the results of nerve simulations, including axon population properties and methods to retrieve individual axon results.

    Returns
    -------
    np.ndarray
        The summed mean membrane conductivity across all axons, as a NumPy array.
    """

    _axons_pop_ppts = results.axons_pop_properties
    sy_mem_t = None
    for i_ax in range(results.n_ax):
        _ax_ppts = _axons_pop_ppts[i_ax, :]
        ax_res = results.get_axon_results(_ax_ppts[0], _ax_ppts[1])
        if sy_mem_t is None:
            sy_mem_t = np.mean(ax_res.get_membrane_conductivity(), axis=0)
        else:
            sy_mem_t += np.mean(ax_res.get_membrane_conductivity(), axis=0)
    return sy_mem_t


## Additionnal On the flight posporoc functions
def sample_keys_mdt(
    results: axon_results,
    keys_to_sample: str | set[str] = {},
    sample_dt: list | None | float = None,
    t_start_rec: float = 0,
    t_stop_rec: float = -1,
    i_sampled_t: None | np.ndarray = None,
    x_bounds: None | float | tuple[float] = None,
    keys_to_remove: str | set[str] = set(),
    keys_to_keep: set[str] = set(),
) -> axon_results:
    """
    extension of sample_key axon postproc function from nrv allowing to simply set an addaptative dt

    Note
    ----
    sample_dt shloud be a list of `tuple` each containing a value of dt (`dt_seg`) and a time (`t_swich`) at which the dt should switch to the next with the following formalism: (t_swich, dt_seg)

    The last t_swich value should be -1 to be set to t_stop_rec



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
    """
    results.is_recruited()
    keys_to_keep = keys_to_keep.union({"recruited"})

    if not np.iterable(sample_dt):
        return sample_keys(
            results=results,
            keys_to_sample=keys_to_sample,
            t_start_rec=t_start_rec,
            t_stop_rec=t_stop_rec,
            sample_dt=sample_dt,
            i_sampled_t=i_sampled_t,
            x_bounds=x_bounds,
            keys_to_remove=keys_to_remove,
            keys_to_keep=keys_to_keep,
        )
    if t_stop_rec < 0:
        i_t_max = len(results["t"])
    else:
        i_t_max = np.argwhere(results["t"] <= t_stop_rec)[-1][0]
    i_t_min = np.argwhere(results["t"] >= t_start_rec)[0][0]
    t_APs = []
    i_t_start = i_t_min
    for t_switch, cur_dt in sample_dt:
        if t_switch > 0:
            i_switch_dt = np.argwhere(results["t"] <= t_switch)[-1][0]
        else:
            i_switch_dt = i_t_max
        t_APs += [k for k in range(i_t_start, i_switch_dt, int(cur_dt / results.dt))]
        i_t_start = deepcopy(i_switch_dt)

    i_sampled_t = np.array(t_APs)
    return sample_keys(
        results=results,
        keys_to_sample=keys_to_sample,
        t_start_rec=t_start_rec,
        t_stop_rec=t_stop_rec,
        sample_dt=None,
        i_sampled_t=i_sampled_t,
        x_bounds=x_bounds,
        keys_to_remove=keys_to_remove,
        keys_to_keep=keys_to_keep,
    )


def get_samples_index(
    results: nerve_results,
    n_pts: int,
    alpha: float = 0.001,
    t_iclamp: float = 1,
    d_iclamp: float = 0.2,
    n_pts_min=None,
) -> np.ndarray:
    """
    Selects sample indices from nerve simulation results to achieve adaptative sampling along the arc length of the signal.

    Note
    ----
    For now, the sampling indexes are computed from the analytical recorder's variation, i.e. proximity between indexes is proportionnal to the time derivative of the recoeder's values.

    Warning
    -------
    In future version, the previous note might be extended to the global variation of conductivity in axons' membrane in the nerve (instead of only analytical recorder).


    Parameters
    ----------
    results : nerve_results
        The results object containing simulation recordings and time points.
    n_pts : int
        The desired number of sample points.
    alpha : float, optional
        Regularization parameter for arc length calculation (default is 0.001).
    t_iclamp : float, optional
        Start time of the current clamp artifact to be removed (default is 1).
    d_iclamp : float, optional
        Duration of the current clamp artifact to be removed (default is 0.2).
    n_pts_min : int, optional
        Minimum number of sample points to return. If not specified, defaults to `n_pts`.

    Returns
    -------
    np.ndarray
        Array of indices corresponding to selected sample points, distributed homogeneously along the arc length of the signal.

    Note
    ----
    - Removes the effect of current clamp artifact from the signal before sampling.
    """

    # TODO: From sum of gmem instead of recorder
    if "recorder" in results:
        if n_pts_min is None:
            n_pts_min = n_pts
        t = np.array(results.recorder.t)
        t_sim = t[-1]
        dt = t[1] - t[0]
        v = np.array(results.recorder.recording_points[0].recording)
        # removing change due to iclamp
        v[int(t_iclamp / dt) : int((t_iclamp + d_iclamp + 0.01) / dt)] *= 0
        # v = sum_sigma_ax(results)
        # plt.plot(t, v)
        # plt.savefig("test.png")
        # Normalize axes
        norm_dt = dt / t_sim
        norm_v = abs(v)
        norm_v /= max(norm_v)

        #
        dv = np.diff(v, prepend=v[0])
        drec_dt = (dv**2 + (alpha * norm_dt) ** 2) ** 0.5
        Sdv_dt = np.cumsum(drec_dt)
        lenght_arc = Sdv_dt[-1]
        length_sample = lenght_arc / (n_pts - 1)

        # Sample homogeneously along arc length
        i_t_samples = np.array(
            [np.argmin(abs(Sdv_dt - (k * length_sample))) for k in range(n_pts)]
        )

        # Remove repeted indexes
        ok_mask = np.append(np.diff(i_t_samples) != 0, [True])
        i_t_samples = i_t_samples[ok_mask]
        if len(i_t_samples) < n_pts_min:
            i_t_samples = get_samples_index(
                results=results,
                n_pts=n_pts + 1,
                alpha=alpha,
                t_iclamp=t_iclamp,
                d_iclamp=d_iclamp,
                n_pts_min=n_pts_min,
            )
        return i_t_samples


def sample_nerve_results(
    results: nerve_results,
    n_pts: int,
    alpha: float = 0.001,
    t_iclamp: float = 1,
    d_iclamp: float = 0.2,
    keys_to_sample="g_mem",
) -> nerve_results:
    """
    Samples specific keys from nerve simulation results at selected time points.

    Note
    ----
    By contrast with the :func:`sample_keys`-function, this one must be call after the nerve simulation on the whole :class:`nerve_results`.

    Parameters
    ----------
    results : nerve_results
        The nerve simulation results object containing axon population properties and results.
    n_pts : int
        Number of time points to sample from the results.
    alpha : float, optional
        Threshold parameter used for sample index selection (default is 0.001).
    t_iclamp : float, optional
        Time of current clamp onset in milliseconds (default is 1).
    d_iclamp : float, optional
        Duration of current clamp in milliseconds (default is 0.2).
    keys_to_sample : str or list of str, optional
        Keys of the results to sample (default is "g_mem").

    Returns
    -------
    nerve_results
        The updated nerve_results object with sampled keys at selected time points.

    Note
    ----
    This function modifies the input `results` object in place by sampling the specified keys for each axon at the selected time indices.
    """
    import pandas as pd

    i_t_fem = get_samples_index(
        results, n_pts, alpha=alpha, d_iclamp=d_iclamp, t_iclamp=t_iclamp
    )
    _axons_pop_ppts: pd.DataFrame = results.axons
    for i_ax in _axons_pop_ppts.index:
        _ax_ppts = _axons_pop_ppts.loc[i_ax]
        ax_res = results[_ax_ppts["fkey"]][_ax_ppts["akey"]]
        ax_res = sample_keys(ax_res, keys_to_sample=keys_to_sample, i_sampled_t=i_t_fem)
    return results


## Post-processing


def compute_v_rec_cap_idxs(
    Voltage, dt, t_stim=0, stim_duration=0.2, tol=0.05, use_filter=True
):
    i_offset_stim = int((t_stim + stim_duration) / dt) + 1
    _v_rec_nrm = Voltage[i_offset_stim:].copy()
    _v_rec_nrm /= -_v_rec_nrm.min()
    i_t_m = np.argwhere(_v_rec_nrm < -tol).squeeze()
    if len(i_t_m) == 0:
        print("No mylinated cap detected")
        i_cap_m = 0, 0, 0, 0
    else:
        di_t_m = np.diff(i_t_m[:-1], prepend=-1, append=0)

        i_cut = np.squeeze(np.where(di_t_m != 1)) - 1
        if not np.iterable(i_cut):
            i_start_m, i_stop_m = i_t_m[0], i_t_m[i_cut]
        else:
            if i_cut[0] != 0:
                i_start_m, i_stop_m = i_t_m[0], i_t_m[i_cut[0]]
            else:
                i_start_m, i_stop_m = i_t_m[i_cut[:2]]
        i_start_m += i_offset_stim
        i_stop_m += i_offset_stim
        i_t_min, i_t_max = (
            np.argmin(Voltage[i_start_m:i_stop_m]) + i_start_m,
            np.argmax(Voltage[i_start_m:i_stop_m]) + i_start_m,
        )
        i_cap_m = i_start_m, i_t_min, i_t_max, i_stop_m

    i_start = max(i_cap_m[-1], i_offset_stim)
    i_start += np.argwhere(Voltage[i_cap_m[-1] :] > 0)[0][0]
    dv_rec_dt = np.diff(Voltage[i_start:])
    if use_filter:
        dv_rec_dt = savgol_filter(dv_rec_dt, 1000, 3)
        dv_rec_dt /= np.max(abs(dv_rec_dt))
    else:
        dv_rec_dt /= np.max(abs(dv_rec_dt))
    i_t_u = np.argwhere(dv_rec_dt > 0.1).squeeze() + i_start
    i_t_start, i_t_stop = i_t_u[0], i_t_u[-1]
    i_t_min, i_t_max = (
        np.argmin(Voltage[i_t_start:i_t_stop]) + i_t_start,
        np.argmax(Voltage[i_t_start:i_t_stop]) + i_t_start,
    )
    i_cap_u = i_t_start, i_t_min, i_t_max, i_t_stop
    return i_cap_m, i_cap_u
