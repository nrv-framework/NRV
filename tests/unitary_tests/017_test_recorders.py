import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    y = 0
    z = 0
    d = 1
    L = 500

    t_start = 1
    duration = 0.2
    amplitude = 1

    # test 1: 1 section stim in middle
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nseg_per_sec = 99)
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
    results = axon1.simulate(t_sim=4,record_I_mem=True, record_particles=True,record_I_ions=True)
    del axon1

    if results['Simulation_state'] == 'Unsuccessful':
        print(results['Error_from_prompt'])


    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/17_A.png')


    plt.figure()
    plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
    plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
    plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
    plt.xlabel('time (ms)')
    plt.ylabel('V membrane (mV)')
    plt.legend()
    plt.savefig('./unitary_tests/figures/17_B.png')


    fig, axs = plt.subplots(4)
    axs[0].plot(results['t'],results['V_mem'][75])
    axs[0].set_xlabel('time (ms)')
    axs[0].set_ylabel('voltage (mV)')
    axs[1].plot(results['t'],results['I_mem'][75])
    axs[1].set_xlabel('time (ms)')
    axs[1].set_ylabel('current (mA/cm^2)')
    axs[2].plot(results['t'],results['I_na'][75],label='Na')
    axs[2].plot(results['t'],results['I_k'][75],label='K')
    axs[2].plot(results['t'],results['I_l'][75],label='leakage')
    axs[2].set_xlabel('time (ms)')
    axs[2].set_ylabel('current (mA/cm^2)')
    axs[3].plot(results['t'],results['m'][75],label='m')
    axs[3].plot(results['t'],results['n'][75],label='n')
    axs[3].plot(results['t'],results['h'][75],label='k')
    axs[3].set_xlabel('time (ms)')
    plt.savefig('./unitary_tests/figures/17_C.png')
    #plt.show()