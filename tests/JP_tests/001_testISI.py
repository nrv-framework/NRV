import nrv
import numpy as np
import matplotlib.pyplot as plt

# import the extended results module
import extended_results


if __name__ == "__main__":
    L = 2000.0  # Length of the axon in micrometers
    D = 1.0     # Diameter of the axon in micrometers
    I0 = 5.0  # Constant current clamp in microamperes per
    A_stim = 0  # Amplitude of the sinusoidal stimulation in nanoampers
    f_stim = 1.0  # Frequency of the sinusoidal stimulation in kHz
    position_measure_isi = 0.95  # Normalized position along the axon (0 to 1)
    t_stop = 400.0  # Total simulation time in milliseconds
    dt = 0.001 #1/(f_stim * 1e3)    # Time step for the simulation in milliseconds
    t_start = 100.0  # Start time for the stimulation in milliseconds       
    model = 'HH' #'Rattay_Aberham' #

    axon = nrv.unmyelinated(0, 0, D, L, dt = dt, model = model)
    stim_protocol = nrv.stimulus()
    #stim_protocol.sinus(t_start, t_stop - t_start, A_stim, f_stim, offset=I0, phase=0, dt=dt)
    dur = 0.2
    for ti in np.arange(50, 350, 5):
        stim_protocol.pulse(ti, I0, dur)
    axon.insert_intra_stim(0.5, stim_protocol, stype="i")

    results = axon.simulate(t_sim=t_stop)

    extended_results.ISI(axon, results, key="V_mem", position=position_measure_isi, t_min_AP=0.01, t_refractory=0.05)
    print(results.isi)
    fig, ax = plt.subplots()
    ax.plot(results["t"], results["V_mem"][int(len(results["V_mem"])*position_measure_isi)])
    plt.show()