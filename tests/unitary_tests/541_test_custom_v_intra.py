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
    t_sim=10
    
    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

    t_start = 2
    duration = 0.1
    amplitude = 100
    node_index = 2
    s = nrv.stimulus()
    s.pulse(start=t_start, value=amplitude, duration=duration)
    s += axon1.v_init

    block_amp = 1
    block_freq = 10 #kHZ
    node_block = 7
    s_block = nrv.stimulus()
    s_block.sinus(start=0, amplitude=block_amp, freq=block_freq, duration=t_sim)
    s_block += axon1.v_init

    axon1.insert_V_Clamp_node(index=node_index, stimulus=s)
    axon1.insert_V_Clamp_node(index=node_block, stimulus=s_block)
    t_a1 = perf_counter()
    res_1 = axon1.simulate(t_sim=t_sim,record_I_mem=True)
    t_a1 = perf_counter() - t_a1
    del axon1


    axon2 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon2.insert_intra_stim_node(node_index, stim=s, stype="v")
    axon2.insert_intra_stim_node(node_block, stim=s_block, stype="v")

    t_a2 = perf_counter()
    res_2 = axon2.simulate(t_sim=t_sim,record_I_mem=True)
    t_a2 = perf_counter() - t_a2
    del axon2

    print(t_a1, t_a2)#, t_a3)

    i_plot = node_index

    fig, axs = plt.subplots(2)
    s.plot(axs[0], color="b", linestyle="--")
    axs[0].set_xlim(0,t_sim)


    axs[1].plot(res_1['t'],res_1['V_mem'][i_plot])
    axs[1].plot(res_2['t'],res_2['V_mem'][i_plot], "--")
    axs[1].set_xlim(0,t_sim)
    axs[1].set_ylabel('Voltage (mV/cm^2)')


    print()
    plt.savefig(f'{figdir}_A.png')

    fig, axs = plt.subplots(1,2)
    res_1.plot_x_t(axs[0], "V_mem")#, node_index=np.arange(0,5))
    res_2.plot_x_t(axs[1], "V_mem")#, node_index=np.arange(0,5))
    plt.savefig(f'{figdir}_A.png')
    # plt.show()