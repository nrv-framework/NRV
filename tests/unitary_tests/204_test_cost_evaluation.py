
import nrv
import matplotlib.pyplot as plt
import numpy as np
import time 
if __name__ == "__main__":
    t0 = time.time()
    context = "./unitary_tests/sources/202_axon.json"
    t_sim=2
    # generate cost_evaluation method
    test_CE1 = nrv.raster_count_CE()
    test_CE2 = nrv.charge_quantity_CE()


    # generate stimulus
    N_spike = 1
    I_cathod = 100
    I_anod = I_cathod*0.05
    T_cathod = 0.5
    T_inter = 40e-3
    stim = nrv.stimulus()
    stim.biphasic_pulse(0.1,  I_cathod, T_cathod, I_anod, T_inter)
    for i in range(1,N_spike):
        stimi = nrv.stimulus()
        stimi.biphasic_pulse(3*i,  I_cathod, T_cathod, I_anod, T_inter)
        stim += stimi

    plt.figure()
    N_plot = 300
    stim2 = nrv.stimulus()
    stim2.s = np.zeros(N_plot)
    stim2.t = np.linspace(0, t_sim, N_plot)
    stim2 += stim
    plt.plot(stim2.t, stim2.s)
    plt.savefig('./unitary_tests/figures/202_A.png')



    ## Generate and simulate axon
    ax = nrv.load_any(context, extracel_context=True)
    ax.change_stimulus_from_electrode(0, stim)
    results = ax(t_sim=t_sim)
    del ax
    t1 = time.time()
    print("simulation done in", t1 - t0, "s")
    print(test_CE1(results)==N_spike)
    t2 = time.time()
    print("cost1 computed in", t2 - t1, "s")
    print(test_CE2(results))
    t3 = time.time()
    print("cost2 computed in", t3 - t2, "s")

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')

    plt.savefig('./unitary_tests/figures/202_B.png')
    # plt.show()