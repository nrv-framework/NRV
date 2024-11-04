import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # mimicing axon coordinates
    L = 10000 # in um
    x = np.linspace(0,1,num=500)*L
    y = 0
    z = 0

    epineurium = nrv.load_material('endoneurium_ranck')

    # stimuli parameters
    I_cathod = 100
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3

    freq = 4
    amp = 10
    start = 1.5
    duration = 8.5

    # electrode 1 
    x_elec1 = L*1/4
    y_elec1 = 100
    z_elec1 = 0
    E1 = nrv.point_source_electrode(x_elec1,y_elec1,z_elec1)
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(1, I_cathod, T_cathod, I_anod, T_inter)

    # electrode 2
    x_elec2 = L*3/4
    y_elec2 = 100
    z_elec2 = 0
    E2 = nrv.point_source_electrode(x_elec2,y_elec2,z_elec2)
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(2, I_cathod, T_cathod, I_anod, T_inter)

    # electrode 3
    x_elec3 = L/2
    y_elec3 = 100
    z_elec3 = 0
    E3 = nrv.point_source_electrode(x_elec3,y_elec3,z_elec3)
    stim3 = nrv.stimulus()
    stim3.sinus(start, duration, amp, freq)

    ### define extra cellular stimulation
    big_stim = nrv.stimulation(epineurium)
    print(nrv.is_extra_stim(big_stim))
    big_stim.add_electrode(E1, stim1)
    big_stim.add_electrode(E2, stim2)
    big_stim.add_electrode(E3, stim3)
    print(big_stim.is_empty() == False)
    big_stim.synchronise_stimuli()
    print(big_stim.synchronised == True)
    print(len(big_stim.synchronised_stimuli)==3)
    # compute all electrodes footprints
    big_stim.compute_electrodes_footprints(x,y,z)
    # all synchronised stim have same signal length
    print(len(big_stim.synchronised_stimuli[1].s)==len(big_stim.synchronised_stimuli[2].s))
    print(len(big_stim.synchronised_stimuli[1].s)==len(big_stim.synchronised_stimuli[0].s))
    # all synchronised stim are not corupted ?
    print(len(big_stim.synchronised_stimuli[0].s)==len(big_stim.synchronised_stimuli[0].t))
    print(len(big_stim.synchronised_stimuli[1].s)==len(big_stim.synchronised_stimuli[1].t))
    print(len(big_stim.synchronised_stimuli[2].s)==len(big_stim.synchronised_stimuli[2].t))
    # the global time serie is the good one
    print(np.array_equal(big_stim.synchronised_stimuli[0].t, big_stim.global_time_serie))
    print(np.array_equal(big_stim.synchronised_stimuli[1].t, big_stim.global_time_serie))
    print(np.array_equal(big_stim.synchronised_stimuli[2].t, big_stim.global_time_serie))
    # 
    print(len(big_stim.global_time_serie)==3409)
    # 
    vext_1 = big_stim.compute_vext(1)
    vext_2 = big_stim.compute_vext(228)
    vext_3 = big_stim.compute_vext(3250)
    vext_4 = big_stim.compute_vext(4000)
    plt.figure()
    plt.plot(x,vext_1)
    plt.plot(x,vext_2)
    plt.plot(x,vext_3)
    plt.plot(x,vext_4)
    plt.savefig('./unitary_tests/figures/11_A.png')
    #plt.show()