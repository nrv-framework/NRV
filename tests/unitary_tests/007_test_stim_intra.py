import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    y = 0
    z = 0
    d = 1
    L = 5000

    t_start = 1
    duration = 0.5
    amplitude = 5

    # test 1: 1 section stim in middle
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100)
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
    results = axon1.simulate(t_sim=10)
    del axon1

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/07_A.png')

    # test 2: 10 sections stim in middle
    axon2 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100,Nsec=10)
    axon2.insert_I_Clamp(0.5, t_start, duration, amplitude)
    results2 = axon2.simulate(t_sim=10)
    del axon2

    plt.figure()
    map = plt.pcolormesh(results2['t'], results2['x_rec'], results2['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/07_B.png')

    # test 3: 10 sections multiple stims
    axon3 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100,Nsec=10)
    axon3.insert_I_Clamp(0.25, t_start, duration, amplitude)
    axon3.insert_I_Clamp(0.75, t_start, duration, amplitude)
    axon3.insert_I_Clamp(0.5, t_start+7, duration, amplitude)
    results3 = axon3.simulate(t_sim=12)
    del axon3

    plt.figure()
    map = plt.pcolormesh(results3['t'], results3['x_rec'], results3['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/07_C.png')

    #plt.show()

