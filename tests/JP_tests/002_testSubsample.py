import nrv
import numpy as np
import matplotlib.pyplot as plt

import extended_results

if __name__ == "__main__":
    L = 2000.0  # Length of the axon in micrometers
    D = 1.0 # Diameter of the axon in micrometers
    I0 = 2.0  # Constant current clamp in microamperes per
    A_stim = 0  # Amplitude of the sinusoidal stimulation in nanoamp
    f_stim = 1.0  # Frequency of the sinusoidal stimulation in kHz
    dt = 0.001
    new_dt = 0.01
    t_stop = 400.0  # Total simulation time in milliseconds
    t_start = 100.0  # Start time for the stimulation in milliseconds
    pos_stim = 0.5  # Normalized position along the axon (0 to 1)

    model = 'HH' #'Rattay_Aberham' #
    axon = nrv.unmyelinated(0, 0, D, L, dt = dt, model = model)
    stim_protocol = nrv.stimulus()
    dur = 0.2
    for ti in np.arange(50, 350, 5):
        stim_protocol.pulse(ti, I0, dur)
    axon.insert_intra_stim(0.5, stim_protocol, stype="i")
    results = axon.simulate(t_sim=t_stop)
    x_idx_stim = int(len(results["V_mem"]) * pos_stim)
    extended_results.subsample(axon, results, key="V_mem", new_dt=new_dt)
    fig, ax = plt.subplots()
    ax.plot(results["t"], results["V_mem"][x_idx_stim], color = 'blue')
    ax.scatter(results["t_subsampled"], results["V_mem_subsampled"][x_idx_stim], s = 10, color = 'red')
    plt.show()
