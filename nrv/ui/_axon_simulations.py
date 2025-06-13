"""
NRV-Cellular Level simulations.
"""

import sys
from typing import Callable
from time import perf_counter
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)

from ..backend._file_handler import is_iterable
from ..backend._log_interface import (
    pass_info,
    rise_error,
    rise_warning,
    clear_prompt_line,
)
from ..backend._parameters import parameters
from ..backend._NRV_Mproc import get_pool
from ..fmod._electrodes import *
from ..fmod._extracellular import *
from ..fmod._materials import *
from ..nmod._axons import *
from ..nmod._myelinated import *
from ..nmod._unmyelinated import *
from ..utils._stimulus import *
from ..utils._saving_handler import *
from ._axon_postprocessing import *


def set_args_kwargs(func, args, kwargs):
    return func(*args, **kwargs)


def _call_wrapper(args):
    param, kw, func = args
    return func(param, **kw)


def search_threshold_dispatcher(
    search_func: Callable, parameter_list: list[any], ncore: int = None, **kwargs
) -> list[any]:
    """
    Automatically dispatches any search threshold callable object on available cpu cores.

    Parameters
    ----------
    search_func : Callable
        Any callable object that takes as input a value from parameter_list and that returns a threshold
    parameter_list : list[any]
        Lists the values to evaluate the thresholds
    ncore : int, optional
        Fix the number of CPU core count. If None, ncore is set the size of parameter_list. By default None

    Returns
    -------
    list[any]
        List of ordered thresholds.
    """

    total = len(parameter_list)
    if ncore is None:
        ncore = total

    # Split constant kwargs variable ones
    varying_keys = {
        k: v for k, v in kwargs.items() if is_iterable(v) and len(v) == total
    }
    constant_kwargs = {
        k: v for k, v in kwargs.items() if not (is_iterable(v) and len(v) == total)
    }

    call_args = []
    for i in range(total):
        kw = {k: v[i] for k, v in varying_keys.items()}
        kw.update(constant_kwargs)
        call_args.append((parameter_list[i], kw, search_func))

    call_args = []
    for i in range(total):
        kw = {k: v[i] for k, v in varying_keys.items()}
        kw.update(constant_kwargs)
        call_args.append((parameter_list[i], kw, search_func))

    results = []
    # TODO: display individual search output (for each core, see EIT) instead of "processing search"
    with get_pool(n_jobs=ncore, backend="spawn") as pool:
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TextColumn("Processing Search..."),
        ) as progress:
            task = progress.add_task("[cyan]Dispatching...", total=total)
            for result in pool.imap(_call_wrapper, call_args):
                results.append(result)
                progress.update(task, advance=1, refresh=True)
            pool.close()  # LR: Apparently this avoid PETSC Terminate ERROR
            pool.join()  # LR: but this shouldn't be needed as we are in "with"...

    return results


def axon_AP_threshold(
    axon: axon,
    amp_max: float,
    update_func: Callable,
    t_sim: float = 5,
    tol: float = 1,
    t_start=None,
    freq=None,
    verbose: bool = True,
    args_update=None,
    save_path: str | None = None,
    **kwargs,
) -> np.float64:
    """
    Find the activation threshold of an axon with arbitrary stimulation settings.

    Parameters
    ----------
    axon : axon
        axon object to simulation
    amp_max : float
        maximum amplitude for the binary search, in µA
    update_func : Callable
        Callable function to update the axon stimulation parameters between each binary search iteration
    t_sim : float, optional
        Simulation duration, in ms, by default 5
    tol : float, optional
        Search tolerance, in %, by default 1
    verbose : bool, optional
        Verbosity of the search, by default True
    args_update : arg, optional
        update_func arguments, by default None
    save_path : str, optional
        if not none, raster_plot and plot_x_t of axon results are saved in save_path

    Returns
    -------
    current_amp : np.float64
        The threshold found with the binary search.
    """

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = tol

    vm_key = "V_mem"
    if freq is not None:
        vm_key += "_filtered"

    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1
    t_start_cnt = perf_counter()

    while keep_going:
        if verbose and Niter == 1:
            pass_info(f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA ...")

        update_func(axon, current_amp, **args_update)
        verb = parameters.get_nrv_verbosity()
        parameters.set_nrv_verbosity(2)
        results = axon.simulate(t_sim=t_sim)
        parameters.set_nrv_verbosity(verb)

        if freq is not None:
            results.filter_freq("V_mem", freq, Q=2)

        if save_path:
            fig, ax = plt.subplots(1)
            results.raster_plot(ax, key=vm_key)
            ax.set_title(f"Amplitude: {np.round(current_amp,2)}µA")
            amp_str = str(np.round(current_amp, 2)).replace(".", "_")
            fig.tight_layout()
            fig_name = (
                save_path
                + f"raster_plot_axon_{axon.ID}_amp_{amp_str}_uA_iter_{Niter}.png"
            )
            fig.savefig(fig_name)
            plt.close(fig)

            fig, ax = plt.subplots(1)
            results.plot_x_t(ax, key=vm_key)
            ax.set_title(f"Amplitude: {np.round(current_amp,2)}µA")
            fig.tight_layout()
            fig_name = (
                save_path
                + f"vmen_plot_axon_{axon.ID}_amp_{amp_str}_uA_iter_{Niter}.png"
            )
            fig.savefig(fig_name)
            plt.close(fig)

        if verbose:
            clear_prompt_line(1)

        # post-process results
        delta_amp = np.abs(current_amp - previous_amp)
        # put in a function
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                current_tol = 100 * delta_amp / current_amp
            else:
                current_tol = 100 * delta_amp / previous_amp
            if current_tol <= tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if results.is_recruited(vm_key=vm_key, t_start=t_start):
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0
            if verbose:
                pass_info(
                    f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA"
                    + f" ({np.round(current_tol,2)}%)... AP Detected! (in {np.round(results['sim_time'],3)}s)"
                )
                # pass_info("... Spike triggered")
            amplitude_max_th = previous_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0
            if verbose:
                pass_info(
                    f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA"
                    + f" ({np.round(current_tol,2)}%)... AP Not Detected! (in {np.round(results['sim_time'],3)}s)"
                )
            current_amp = amplitude_max_th - delta_amp / 2
            amplitude_min_th = previous_amp

        if previous_amp == amp_max:
            current_amp = amp_min

        Niter += 1
    t_stop = perf_counter()
    if verbose:
        clear_prompt_line(1)
        pass_info(
            f"Activation threshold is {np.round(current_amp,2)}µA ({np.round(current_tol,2)}%),"
            + f" found in {Niter-1} iterations ({np.round(t_stop-t_start_cnt,2)}s)."
        )
    return current_amp


def axon_block_threshold(
    axon: axon,
    amp_max: float,
    update_func: Callable,
    AP_start: float,
    t_sim: float = 10,
    tol: float = 1,
    freq: float | None = None,
    verbose: bool = True,
    args_update=dict | None,
    save_path: str | None = None,
    **kwargs,
) -> np.float64:
    """
    Find the block threshold of an axon with arbitrary stimulation settings.

    Parameters
    ----------
    axon : axon
        axon object to simulation
    amp_max : float
        maximum amplitude for the binary search, in µA
    update_func : Callable
        Callable object to update the axon stimulation parameters between each binary search iteration
    AP_start : float
            timestamp of the test pulse start, in ms.
    t_sim : float, optional
        Simulation duration, in ms, by default 5
    tol : float, optional
        Search tolerance, in %, by default 1
    freq : float, optional
            Frequency of the stimulation, for KES block, by default None
    verbose : bool, optional
        Verbosity of the search, by default True
    args_update : arg, optional
        update_func arguments, by default None
    save_path : str, optional
        if not none, raster_plot and plot_x_t of axon results are saved in save_path

    Returns
    -------
    current_amp : np.float64
        The block threshold found with the binary search.
    """

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = tol

    vm_key = "V_mem"
    if freq is not None:
        vm_key += "_filtered"

    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1
    t_start_cnt = perf_counter()

    while keep_going:
        if verbose and Niter == 1:
            pass_info(f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA ...")

        update_func(axon, current_amp, **args_update)

        verb = parameters.get_nrv_verbosity()
        # parameters.set_nrv_verbosity(2)
        results = axon.simulate(t_sim=t_sim)
        # parameters.set_nrv_verbosity(verb)

        is_blocked = results.is_blocked(AP_start=AP_start, freq=freq)
        if save_path:
            fig, ax = plt.subplots(1)
            results.raster_plot(ax, key=vm_key)
            ax.set_title(f"Block Amplitude: {np.round(current_amp,2)}µA")
            amp_str = str(np.round(current_amp, 2)).replace(".", "_")
            fig.tight_layout()
            fig_name = (
                save_path
                + f"raster_plot_axon_{axon.ID}_amp_{amp_str}_uA_iter_{Niter}.png"
            )
            fig.savefig(fig_name)
            plt.close(fig)

            fig, ax = plt.subplots(1)
            results.plot_x_t(ax, key=vm_key)
            ax.set_title(f"Block Amplitude: {np.round(current_amp,2)}µA")
            fig.tight_layout()
            fig_name = (
                save_path
                + f"vmen_plot_axon_{axon.ID}_amp_{amp_str}_uA_iter_{Niter}.png"
            )
            fig.savefig(fig_name)
            plt.close(fig)

        if verbose:
            clear_prompt_line(1)

        # post-process results
        delta_amp = np.abs(current_amp - previous_amp)
        # put in a function
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                current_tol = 100 * delta_amp / current_amp
            else:
                current_tol = 100 * delta_amp / previous_amp
            if current_tol <= tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if is_blocked is None:
            rise_warning(
                "Failed to evaluate block state of the axon! Consider changing the simulation parameters."
            )
            return 0.0

        if is_blocked:
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0.0
            if verbose:
                pass_info(
                    f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA"
                    + f" ({np.round(current_tol,2)}%)... AP Blocked! (in {np.round(results['sim_time'],3)}s)"
                )
                # pass_info("... Spike triggered")
            amplitude_max_th = previous_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0.0
            if verbose:
                pass_info(
                    f"Iteration {Niter}, Amp is {np.round(current_amp,2)}µA"
                    + f" ({np.round(current_tol,2)}%)... AP Not Blocked! (in {np.round(results['sim_time'],3)}s)"
                )
            current_amp = amplitude_max_th - delta_amp / 2
            amplitude_min_th = previous_amp

        if previous_amp == amp_max:
            current_amp = amp_min

        Niter += 1
    t_stop = perf_counter()
    if verbose:
        clear_prompt_line(1)
        pass_info(
            f"Block threshold is {np.round(current_amp,2)}µA ({np.round(current_tol,2)}%),"
            + f" found in {Niter-1} iterations ({np.round(t_stop-t_start_cnt,2)}s)."
        )
    return current_amp


def firing_threshold_point_source(
    diameter,
    L,
    dist_elec,
    cath_time=100e-3,
    model="MRG",
    amp_max=2000,
    amp_tol=1,
    dt=0.005,
    verbose=True,
    **kwargs,
):
    """
    Find the firing threshold with point source approximation using binary search.

    Parameters
    ----------
    diameter        : float
            axon diameter in um
    L               : float
            axon length in um
    dist_elec       : float
            y coordinate of the point source electrode in um
    cath_time      : float
            cathodic pulse width in ms
    model           : str
            Axon model
    amp_max         : float
            Maximum tested blocking amplitude for the binary search in uA
    amp_tol         : float
            Threshold tolerance in % for the binary search
    dt              : float
        Set the dt to a specific value in ms
    verbose         : bool
            set the verbosity of the search
    **kwargs:
            See below

    Keyword Arguments:
            material       :   str
                    material used to compute the extracellular field
            position_elect : float
                    x location of the electrode, between 0 and 1
            z_elect        : float
                    z coordinate of the electrode
            amp_min        : float
                    minimum amplitude for the binary search
            f_dlambda      : float
                    To set the number of segment with the d_dlambda rule (Hz)
            t_sim          : float
                    Duration of the simulation in ms
            amp_tol_abs    : float
                    Specify an absolute amplitude tolerance for the binary search
                    in uA
            anod_first  : bool
                    Set the anodic phase before the cathodic phase
            t_inter : float
                    Specify the interphase delay in ms
            cath_an_ratio: float
                    Specify the cathodic/anodic ratio
            dt              : float
                    Set the dt to a specific value in ms
            cath_an_ratio          : float
                    Set the tolorance for dt in %
            nseg            : int
                    Set the number of segment for the axon
            amp_tol_abs     : float
                    Set the absolute tolerance for the binary search in uA.
            node_shift      : float between -1 and 1
                    Align electrode with Node of Ranvier. When Shift = 0, Electrode is aligned with node
            n_nodes         : integer
                    Specify the number of Node of Ranvier for myelinated models. Overwrite L when specified.

    Returns
    -------
    threshold       : float
            estimated firing threshold in uA
    """

    rise_warning(
        "DeprecationWarning: ",
        "firing_threshold_point_source is obsolete use axon_AP_threshold instead",
    )

    if "t_sim" in kwargs:
        t_sim = kwargs.get("t_sim")
    else:
        if model in myelinated_models:
            t_sim = 5
        else:
            t_sim = 20

    if "material" in kwargs:
        material = kwargs.get("material")
    else:
        material = material = "endoneurium_bhadra"

    if "anod_first" in kwargs:
        anod_first = kwargs.get("anod_first")
    else:
        anod_first = False

    if "t_inter" in kwargs:
        t_inter = kwargs.get("t_inter")
    else:
        t_inter = 0

    if "cath_an_ratio" in kwargs:
        cath_an_ratio = kwargs.get("cath_an_ratio")
    else:
        cath_an_ratio = 1

    if "position_elec" in kwargs:
        position_elec = kwargs.get("position_elec")
    else:
        position_elec = 0.5

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    if "f_dlambda" in kwargs:
        f_dlambda = kwargs.get("f_dlambda")
    else:
        f_dlambda = 0

    if "nseg" in kwargs:
        nseg = kwargs.get("nseg")
    else:
        nseg = 0

    if "Nseg_per_sec" in kwargs:
        Nseg_per_sec = kwargs.get("Nseg_per_sec")
    else:
        Nseg_per_sec = 0

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    if "node_shift" in kwargs:
        node_shift = kwargs.get("node_shift")
    else:
        node_shift = 0

    if "n_nodes" in kwargs:
        n_nodes = kwargs.get("n_nodes")
    else:
        n_nodes = 0

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol
    # axon
    y = 0
    z = 0

    # extra cellular
    extra_material = load_material(material)
    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1
    while keep_going:
        if verbose:
            pass_info(
                "Iteration number "
                + str(Niter)
                + ", testing firing current amplitude "
                + str(current_amp)
                + " uA"
            )
        # create axon
        if model in unmyelinated_models:
            if Nseg_per_sec:
                axon1 = unmyelinated(
                    y, z, diameter, L, dt=dt, model=model, Nseg_per_sec=Nseg_per_sec
                )  # freq=f_dlambda
            else:
                axon1 = unmyelinated(
                    y, z, diameter, L, dt=dt, freq=f_dlambda, model=model
                )
        elif model in myelinated_models:
            if n_nodes > 0:
                L = get_length_from_nodes(diameter, n_nodes)
            if Nseg_per_sec:
                axon1 = myelinated(
                    y,
                    z,
                    diameter,
                    L,
                    rec="nodes",
                    dt=dt,
                    model=model,
                    Nseg_per_sec=Nseg_per_sec,
                )  # freq=f_dlambda
            else:
                axon1 = myelinated(
                    y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
                )
        else:
            rise_error("Error: Specified model is not recognized.")
        # extra-cellular stimulation
        x_elec = L * position_elec
        if model in myelinated_models:  # Align electrode with node of Ranvier
            n_nodes = len(axon1.x_nodes)
            nearest_node = np.int32(np.round(position_elec * n_nodes))
            x_elec = axon1.x_nodes[nearest_node]
            if node_shift != 0:  # shift it if needed
                if node_shift > 0:
                    if nearest_node < n_nodes - 1:
                        x_next_node = axon1.x_nodes[nearest_node + 1]
                        d_internode = np.abs(x_next_node - x_elec)
                        x_elec = x_elec + d_internode * node_shift
                    else:
                        rise_warning(
                            "Electrode is at the end of the axon and can not be further shifted."
                        )
                else:
                    if nearest_node != 0:
                        x_next_node = axon1.x_nodes[nearest_node + 1]
                        d_internode = np.abs(x_next_node - x_elec)
                        x_elec = x_elec - d_internode * node_shift
                    else:
                        rise_warning(
                            "Electrode is at the end of the axon and can not be further shifted."
                        )

        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec, y_elec, z_elec)

        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        if cath_an_ratio > 0:
            I_anod = I_cathod / cath_an_ratio

            stim_1.biphasic_pulse(
                start, I_cathod, cath_time, I_anod, t_inter, anod_first=anod_first
            )
        else:
            stim_1.biphasic_pulse(
                start, I_cathod, cath_time, 0, 0, anod_first=anod_first
            )

        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1, stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=t_sim)
        del axon1
        if verbose:
            pass_info(
                "... Iteration simulation performed in "
                + str(results["sim_time"])
                + " s"
            )
        # post-process results
        delta_amp = np.abs(current_amp - previous_amp)
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                tol = 100 * delta_amp / current_amp
            else:
                tol = 100 * delta_amp / previous_amp
            if tol <= amp_tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if results.is_recruited("V_mem"):
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0
            if verbose:
                pass_info("... Spike triggered")
            amplitude_max_th = previous_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0
            if verbose:
                pass_info("... Spike not triggered")
            current_amp = amplitude_max_th - delta_amp / 2
            amplitude_min_th = previous_amp

        if previous_amp == amp_max:
            current_amp = amp_min

        Niter += 1
    return current_amp


def firing_threshold_from_axon(
    axon, cath_time=100e-3, amp_max=2000, amp_tol=1, verbose=True, **kwargs
):
    """
    Find the firing threshold from a specified axon using binary search

    Parameters
    ----------
    axon        : axon class
            axon class
    cath_time      : float
            cathodic pulse width in ms
    amp_max         : float
            Maximum tested blocking amplitude for the binary search in uA
    amp_tol         : float
            Threshold tolerance in % for the binary search
    verbose         : bool
            set the verbosity of the search
    **kwargs:
            See below

    Keyword Arguments:
    elec_id        : int
            elec_id where to change stimulus
    amp_min        : float
            minimum amplitude for the binary search
    t_sim          : float
            Duration of the simulation in ms
    amp_tol_abs    : float
            Specify an absolute amplitude tolerance for the binary search
            in uA
    anod_first  : bool
            Set the anodic phase before the cathodic phase
    t_inter : float
            Specify the interphase delay in ms
    cath_an_ratio: float
            Specify the cathodic/anodic ratio
    cath_an_ratio          : float
            Set the tolorance for dt in %
    amp_tol_abs     : float
            Set the absolute tolerance for the binary search in uA.

    Returns
    -------
    threshold       : float
            estimated firing threshold in uA
    """

    rise_warning(
        "DeprecationWarning: ",
        "firing_threshold_point_source is obsolete use axon_AP_threshold instead",
    )

    if "elec_id" in kwargs:
        elec_id = kwargs.get("elec_id")
    else:
        elec_id = 0

    if "t_sim" in kwargs:
        t_sim = kwargs.get("t_sim")
    else:
        t_sim = 10

    if "anod_first" in kwargs:
        anod_first = kwargs.get("anod_first")
    else:
        anod_first = False

    if "t_inter" in kwargs:
        t_inter = kwargs.get("t_inter")
    else:
        t_inter = 0

    if "cath_an_ratio" in kwargs:
        cath_an_ratio = kwargs.get("cath_an_ratio")
    else:
        cath_an_ratio = 1

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol

    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1

    # axon.save_axon(save=True, fname='_axon.json', extracel_context=True)
    # del (axon)
    while keep_going:
        if verbose:
            pass_info(
                "Iteration number "
                + str(Niter)
                + ", testing firing current amplitude "
                + str(current_amp)
                + " uA"
            )

        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        # I_cathod =
        if cath_an_ratio > 0:
            I_anod = I_cathod / cath_an_ratio
            stim_1.biphasic_pulse(
                start, I_cathod, cath_time, I_anod, t_inter, anod_first=anod_first
            )
        else:
            stim_1.biphasic_pulse(
                start, I_cathod, cath_time, 0, 0, anod_first=anod_first
            )
        # axon_load = load_any_axon(axon, extracel_context=True)
        # axon_th = copy.deepcopy(axon)
        axon.change_stimulus_from_electrode(elec_id, stim_1)

        # simulate axon activity
        results = axon.simulate(t_sim=t_sim, loaded_footprints=True)
        # del (axon)
        if verbose:
            pass_info(
                "... Iteration simulation performed in "
                + str(results["sim_time"])
                + " s"
            )
        # post-process results

        delta_amp = np.abs(current_amp - previous_amp)
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                tol = 100 * delta_amp / current_amp
            else:
                tol = 100 * delta_amp / previous_amp
            if tol <= amp_tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if results.is_recruited("V_mem"):
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0
            if verbose:
                pass_info("... Spike triggered")
            amplitude_max_th = previous_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0
            if verbose:
                pass_info("... Spike not triggered")
            current_amp = amplitude_max_th - delta_amp / 2
            amplitude_min_th = previous_amp

        if previous_amp == amp_max:
            current_amp = amp_min

        Niter += 1
    del axon
    return current_amp


def blocking_threshold_point_source(
    diameter,
    L,
    dist_elec,
    block_freq,
    model="MRG",
    amp_max=2000,
    amp_tol=1,
    dt=0.005,
    Nseg_per_sec=2,
    verbose=True,
    **kwargs,
):
    """
    Find the blocking threshold with point source approximation using binary search.

    Parameters
    ----------
    diameter        : float
            axon diameter in um
    L               : float
            axon length in um
    dist_elec       : float
            y coordinate of the point source electrode in um
    block_freq      : float
            Blocking frequency in kHz
    model           : str
            Axon model
    amp_max         : float
            Maximum tested blocking amplitude for the binary search in uA
    amp_tol         : float
            Threshold tolerance in % for the binary search
    dt              : float
            time discretization in ms
    Nseg_per_sec    : int
            Number of segment per section (myelinated axons)
            Number of segment per mm of length (unmyelinated axons)
    verbose         : bool
            set the verbosity of the search

    **kwargs:
            See below

    Keyword Arguments:
            material       :   str
                    material used to compute the extracellular field
            position_elect : float
                    x location of the electrode, between 0 and 1
            z_elect        : float
                    z coordinate of the electrode
            amp_min        : float
                    minimum amplitude for the binary search
            f_dlambda      : float
                    To set the number of segment with the d_dlambda rule (Hz)
            t_sim          : float
                    Duration of the simulation in ms
            amp_tol_abs    : float
                    Specify an absolute amplitude tolerance for the binary search
                    in uA
            t_position     : float
                    Positition on the test electrode.
                    Relative position for unmyelinated axons.
                    Node number for myelinated axons.
            t_start        : float
                    start of the test pulse, in ms
            t_duration     : float
                    duration of the test pulse, in ms
            t_amplitude    : float
                    Amplitude of the test pulse, in nA
            b_start        : float
                    start of the blocking stimulation in ms
            b_duration     : float
                    duration of the blocking stimulation in ms
            node_shift      : float between -1 and 1
                    Align electrode with Node of Ranvier. When Shift = 0, Electrode is aligned with node
            n_nodes         : integer
                    Specify the number of Node of Ranvier for myelinated models. Overwrite L when specified.

    Returns
    -------
    threshold       : float
            estimated threshold in uA
    """

    rise_warning(
        "DeprecationWarning: ",
        "blocking_threshold_point_source is obsolete use axon_block_threshold instead",
    )

    if "material" in kwargs:
        material = kwargs.get("material")
    else:
        material = "endoneurium_bhadra"

    if "position_elec" in kwargs:
        position_elec = kwargs.get("position_elec")
    else:
        position_elec = 0.5

    if "z_elec" in kwargs:
        z_elec = kwargs.get("z_elec")
    else:
        z_elec = 0

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    if "f_dlambda" in kwargs:
        f_dlambda = kwargs.get("f_dlambda")
    else:
        f_dlambda = 100

    if "t_sim" in kwargs:
        t_sim = kwargs.get("t_sim")
    else:
        t_sim = 40

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    if "t_position" in kwargs:
        t_position = kwargs.get("t_position")
    else:
        t_position = 0.05

    if "t_start" in kwargs:
        t_start = kwargs.get("t_start")
    else:
        t_start = 30

    if "t_duration" in kwargs:
        t_duration = kwargs.get("t_duration")
    else:
        t_duration = 1

    if "t_amplitude" in kwargs:
        t_amplitude = kwargs.get("t_amplitude")
    else:
        t_amplitude = 2

    if "b_start" in kwargs:
        b_start = kwargs.get("b_start")
    else:
        b_start = 3

    if "b_duration" in kwargs:
        b_duration = kwargs.get("b_duration")
    else:
        b_duration = t_sim

    if "node_shift" in kwargs:
        node_shift = kwargs.get("node_shift")
    else:
        node_shift = 0

    if "n_nodes" in kwargs:
        n_nodes = kwargs.get("n_nodes")
    else:
        n_nodes = 0

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol

    y = 0
    z = 0

    extra_material = load_material(material)
    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1
    while keep_going:
        if verbose:
            pass_info(
                "Iteration number "
                + str(Niter)
                + ", testing block current amplitude "
                + str(current_amp)
                + " uA"
            )
        # create axon
        if model in unmyelinated_models:
            if Nseg_per_sec:
                axon1 = unmyelinated(
                    y,
                    z,
                    diameter,
                    L,
                    dt=dt,
                    Nseg_per_sec=Nseg_per_sec,
                    Nsec=1,
                    model=model,
                )
            else:
                axon1 = unmyelinated(
                    y, z, diameter, L, dt=dt, freq=f_dlambda, model=model
                )
        elif model in myelinated_models:
            if n_nodes > 0:
                L = get_length_from_nodes(diameter, n_nodes)
            if Nseg_per_sec:
                axon1 = myelinated(
                    y,
                    z,
                    diameter,
                    L,
                    rec="nodes",
                    dt=dt,
                    Nseg_per_sec=Nseg_per_sec,
                    model=model,
                )
            else:
                axon1 = myelinated(
                    y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
                )
        else:
            if n_nodes > 0:
                L = get_length_from_nodes(diameter, n_nodes)
            axon1 = myelinated(
                y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
            )
        # insert test spike
        axon1.insert_I_Clamp(t_position, t_start, t_duration, t_amplitude)
        # extra-cellular stimulation
        x_elec = L * position_elec
        if model in myelinated_models:  # Align electrode with node of Ranvier
            n_nodes = len(axon1.x_nodes)
            nearest_node = np.int32(np.round(position_elec * n_nodes))
            x_elec = axon1.x_nodes[nearest_node]
            if node_shift != 0:  # shift it if needed
                if node_shift > 0:
                    if nearest_node < n_nodes - 1:
                        x_next_node = axon1.x_nodes[nearest_node + 1]
                        d_internode = np.abs(x_next_node - x_elec)
                        x_elec = x_elec + d_internode * node_shift
                    else:
                        rise_warning(
                            "Electrode is at the end of the axon and can not be further shifted."
                        )
                else:
                    if nearest_node != 0:
                        x_next_node = axon1.x_nodes[nearest_node + 1]
                        d_internode = np.abs(x_next_node - x_elec)
                        x_elec = x_elec - d_internode * node_shift
                    else:
                        rise_warning(
                            "Electrode is at the end of the axon and can not be further shifted."
                        )
        y_elec = dist_elec
        z_elec = z_elec
        elec_1 = point_source_electrode(x_elec, y_elec, z_elec)
        stim_1 = stimulus()
        stim_1.sinus(
            b_start, b_duration, current_amp, block_freq, dt=1 / (block_freq * 20)
        )
        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1, stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=t_sim)
        del axon1
        if verbose:
            pass_info(
                "... Iteration simulation performed in "
                + str(results["sim_time"])
                + " s"
            )
        # post-process results
        # filter_freq(results, "V_mem", block_freq)
        # rasterize(results, "V_mem_filtered", threshold=0)
        delta_amp = np.abs(current_amp - previous_amp)
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                tol = 100 * delta_amp / current_amp
            else:
                tol = 100 * delta_amp / previous_amp
            if tol <= amp_tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if results.is_blocked(AP_start=t_start, freq=block_freq) == False:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0
            if verbose:
                pass_info("... Spike not blocked")
            amplitude_min_th = current_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0
            if verbose:
                pass_info("... Spike blocked")
            amplitude_max_th = current_amp
            current_amp = amplitude_max_th - delta_amp / 2

        if previous_amp == amp_max:
            current_amp = amp_min
        Niter += 1
    return current_amp


def blocking_threshold_from_axon(
    axon, block_freq=10, amp_max=2000, amp_tol=1, dt=0.005, verbose=True, **kwargs
):
    """
    Find the blocking threshold with point source approximation using binary search.

    Parameters
    ----------
    axon       : axon
            axon to stimulation
    block_freq      : float
            Blocking frequency in kHz
    amp_max         : float
            Maximum tested blocking amplitude for the binary search in uA
    amp_tol         : float
            Threshold tolerance in % for the binary search
    verbose         : bool
            set the verbosity of the search

    **kwargs:
            See below

    Keyword Arguments:
            amp_min        : float
                    minimum amplitude for the binary search
            t_sim          : float
                    Duration of the simulation in ms
            amp_tol_abs    : float
                    Specify an absolute amplitude tolerance for the binary search
                    in uA
            t_position     : float
                    Positition on the test electrode.
                    Relative position for unmyelinated axons.
                    Node number for myelinated axons.
            t_start        : float
                    start of the test pulse, in ms
            t_duration     : float
                    duration of the test pulse, in ms
            t_amplitude    : float
                    Amplitude of the test pulse, in nA
            b_start        : float
                    start of the blocking stimulation in ms
            b_duration     : float
                    duration of the blocking stimulation in ms

    Returns
    -------
    threshold       : float
            estimated threshold in uA
    """

    rise_warning(
        "DeprecationWarning: ",
        "blocking_threshold_point_source is obsolete use blocking_threshold_from_axon instead",
    )

    if "amp_min" in kwargs:
        amp_min = kwargs.get("amp_min")
    else:
        amp_min = 0

    if "t_sim" in kwargs:
        t_sim = kwargs.get("t_sim")
    else:
        t_sim = 40

    if "amp_tol_abs" in kwargs:
        amp_tol_abs = kwargs.get("amp_tol_abs")
    else:
        amp_tol_abs = 0

    if "t_position" in kwargs:
        t_position = kwargs.get("t_position")
    else:
        t_position = 0.05

    if "t_start" in kwargs:
        t_start = kwargs.get("t_start")
    else:
        t_start = 30

    if "t_duration" in kwargs:
        t_duration = kwargs.get("t_duration")
    else:
        t_duration = 1

    if "t_amplitude" in kwargs:
        t_amplitude = kwargs.get("t_amplitude")
    else:
        t_amplitude = 5

    if "b_start" in kwargs:
        b_start = kwargs.get("b_start")
    else:
        b_start = 3

    if "b_duration" in kwargs:
        b_duration = kwargs.get("b_duration")
    else:
        b_duration = t_sim

    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol

    # Dichotomy initialization
    previous_amp = amp_min
    delta_amp = np.abs(amp_max - amp_min)
    current_amp = amp_max
    Niter = 1
    keep_going = 1
    while keep_going:
        if verbose:
            pass_info(
                "Iteration number "
                + str(Niter)
                + ", testing block current amplitude "
                + str(current_amp)
                + " uA"
            )

        # insert test spike
        axon.insert_I_Clamp(t_position, t_start, t_duration, t_amplitude)
        # extra-cellular stimulation

        stim_1 = stimulus()
        stim_1.sinus(
            b_start, b_duration, current_amp, block_freq, dt=1 / (block_freq * 20)
        )

        axon.change_stimulus_from_electrode(0, stim_1)

        # simulate axon activity
        results = axon.simulate(t_sim=t_sim, loaded_footprints=True)

        if verbose:
            pass_info(
                "... Iteration simulation performed in "
                + str(results["sim_time"])
                + " s"
            )
        # post-process results
        delta_amp = np.abs(current_amp - previous_amp)
        if amp_tol_abs > 0:
            if delta_amp < amp_tol_abs:
                keep_going = 0
            else:
                keep_going = 1
        else:
            if current_amp > previous_amp:
                tol = 100 * delta_amp / current_amp
            else:
                tol = 100 * delta_amp / previous_amp
            if tol <= amp_tol:
                keep_going = 0
            else:
                keep_going = 1
        previous_amp = current_amp
        # test simulation results, update dichotomy
        if results.is_blocked(AP_start=t_start, freq=block_freq) == False:
            if current_amp == amp_max:
                rise_warning("Maximum Stimulation Current is too Low!")
                return 0
            if verbose:
                pass_info("... Spike not blocked")
            amplitude_min_th = current_amp
            current_amp = (delta_amp / 2) + amplitude_min_th
        else:
            if current_amp == amp_min:
                rise_warning("Minimum Stimulation Current is too High!")
                return 0
            if verbose:
                pass_info("... Spike blocked")
            amplitude_max_th = current_amp
            current_amp = amplitude_max_th - delta_amp / 2

        if previous_amp == amp_max:
            current_amp = amp_min
        Niter += 1
    return current_amp
