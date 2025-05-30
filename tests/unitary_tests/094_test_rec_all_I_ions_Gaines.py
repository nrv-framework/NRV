import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    gnafbar_mrg = 3.0 # S.cm-2
    gnapbar_mrg = 0.01 # S.cm-2
    gksbar_mrg = 0.08  # S.cm-2
    gl_mrg = 0.007  # S.cm-2
    cm=1 * 1e-6 # F

    ## Test1


    y = 0
    z = 0
    d = 6
    L = nrv.get_length_from_nodes(d, 4) +100

    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all', Nseg_per_sec=1,model='Gaines_motor')
    #print(axon1.rec_position_list)
    total = 0
    for positions in axon1.rec_position_list:
        total += len(positions)
    #print(total)
    print(total == len(axon1.x_rec))

    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)

    t_sim=15
    results = axon1.simulate(t_sim=t_sim, record_V_mem=False, record_I_ions=True)
    print(axon1.this_ax_sequence)
    del axon1


    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['I_q'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('I q (mV)')
    plt.savefig('./unitary_tests/figures/94_A.png')

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['I_na'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('I na (mV)')

    plt.savefig('./unitary_tests/figures/94_B.png')
    #plt.show()
