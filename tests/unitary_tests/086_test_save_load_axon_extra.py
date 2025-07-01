import nrv
import matplotlib.pyplot as plt
import numpy as np


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = test_dir+ "figures/" + test_num + "_"
extastim_file = test_dir+ "results/json/" + test_num+ "_extastim.json"
unm_axon_file = test_dir+ "results/json/" + test_num+ "_uaxon.json"
m_axon_file = test_dir+ "results/json/" + test_num+ "_maxon.json"

if __name__ == "__main__":
    ###########################
    ## extracellular contexts ##
    ###########################

    L_mye = 10000


    ####### electrode and stimulus definition
    D_1 = 25
    length_1 = 1000
    y_c_1 = 50
    z_c_1 = 50
    x_1_offset = L_mye/9
    elec_1 = nrv.LIFE_electrode('LIFE', D_1, length_1, x_1_offset, y_c_1, z_c_1)

    y_c_2 = 50
    z_c_2 = 50
    x_1_offset = L_mye/2
    elec_2 = nrv.LIFE_electrode('LIFE', D_1, length_1, x_1_offset, y_c_1, z_c_1)

    ####### stimulus def
    start = 0.5
    I_cathod = 10
    I_anod = I_cathod/5
    T_cathod = 100e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

    start2 = 5
    duration = 10
    amplitude = 10
    freq = 10
    stim2 = nrv.stimulus()
    stim2.sinus(start=start2, duration=duration, amplitude=amplitude, freq=freq)

    start = 10
    stim3 = nrv.stimulus()
    stim3.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

    stim_m1 = 8*(stim1+stim3)
    stim_m2 = 10*stim2

    stim_u1 = 88*(stim1+stim3)
    stim_u2 = 40*stim2

    # Stimulation context
    Outer_D = 5
    Nerve_D = 250
    Fascicle_D = 220
    #nrv.parameters.set_nrv_verbosity(2)
    test_stim = nrv.FEM_stimulation()
    ### Simulation box size
    test_stim.reshape_outerBox(Outer_D)
    #### Nerve and fascicle geometry

    test_stim.reshape_nerve(Nerve_D, L_mye)
    test_stim.reshape_fascicle(Fascicle_D)
    test_stim.add_electrode(elec_1, stim1+stim3)
    test_stim.add_electrode(elec_2, stim1)

    test_stim.save(save=True, fname=extastim_file)
    loaded_stim = nrv.load_any(extastim_file)
    #print(loaded_stim.save())
    print(nrv.is_mat(loaded_stim.perineurium))
    print(nrv.is_FEM_electrode(loaded_stim.electrodes[0]))




    ##########
    ## axon ##
    ##########

    # axon def
    y = 0                        # axon y position, in [um]
    z = 0                        # axon z position, in [um]
    d = 10                    # axon diameter, in [um]
    axonm1 = nrv.myelinated(y,z,d,L_mye,rec='all', dt=0.0003)
    axonm1.attach_extracellular_stimulation(test_stim)
    axonm1.change_stimulus_from_electrode(ID_elec=0, stimulus=stim_m1)
    axonm1.change_stimulus_from_electrode(ID_elec=1, stimulus=stim_m2)
    axonm1.get_electrodes_footprints_on_axon()


    """for i in axonm1.__dict__.keys():
        print(i, ": ", type(axonm1.__dict__[i]))
        if np.iterable(axonm1.__dict__[i]):
            if len(axonm1.__dict__[i])>0:
                print(i, ": ", type(axonm1.__dict__[i][0]))"""

    ax_dic1 = axonm1.save(save=True, fname=m_axon_file, extracel_context=True)
    # simulate the axon
    t_sim = 15
    results1 = axonm1.simulate(t_sim=t_sim)
    del axonm1

    axonm2 = nrv.load_any(ax_dic1, extracel_context=True)
    print(nrv.is_LIFE_electrode(axonm2.extra_stim.electrodes[0]))
    results2 = axonm2.simulate(t_sim=t_sim)
    del axonm2

    plt.figure()
    for k in range(len(results1['node_index'])):
        index = results1['node_index'][k]
        plt.plot(results1['t'], results1['V_mem'][index]+k*100, 'k')
        plt.plot(results2['t'], results2['V_mem'][index]+k*100, ':', color='grey')
    plt.yticks([])
    plt.xlim(0,t_sim)
    plt.xlabel(r'time ($ms$)')
    plt.savefig('./unitary_tests/figures/505_A.png')


    # axon def
    y = 0                        # axon y position, in [um]
    z = 0                        # axon z position, in [um]
    d = 1                    # axon diameter, in [um]
    axonu1 = nrv.unmyelinated(y,z,d,L_mye, dt=0.0003)
    axonu1.attach_extracellular_stimulation(test_stim)
    axonu1.change_stimulus_from_electrode(ID_elec=0, stimulus=stim_u1)
    axonu1.change_stimulus_from_electrode(ID_elec=1, stimulus=stim_u2)
    axonu1.get_electrodes_footprints_on_axon()

    ax_dic2 = axonu1.save(save=True, fname=unm_axon_file, extracel_context=True)
    # simulate the axon
    t_sim = 25
    resultsu1 = axonu1.simulate(t_sim=t_sim)
    del axonu1

    axonu2 = nrv.load_any(ax_dic2, extracel_context=True)
    resultsu2 = axonu2.simulate(t_sim=t_sim)
    del axonu2


    plt.figure(figsize=(14,6))
    plt.subplot(121)
    map = plt.pcolormesh(resultsu1['t'], resultsu1['x_rec'], resultsu1['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    plt.subplot(122)
    map = plt.pcolormesh(resultsu2['t'], resultsu2['x_rec'], resultsu2['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/505_B.png')









