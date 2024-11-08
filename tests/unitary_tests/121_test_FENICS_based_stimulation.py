import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
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
    D_1 = 25
    length_1 = 1000
    y_c_1 = 50
    z_c_1 = 50
    x_1_offset = 1000
    elec_1 = nrv.LIFE_electrode('LIFE', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    start = 1
    I_cathod = 500
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim.add_electrode(elec_1, stim1)

    D_2 = 25
    length_2 = 1000
    y_c_2 = -50
    z_c_2 = -50
    x_2_offset = 5000
    elec_2 = nrv.LIFE_electrode('LIFE', D_2, length_2, x_2_offset, y_c_2, z_c_2)
    # stimulus def
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim.add_electrode(elec_2, stim2)

    ##### run FEM model
    #test_stim.run_model()

    ##### compute footprints
    x = np.linspace(0,L,num=1000)
    y = 0
    z = 0
    test_stim.compute_electrodes_footprints(x, y, z, ID=0)

    elec_1.save(save=True, fname="./unitary_tests/results/json/121_elec1fen.json")

    print(np.shape(elec_1.footprint))
    test_stim.model.get_timers(verbose=True)

    #### plot fotprints
    plt.figure()
    plt.plot(x, elec_1.footprint,color='r')
    plt.plot(x, elec_2.footprint,color='r')
    plt.savefig('./unitary_tests/figures/121_A.png')
    #plt.show()
