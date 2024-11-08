import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 27000


    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

    t_start = 5
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)

    results = axon1.simulate(t_sim=15)
    del axon1
    plt.figure()
    plt.plot(results['t'],results['V_mem'][2],color='r')
    plt.plot(results['t'],results['V_mem'][10],color='tab:gray')
    plt.plot(results['t'],results['V_mem'][18],color='b')
    plt.ylim(-80,-75.5)
    plt.xlim(4.5,13)
    plt.savefig('./unitary_tests/figures/22_A.png')

    axon2 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes',T=33)

    t_start = 5
    duration = 0.1
    amplitude = 2
    axon2.insert_I_Clamp_node(2, t_start, duration, amplitude)

    results2 = axon2.simulate(t_sim=15)
    del axon2
    plt.figure()
    plt.plot(results2['t'],results2['V_mem'][2],color='r')
    plt.plot(results2['t'],results2['V_mem'][10],color='tab:gray')
    plt.plot(results2['t'],results2['V_mem'][18],color='b')
    plt.ylim(-80,-75.5)
    plt.xlim(4.5,13)
    plt.savefig('./unitary_tests/figures/22_B.png')

    fig, ax = plt.subplots()
    results2.plot_x_t(ax)
    plt.savefig('./unitary_tests/figures/22_C.png')
    #plt.show()