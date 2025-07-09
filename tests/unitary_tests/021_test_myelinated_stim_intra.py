import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 20000


    axon1 = nrv.myelinated(y,z,d,L,dt=0.001,rec='all')

    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)

    results = axon1.simulate(t_sim=6)
    del axon1
    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')

    plt.savefig('./unitary_tests/figures/21_A.png')
    # plt.show()