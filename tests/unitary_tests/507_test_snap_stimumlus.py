import nrv
import matplotlib.pyplot as plt
import time
import numpy as np

if __name__ == "__main__":
    L=10000
    d=10


    stim = nrv.stimulation()
    # ### Simulation box size
    d = 25
    length = 1000
    x_elec = 0                # electrode x position, in [um]
    y_elec = 100                # electrode y position, in [um]
    z_elec = 0                    # electrode y position, in [um]
    elec_1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    # stimulus def
    freq = 10
    amp = 10
    start = 0
    duration = 10
    stim1 = nrv.stimulus()
    stim1.sinus(start=start, duration=duration, amplitude=amp, freq=freq, dt=0.001)
    stim.add_electrode(elec_1, stim1)

    x_2_offset = (length)/2
    # electrode def
    x_elec = L/2                # electrode x position, in [um]
    y_elec = 100                # electrode y position, in [um]
    z_elec = 0                    # electrode y position, in [um]
    elec_2 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    start = 0
    I_cathod = 40
    I_anod = I_cathod/5
    T_cathod = 100e-3
    T_inter = 50e-3
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    stim.add_electrode(elec_2, stim2)

    stim.synchronise_stimuli()

    print(len(stim.stimuli[0].t), len(stim.stimuli[1].t),  len(stim.synchronised_stimuli[1].t))
    print(min(np.diff(stim.global_time_serie)))



    #nrv.parameters.set_nrv_verbosity(4)
    ax1 = nrv.myelinated(L=L, d=d)
    ax1.attach_extracellular_stimulation(stim)
    t0 = time.time()
    r1 = ax1.simulate(t_sim=3)
    t1 = time.time()
    del ax1

    stim.synchronised = False
    stim.synchronised_stimuli = []
    stim.synchronise_stimuli(snap_time=True)

    print(len(stim.stimuli[0].t), len(stim.stimuli[1].t),  len(stim.synchronised_stimuli[1].t))
    print(min(np.diff(stim.global_time_serie)))

    #nerve.compute_electrodes_footprints()

    #nrv.parameters.set_nrv_verbosity(4)
    ax2 = nrv.myelinated(L=L, d=d)
    ax2.attach_extracellular_stimulation(stim)
    t2 = time.time()
    r2 = ax2.simulate(t_sim=3)
    t3 = time.time()

    print('without snap : '+str(t1-t0)+' s')
    print('with snap : '+str(t3-t2)+' s')

    plt.figure()
    plt.plot(r1['t'], r1['V_mem'][len(r1['V_mem'])//2], label="without snap")
    plt.plot(r2['t'], r2['V_mem'][len(r2['V_mem'])//2], ':g', label="with snap")
    plt.legend()
    plt.savefig("./unitary_tests/figures/507_A.png")
    # plt.show()
