import nrv
import numpy as np
import matplotlib.pyplot as plt
if __name__ == "__main__":
    output_file = "./unitary_tests/results/outputs/125_res_sim"
    ##### extracellular context
    test_stim = nrv.FEM_stimulation()

    ### Simulation box size
    Outer_D = 6
    test_stim.reshape_outerBox(Outer_D)

    #### Nerve and fascicle geometry
    L = 7000
    Nerve_D = 300
    Fascicle_D = 270
    test_stim.reshape_nerve(Nerve_D, L)
    test_stim.reshape_fascicle(Fascicle_D)


    print(test_stim.is_empty())
    ##### electrodes and stimuli definition

    contact_length=50
    contact_thickness=20
    insulator_length=1000
    insulator_thickness=100

    x_center = L/2

    elec_1 = nrv.CUFF_electrode('CUFF', contact_length=contact_length,\
        contact_thickness=contact_thickness, insulator_length=insulator_length,\
        insulator_thickness=insulator_thickness, x_center=x_center)
    # stimulus def
    start = 1
    I_cathod = 500
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim.add_electrode(elec_1, stim1)

    ##### compute footprints
    x = np.linspace(0,L,num=1000)
    y = 0
    z = 0
    test_stim.compute_electrodes_footprints(x, y, z, ID=0)

    elec_1.save(save=True, fname="./unitary_tests/results/json/125_elec1fen.json")

    print(np.allclose(np.shape(elec_1.footprint),(1000,)))
    test_stim.model.get_timers(verbose=True)
    #print(output_file)
    test_stim.model.save(save=True, fname=output_file)

    #### plot fotprints
    plt.figure()
    plt.plot(x, elec_1.footprint,color='r')
    plt.savefig('./unitary_tests/figures/125_A.png')
    # plt.show()
