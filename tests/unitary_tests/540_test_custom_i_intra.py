import nrv
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]
figdir = "unitary_tests/figures/" + test_id + "_"

if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 15000
    
    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

    t_start = 3
    duration = 0.1
    amplitude = 5
    node_index = 2
    axon1.insert_I_Clamp_node(node_index, t_start, duration, amplitude)

    t_sim=10
    t_a1 = perf_counter()
    res_1 = axon1.simulate(t_sim=t_sim,record_I_mem=True)
    t_a1 = perf_counter() - t_a1
    del axon1


    axon2 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')
    s = nrv.stimulus()
    s.pulse(start=t_start, value=amplitude, duration=duration)
    axon2.insert_intra_stim_node(node_index, stim=s)

    t_a2 = perf_counter()
    res_2 = axon2.simulate(t_sim=t_sim,record_I_mem=True)
    t_a2 = perf_counter() - t_a2
    del axon2



    axon3 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

    block_freq = 10 #kHZ
    s3 = nrv.stimulus()
    s3.sinus(start=t_start, amplitude=amplitude, freq=block_freq, duration=10*duration)

    axon3.insert_intra_stim_node(node_index, stim=s3)

    t_a3 = perf_counter()
    res_3 = axon3.simulate(t_sim=t_sim,record_I_mem=True)
    t_a3 = perf_counter() - t_a3
    del axon3


    axon4 = nrv.myelinated(y,z,d,3*L,dt=0.001,Nseg_per_sec=1,rec='nodes')
    block_node = 20
    block_amp = 100
    s4 = nrv.stimulus()
    s4.sinus(start=0, amplitude=block_amp, freq=block_freq, duration=t_sim)
    axon4.insert_intra_stim_node(node_index, stim=s)
    axon4.insert_intra_stim_node(block_node, stim=s4)

    t_a4 = perf_counter()
    res_4 = axon4.simulate(t_sim=t_sim,record_I_mem=True)
    t_a4 = perf_counter() - t_a4
    del axon4

    print(t_a1, t_a2, t_a3, t_a4)

    # ---------------- #
    # Theorical I_stim #
    # ---------------- #
    # Node area in cm
    node_d_cm = nrv.convert(nrv.get_MRG_parameters(d)[3], unitin="um", unitout="cm") # um
    node_l_cm = nrv.convert(1., unitin="um", unitout="cm") # um
    sec_area_cm_2 = (
        np.pi * node_d_cm * node_l_cm
        + 2 * np.pi * (node_d_cm/2) ** 2
    )

    amplitude_mA = nrv.convert(amplitude, unitin="nA", unitout="mA")
    # Curent density
    i_plot = node_index
    j_stim = np.zeros_like(res_1['V_mem'][i_plot])
    j_stim[(res_1['t']>t_start) & (res_1['t']<t_start+duration)] += (amplitude_mA/sec_area_cm_2)

    I_stim = np.zeros_like(res_1['V_mem'][i_plot])
    I_stim[(res_1['t']>t_start) & (res_1['t']<t_start+duration)] += amplitude
    # ---------------- #

    fig, axs = plt.subplots(3)
    axs[0].plot(res_1['t'],I_stim, "r")
    s.plot(axs[0], color="b", linestyle="--")
    s3.plot(axs[0], color="b", linestyle="--")
    axs[0].set_xlim(0,4)


    axs[1].plot(res_1['t'],res_1['I_mem'][i_plot])
    axs[1].plot(res_2['t'],res_2['I_mem'][i_plot], ":")
    axs[1].plot(res_3['t'],res_3['I_mem'][i_plot], "--")
    axs[1].set_xlim(0,4)
    axs[1].set_ylabel('current (mA/cm^2)')


    axs[2].plot(res_1['t'],res_1['I_mem'][i_plot] - j_stim)
    axs[2].set_xlim(0,4)
    axs[2].set_xlabel('time (ms)')
    axs[2].set_ylabel('current (mA/cm^2)')

    # print()
    # plt.savefig(f'{figdir}_A.png')

    fig, ax = plt.subplots()
    res_4.plot_x_t(ax, "V_mem")#, node_index=np.arange(0,5))
    # plt.savefig(f'{figdir}_A.png')
    # plt.show()