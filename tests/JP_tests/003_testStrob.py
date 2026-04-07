import nrv
import numpy as np
import matplotlib.pyplot as plt

import extended_results

if __name__ == "__main__":
    L = 2000.0  # Length of the axon in micrometers
    D = 1.0     # Diameter of the axon in micrometers
    I0 = 0.0  # Constant current clamp in microamperes per
    A_stim = 0.235 # Amplitude of the sinusoidal stimulation in nanoampers
    f_stim = 1.0  # Frequency of the sinusoidal stimulation in kHz
    t_stop = 400.0  # Total simulation time in milliseconds
    dt = 1 /(f_stim * 1e3)     # Time step for the simulation in milliseconds
    dt_strob = 1 / f_stim
    pos_stim = 0.5
    t_start = 100.0  # Start time for the stimulation in milliseconds       
    model = 'HH' #'Rattay_Aberham' #

    axon = nrv.unmyelinated(0, 0, D, L, dt = dt, model = model)
    stim_protocol = nrv.stimulus()
    stim_protocol.sinus(t_start, t_stop - t_start, A_stim, f_stim, offset=I0, phase=0, dt=dt)
    # dur = 0.2
    # for ti in np.arange(50, 350, 5):
    #     stim_protocol.pulse(ti, I0, dur)
    axon.insert_intra_stim(pos_stim, stim_protocol, stype="i")

    results = axon.simulate(t_sim=t_stop)

    extended_results.stroboscopic(axon, results, key="V_mem", f_stim=f_stim)
    x_idx_stim = int(len(results["V_mem"]) * pos_stim)
    fig, ax = plt.subplots()
    ax.plot(results["t"], results["V_mem"][x_idx_stim], color = 'blue')
    ax.scatter(results["t_stroboscopic"], results["V_mem_stroboscopic"][x_idx_stim], s = 10, color = 'red')
    plt.show()