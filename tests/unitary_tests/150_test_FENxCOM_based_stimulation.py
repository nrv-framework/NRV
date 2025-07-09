import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    my_model = "../nrv/_misc/comsol_templates/Nerve_1_Fascicle_1_LIFE.mph"
    ##### extracellular context
    test_stim1 = nrv.FEM_stimulation()
    test_stim2 = nrv.FEM_stimulation(my_model)

    ### Simulation box size
    Outer_D = 6
    test_stim1.reshape_outerBox(Outer_D)
    test_stim2.reshape_outerBox(Outer_D)

    #### Nerve and fascicle geometry
    L = 15000
    Nerve_D = 300
    Fascicle_D = 270
    test_stim1.reshape_nerve(Nerve_D, L)
    test_stim2.reshape_nerve(Nerve_D, L)
    test_stim1.reshape_fascicle(Fascicle_D, Perineurium_thickness=5)
    test_stim2.reshape_fascicle(Fascicle_D, Perineurium_thickness=5)


    print(test_stim1.is_empty())
    print(test_stim2.is_empty())
    ##### electrodes and stimuli definition
    D_1 = 25
    length_1 = 1000
    y_c_1 = 50
    z_c_1 = 50
    x_1_offset = (L-length_1)/2
    fen_elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    com_elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    start = 1
    I_cathod = 500
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim1.add_electrode(fen_elec_1, stim1)
    test_stim2.add_electrode(com_elec_1, stim1)

    ##### compute footprints
    x = np.linspace(0,L,num=1000)
    y = 0
    z = 0
    test_stim1.compute_electrodes_footprints(x, y, z, ID=0)
    test_stim2.compute_electrodes_footprints(x, y, z, ID=0)

    fen_elec_1.save(save=True, fname="./unitary_tests/results/json/150_elec1fen.json")
    com_elec_1.save(save=True, fname="./unitary_tests/results/json/150_elec1com.json")

    print(np.shape(fen_elec_1.footprint))
    print('Fenics sim:')
    test_stim1.model.get_timers(verbose=True)
    print('Comsol sim:')
    test_stim2.model.get_timers(verbose=True)

    #### plot fotprints
    plt.figure()
    plt.plot(x, com_elec_1.footprint,color='b', label='COMSOL')
    plt.plot(x, fen_elec_1.footprint,color='g',label='FEniCS')
    plt.legend()
    plt.savefig('./unitary_tests/figures/150_A.png')
    # plt.show()
