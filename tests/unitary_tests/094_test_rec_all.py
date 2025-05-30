import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":

    ## Test1
    y = 0
    z = 0
    d = 6
    L = nrv.get_length_from_nodes(d, 15)

    axon1 = nrv.myelinated(y,z,d,L,dt=0.001,rec='all')
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
    results = axon1.simulate(t_sim=t_sim, record_I_mem=True)
    del axon1


    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/94_A.png')



