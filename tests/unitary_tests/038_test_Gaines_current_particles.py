import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # axon parameters
    y = 0
    z = 0
    d = 10
    L = 27000
    # intra stim parameters
    t_start = 5
    duration = 0.1
    amplitude = 2


    # Gaines sensory test
    axon1 = nrv.myelinated(y,z,d,L,model='Gaines_sensory',dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results1 = axon1.simulate(t_sim=15,record_I_ions=True, record_particles=True)
    del axon1
    if results1['Simulation_state'] == 'Unsuccessful':
        print(results1['Error_from_prompt'])

    # Gaines motor test
    axon2 = nrv.myelinated(y,z,d,L,model='Gaines_motor',dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon2.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results2 = axon2.simulate(t_sim=15,record_I_ions=True, record_particles=True)
    del axon2
    if results2['Simulation_state'] == 'Unsuccessful':
        print(results2['Error_from_prompt'])


    fig, axs = plt.subplots(3)

    axs[0].plot(results1['t'],results1['V_mem'][10])

    axs[1].plot(results1['t'],results1['I_na'][10])
    axs[1].plot(results1['t'],results1['I_nap'][10])
    axs[1].plot(results1['t'],results1['I_k'][10])
    axs[1].plot(results1['t'],results1['I_kf'][10])
    axs[1].plot(results1['t'],results1['I_l'][10])

    axs[2].plot(results1['t'],results1['m'][10])
    axs[2].plot(results1['t'],results1['mp'][10])
    axs[2].plot(results1['t'],results1['s'][10])
    axs[2].plot(results1['t'],results1['h'][10])
    axs[2].plot(results1['t'],results1['n'][10])
    plt.savefig('./unitary_tests/figures/38_A.png')


    fig, axs = plt.subplots(3)

    axs[0].plot(results2['t'],results2['V_mem'][10])

    axs[1].plot(results2['t'],results2['I_na'][10])
    axs[1].plot(results2['t'],results2['I_nap'][10])
    axs[1].plot(results2['t'],results2['I_k'][10])
    axs[1].plot(results2['t'],results2['I_kf'][10])
    axs[1].plot(results2['t'],results2['I_l'][10])

    axs[2].plot(results2['t'],results2['m'][10])
    axs[2].plot(results2['t'],results2['mp'][10])
    axs[2].plot(results2['t'],results2['s'][10])
    axs[2].plot(results2['t'],results2['h'][10])
    axs[2].plot(results2['t'],results2['n'][10])
    plt.savefig('./unitary_tests/figures/38_A.png')

    # plt.show()

