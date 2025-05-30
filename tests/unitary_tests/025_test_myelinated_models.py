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

    # MRG test
    axon1 = nrv.myelinated(y,z,d,L,model='MRG',dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results1 = axon1.simulate(t_sim=15)
    del axon1

    # Gaines sensory test
    axon2 = nrv.myelinated(y,z,d,L,model='Gaines_sensory',dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon2.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results2 = axon2.simulate(t_sim=15)
    del axon2

    # Gaines motor test
    axon3 = nrv.myelinated(y,z,d,L,model='Gaines_motor',dt=0.005,Nseg_per_sec=1,rec='nodes')
    axon3.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results3 = axon3.simulate(t_sim=15)
    del axon3

    plt.figure()
    plt.plot(results1['t'],results1['V_mem'][10],label='MRG')
    plt.plot(results2['t'],results2['V_mem'][10],label='Gaines sensory')
    plt.plot(results3['t'],results3['V_mem'][10],label='Gaines motor')
    plt.legend()
    plt.savefig('./unitary_tests/figures/25_A.png')

    plt.figure()
    plt.plot(results1['t'],results1['V_mem'][10],label='MRG')
    plt.plot(results2['t'],results2['V_mem'][10],label='Gaines sensory')
    plt.plot(results3['t'],results3['V_mem'][10],label='Gaines motor')
    plt.legend()
    plt.ylim(-86,-74.5)
    plt.xlim(5,11)
    plt.savefig('./unitary_tests/figures/25_B.png')


    #plt.show()