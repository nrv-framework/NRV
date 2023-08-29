"""
NRV-Cellular Level simulations
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import sys

from ...backend.log_interface import pass_info, rise_error, rise_warning
from ...backend.MCore import *
from ...fmod.electrodes import *
from ...fmod.extracellular import *
from ...fmod.materials import *
from ...fmod.stimulus import *
from ...nmod.axons import *
from ...nmod.myelinated import *
from ...nmod.unmyelinated import *
from ..saving_handler import *
from .CL_discretization import *
from .CL_postprocessing import *

unmyelinated_models = [
    "HH",
    "Rattay_Aberham",
    "Sundt",
    "Tigerholm",
    "Schild_94",
    "Schild_97",
]
myelinated_models = ["MRG", "Gaines_motor", "Gaines_sensory"]


def firing_threshold_point_source(
    diameter,
    L,
    dist_elec,
    cath_time=100e-3,
    model="MRG",
    amp_max=2000,
    amp_tol=1,
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
            nseg_tol        : float
                    Set the nseg tolerance in %
            dt_tol        : float
                    Set the dt tolerance in %
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

    if "dt" in kwargs:
        dt = kwargs.get("dt")
    else:
        dt = 0

    if "dt_tol" in kwargs:
        dt_tol = kwargs.get("dt_tol")
    else:
        dt_tol = amp_tol

    if "nseg" in kwargs:
        nseg = kwargs.get("nseg")
    else:
        nseg = 0

    if "Nseg_per_sec" in kwargs:
        Nseg_per_sec = kwargs.get("Nseg_per_sec")
    else:
        Nseg_per_sec = 0

    if "nseg_tol" in kwargs:
        nseg_tol = kwargs.get("nseg_tol")
    else:
        nseg_tol = amp_tol

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

    if dt == 0:
        if cath_an_ratio > 0 and cath_an_ratio < 1:
            dt = Get_dt(
                dt_tol,
                model,
                simulation_category="Spike_threshold",
                stim_pw=cath_time / cath_an_ratio,
            )
        else:
            dt = Get_dt(
                dt_tol, model, simulation_category="Spike_threshold", stim_pw=cath_time
            )

    if (nseg == 0) and (f_dlambda == 0) and (Nseg_per_sec == 0):
        if model in unmyelinated_models:
            Nseg_per_sec = Get_nseg(
                nseg_tol, model, simulation_category="Spike_threshold", d=diameter, L=L
            )
        else:
            Nseg_per_sec = Get_nseg(
                nseg_tol, model, simulation_category="Spike_threshold"
            )

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
        rasterize(results, "V_mem")
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
        if len(results["V_mem_raster_position"]) > 0:
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
            amp_min        : float
                    minimum amplitude for the binary search
            t_sim          : float
                    Duration of the simulation in ms
            amp_tol_abs    : float
                    Specify an absolute amplitude tolerance for the binary search
                    in uA
            dt             : float
                    Set the dt to a specific value in ms
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
            dt_tol        : float
                    Set the dt tolerance in %

    Returns
    -------
    threshold       : float
            estimated firing threshold in uA
    """

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

    if "dt" in kwargs:
        dt = kwargs.get("dt")
    else:
        dt = 0

    if "dt_tol" in kwargs:
        dt_tol = kwargs.get("dt_tol")
    else:
        dt_tol = amp_tol

    if dt == 0:
        if cath_an_ratio > 0 and cath_an_ratio < 1:
            dt = Get_dt(
                dt_tol,
                axon.model,
                simulation_category="Spike_threshold",
                stim_pw=cath_time / cath_an_ratio,
            )
        else:
            dt = Get_dt(
                dt_tol,
                axon.model,
                simulation_category="Spike_threshold",
                stim_pw=cath_time,
            )

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
        axon.dt = dt
        axon.change_stimulus_from_elecrode(0, stim_1)

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
        rasterize(results, "V_mem")
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
        if len(results["V_mem_raster_position"]) > 0:
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


def para_firing_threshold(
    diameter,
    L,
    material,
    dist_elec,
    cath_first=True,
    cath_time=60e-3,
    t_inter=40e-3,
    cath_an_ratio=5,
    position_elec=0.5,
    model="MRG",
    amp_max=2000,
    amp_min=0,
    amp_tol=1,
    verbose=False,
    f_dlambda=100,
    dt=0.005,
):
    if MCH.is_alone() or MCH.size < 3:
        if MCH.do_master_only_work():
            rise_error(
                "Error: parallel evaluation of a threshold by binary search needs at least 3 parallel processes, but only",
                MCH.size,
                "launched",
            )
        sys.exit(1)
    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol
    # axon
    y = 0
    z = 0
    # extra cellular
    extra_material = load_material(material)
    # Dichotomy initialization
    Niter = 1
    values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size)
    delta_amp = values[-1] - values[0]
    current_amp = (values[-1] - values[0]) / 2
    all_values = values
    while delta_amp > amplitude_tol or Niter == 1:
        # update toledance
        delta_amp = values[1] - values[0]
        # split job
        current_amp = values[MCH.rank]
        # create axon
        if model in unmyelinated_models:
            axon1 = unmyelinated(y, z, diameter, L, dt=dt, freq=f_dlambda, model=model)
        elif model in myelinated_models:
            axon1 = myelinated(
                y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
            )
        else:
            axon1 = myelinated(
                y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
            )
        # extra-cellular stimulation
        x_elec = L * position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec, y_elec, z_elec)

        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        I_anod = I_cathod / cath_an_ratio
        stim_1.biphasic_pulse(
            start, I_cathod, cath_time, I_anod, t_inter, anod_first=(not cath_first)
        )

        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1, stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=5)
        del axon1
        # post-process results
        rasterize(results, "V_mem")
        # test simulation results, gather results to master
        if len(results["V_mem_raster_position"]) > 0:
            spike = np.asarray([True])
        else:
            spike = np.asarray([False])
        all_spikes = MCH.gather_jobs_as_array(spike)
        if MCH.do_master_only_work():
            # add the extrema (False at start, True at the end) already computed at the previous step if Niter > 1
            if Niter > 1:
                all_spikes = np.insert(np.append(all_spikes, True), 0, False)
            # find the zone where the spike appears, update min max
            appear_index = np.argmax(all_spikes == True)
            amplitude_max_th = all_values[appear_index]
            amplitude_min_th = all_values[appear_index - 1]
            # update current amp
            current_amp = amplitude_min_th + (amplitude_max_th - amplitude_min_th) / 2
            # compute new values
            all_values = np.linspace(
                amplitude_min_th, amplitude_max_th, num=MCH.size + 3
            )
            values = all_values[1:-1]
        # share new values
        values = MCH.master_broadcasts_array_to_all(values)
        Niter += 1
    # adapt Niter for correct return
    Niter -= 1
    # share master current amp to all process
    current_amp = MCH.master_broadcasts_array_to_all(current_amp)
    return current_amp, Niter


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
        filter_freq(results, "V_mem", block_freq)
        rasterize(results, "V_mem_filtered", threshold=0)
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
        if block(results, t_start=t_start) == False:
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

        axon.dt = dt
        axon.change_stimulus_from_elecrode(0, stim_1)

        # simulate axon activity
        results = axon.simulate(t_sim=t_sim, loaded_footprints=True)

        if verbose:
            pass_info(
                "... Iteration simulation performed in "
                + str(results["sim_time"])
                + " s"
            )
        # post-process results
        filter_freq(results, "V_mem", block_freq)
        rasterize(results, "V_mem_filtered", threshold=0)
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
        if block(results, t_start=t_start) == False:
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


def para_blocking_threshold(
    diameter,
    L,
    material,
    dist_elec,
    block_freq,
    position_elec=0.5,
    model="MRG",
    amp_max=2000,
    amp_min=0,
    amp_tol=15,
    verbose=True,
    f_dlambda=100,
    dt=0.005,
):
    amplitude_max_th = amp_max
    amplitude_min_th = amp_min
    amplitude_tol = amp_tol
    # axon
    y = 0
    z = 0
    # test spike
    t_start = 20
    duration = 0.1
    amplitude = 3
    # extra cellular
    extra_material = load_material(material)
    block_start = 3  # ms
    block_duration = 20  # ms
    # Dichotomy initialization
    Niter = 1
    values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size)
    delta_amp = values[-1] - values[0]
    current_amp = (values[-1] - values[0]) / 2
    all_values = values
    while delta_amp > amplitude_tol or Niter == 1:
        # update toledance
        delta_amp = values[1] - values[0]
        # split job
        current_amp = values[MCH.rank]
        # create axon
        if model in unmyelinated_models:
            axon1 = unmyelinated(y, z, diameter, L, dt=dt, freq=f_dlambda, model=model)
        elif model in myelinated_models:
            axon1 = myelinated(
                y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
            )
        else:
            axon1 = myelinated(
                y, z, diameter, L, rec="nodes", dt=dt, freq=f_dlambda, model=model
            )
        # insert test spike
        axon1.insert_I_Clamp(0, t_start, duration, amplitude)
        # extra-cellular stimulation
        x_elec = L * position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec, y_elec, z_elec)
        stim_1 = stimulus()
        stim_1.sinus(
            block_start,
            block_duration,
            current_amp,
            block_freq,
            dt=1 / (block_freq * 20),
        )
        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1, stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=25)
        del axon1
        # post-process results
        rasterize(results, "V_mem")

        # test simulation results, gather results to master
        blocked = [block(results)]
        all_blocks = MCH.gather_jobs_as_array(blocked)
        if MCH.do_master_only_work():
            # add the extrema (False at start, True at the end) already computed at the previous step if Niter > 1
            if Niter > 1:
                all_blocks = np.insert(np.append(all_blocks, True), 0, False)
            # find the zone where the blocking appears, update min max
            appear_index = np.argmax(all_blocks == True)
            amplitude_max_th = all_values[appear_index]
            amplitude_min_th = all_values[appear_index - 1]
            # update current amp
            current_amp = amplitude_min_th + (amplitude_max_th - amplitude_min_th) / 2
            # compute new values
            all_values = np.linspace(
                amplitude_min_th, amplitude_max_th, num=MCH.size + 3
            )
            values = all_values[1:-1]
        # share new values
        values = MCH.master_broadcasts_array_to_all(values)
        Niter += 1
    # adapt Niter for correct return
    Niter -= 1
    # share master current amp to all process
    current_amp = MCH.master_broadcasts_array_to_all(current_amp)
    return current_amp, Niter
