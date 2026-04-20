import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ###########################
    ## extracellular context ##
    ###########################

    test_stim = nrv.FEM_stimulation(comsol=False)
    ### Simulation box size
    Outer_D = 5
    test_stim.reshape_outerBox(Outer_D)
    #### Nerve and fascicle geometry
    L = 10000
    Nerve_D = 250
    Fascicle_D = 220
    test_stim.reshape_nerve(Nerve_D, L)
    test_stim.reshape_fascicle(Fascicle_D)
    ##### electrode and stimulus definition
    # first electrode
    D_1 = 25
    length_1 = 1000
    y_c_1 = 50
    z_c_1 = 50
    x_1_offset = 2000
    elec_1 = nrv.LIFE_electrode('LIFE', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    start = 1
    I_cathod = 40
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim.add_electrode(elec_1, stim1)
    # secont electrode
    D_2 = 25
    length_2 = 1000
    y_c_2 = -50
    z_c_2 = -50
    x_2_offset = 7000
    elec_2 = nrv.LIFE_electrode('LIFE', D_2, length_2, x_2_offset, y_c_2, z_c_2)
    # stimulus def
    start_2 = 6
    I_cathod_2 = 40
    I_anod_2 = I_cathod/5
    T_cathod_2 = 60e-3
    T_inter_2 = 40e-3
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(start_2, I_cathod_2, T_cathod_2, I_anod_2, T_inter_2)
    test_stim.add_electrode(elec_2, stim2)

    ##########
    ## axon ##
    ##########
    # axon def
    y = 100                        # axon y position, in [um]
    z = 0                        # axon z position, in [um]
    d = 6.5                        # axon diameter, in [um]
    axon1 = nrv.myelinated(y,z,d,L,rec='all')
    axon1.attach_extracellular_stimulation(test_stim)

    # simulate the axon
    results = axon1.simulate(t_sim=10)
    del axon1

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/123_A.png')

    plt.figure()
    for k in range(len(results['node_index'])):
        index = results['node_index'][k]
        plt.plot(results['t'], results['V_mem'][index]+k*100, color = 'k')
    plt.yticks([])
    plt.xlim(0.9,7)
    plt.xlabel(r'time ($ms$)')
    plt.savefig('./unitary_tests/figures/123_B.png')
    # plt.show()