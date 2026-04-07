import nrv
import numpy as np
import matplotlib.pyplot as plt
from nrv.backend._log_interface import rise_warning, rise_error

def choose_dt(fstim_khz, dt_max=0.001):
    dt_strob = 1.0 / fstim_khz  # ms

    # queremos o maior dt = dt_strob/k que seja ≤ dt_max
    # isso significa k >= dt_strob/dt_max
    k_min = int(dt_strob / dt_max)

    if dt_strob % dt_max == 0:
        return dt_max, dt_strob

    # teste crescente de k até achar o maior dt possível
    k = max(1, k_min)
    dt = dt_strob / k

    # garante dt ≤ dt_max
    if dt > dt_max:
        k += 1
        dt = dt_strob / k

    return dt, dt_strob

def ISI(axon:nrv.axon , results: nrv.axon_results, key: str = "V_mem", position: float=0.5, **kwargs) -> nrv.axon_results:
    """
    Compute the inter-spike intervals (ISI) from the membrane potential results at specified position along the axon
    
    Parameters
    ----------
    axon: nrv.axon
        The axon object used in the simulation.
    results : nrv.axon_results
        The results object obtained from simulating an axon.
    key : str, optional
        The key in the results dictionary corresponding to membrane potential data, by default "V_mem".
    position : float, optional
        Normalized position along the axon (0 to 1) where ISI is computed, by default 0.5.
    
    Returns
    -------
    nrv.axon_results
        A new results object containing the ISI data.
    
    ** kwargs
        Additional keyword arguments passed to the rasterization method
        - threshold: (float) threshold for AP detection, in mV. Default value is taken from the axon model.
        - t_min_AP: (float) minimum AP duration, in ms. Default is 0.1 ms.
        - t_refractory: (float) inter-AP duration, in ms. Default is 0.5 ms.
        - t_start: (float) start time for rasterization, in ms. Default is 0 ms.
        - t_stop: (float) stop time for rasterization, in ms. Default is the total simulation time.
    """

    results.rasterize(key, clear_artifacts = False, **kwargs)
    spike_position = results[f"{key}_raster_position"]
    spike_times = results[f"{key}_raster_time"]
    position_measured = np.int32(len(results[f"{key}"]) * position)
    measured_spike_times = spike_times[spike_position == position_measured]
    if measured_spike_times.size < 2:
        results.isi = 0.0
        return results
    else:
        isi_values = np.diff(measured_spike_times)
        results.isi = isi_values
        return results
    
def subsample(axon:nrv.axon, results: nrv.axon_results, key: str = "V_mem", new_dt = 0.01):
    """Subsample the results of an axon stimulation to a new time step.
    
    Parameters
    ----------

    axon : nrv.axon
        The axon object used in the simulation.
    results : nrv.axon_results
        The results object obtained from simulating an axon.
    key : str
        The key in the results dictionary corresponding to the data to be subsampled, by default "V_mem".
    new_dt : float
        The new time step for the subsampled data, in milliseconds. Must be larger than the original dt and also a multiple of it.

    This function adds 2 items to the results class with termination '_subsampled':

    """

    if new_dt <= axon.dt:
        results[f"{key}_subsampled"] = results[f"{key}"]
        results["t" + "_subsampled"] = results["t"]
        rise_warning(f"new_dt must be larger than the original dt. Returning the original {key} time series.", abort = False)
        return results
    if (new_dt / axon.dt) % 1 != 0:
        results[f"{key}_subsampled"] = results[f"{key}"]
        results["t" + "_subsampled"] = results["t"]
        rise_warning("new_dt must be a multiple of the original dt.Returning the original {key} time series.", abort = False)
        return results
    
    step = int(new_dt / axon.dt)
    results[f"{key}_subsampled"] = results[f"{key}"][:,::step]
    results["t" + "_subsampled"] = results["t"][::step]
    
    return results

def stroboscopic(axon:nrv.axon, results: nrv.axon_results, key: str = "V_mem", f_stim = 1.0):
    """
    Create a stroboscopic sampling of the results of an axon stimulation at the stimulation frequency.

    Parameters
    ----------
    axon : nrv.axon
        The axon object used in the simulation.
    results : nrv.axon_results
        The results object obtained from simulating an axon.
    key : str   
        The key in the results dictionary corresponding to the data to be sampled, by default "V_mem".
    f_stim : float
        The frequency of the stimulation in kHz.
    
    This function adds 2 items to the results class with termination '_stroboscopic':
    """

    dt_strob = 1.0 / (f_stim)  # in ms
    if dt_strob < axon.dt:
        results[f"{key}"+"_stroboscopic"] = results[f"{key}"]
        results["t"+"_stroboscopic"] = results["t"]
        rise_warning(f"Stimulation period is smaller than the simulation time step. Returning the original {key} time series.", abort = False)
        return results
    if (dt_strob / axon.dt) % 1 != 0:
        results[f"{key}"+"_stroboscopic"] = results[f"{key}"]
        results["t"+"_stroboscopic"] = results["t"]
        rise_warning(f"Stimulation period is not a multiple of the simulation time step. Returning the original {key} time series.", abort = False)
        return results
    subsample(axon, results, f"{key}", dt_strob)
    results[f"{key}"+"_stroboscopic"] = results[f"{key}"+"_subsampled"]
    results["t"+"_stroboscopic"] = results["t"+"_subsampled"]
    return results