
import nrv
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    context = "./unitary_tests/sources/200_unmyelinated_axon.json"
    t_sim=20
    # generate cost_evaluation method
    cost_evaluation = nrv.raster_count_CE()


    # generate stimulus
    N_spike = 6
    I_cathod = 80
    I_anod = I_cathod/5
    T_cathod = 60e-3
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

    print(cost_evaluation(results)==N_spike)

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')

    plt.savefig('./unitary_tests/figures/202_B.png')
    # plt.show()