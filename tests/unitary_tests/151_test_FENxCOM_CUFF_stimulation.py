import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    my_model = "../nrv/_misc/comsol_templates/Nerve_1_Fascicle_1_CUFF.mph"
    ##### extracellular context
    test_stim1 = nrv.FEM_stimulation()
    test_stim2 = nrv.FEM_stimulation(my_model)

    ### Simulation box size
    Outer_D = 6
    test_stim1.reshape_outerBox(Outer_D)
    test_stim2.reshape_outerBox(Outer_D)

    #### Nerve and fascicle geometry
    L = 7000
    Nerve_D = 300
    Fascicle_D = 270
    test_stim1.reshape_nerve(Nerve_D, L)
    test_stim2.reshape_nerve(Nerve_D, L)
    test_stim1.reshape_fascicle(Fascicle_D, Perineurium_thickness=5)
    test_stim2.reshape_fascicle(Fascicle_D, Perineurium_thickness=5)


    ##### electrodes and stimuli definition
    contact_length=50
    contact_thickness=20
    insulator_length=1000
    insulator_thickness=100
    x_center = L/2

    fen_elec_1 = nrv.CUFF_electrode('CUFF_1', contact_length=contact_length,\
        contact_thickness=contact_thickness, insulator_length=insulator_length,\
        insulator_thickness=insulator_thickness, x_center=x_center)
    com_elec_1 = nrv.CUFF_electrode('CUFF_1', contact_length=contact_length,\
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
    test_stim1.add_electrode(fen_elec_1, stim1)
    test_stim2.add_electrode(com_elec_1, stim1)

    ##### compute footprints
    x = np.linspace(0,L,num=1000)
    y = 0
    z = 0

    
    print(test_stim1.comsol)
    test_stim1.compute_electrodes_footprints(x, y, z, ID=0)
    print(test_stim2.comsol)
    test_stim2.compute_electrodes_footprints(x, y, z, ID=0)

    fen_elec_1.save(save=True, fname="./unitary_tests/results/json/151_elec1fen.json")
    com_elec_1.save(save=True, fname="./unitary_tests/results/json/151_elec1com.json")

    print(np.shape(fen_elec_1.footprint))
    print('Fenics sim:')
    test_stim1.model.get_timers(verbose=True)
    print('Comsol sim:')
    test_stim2.model.get_timers(verbose=True)

    #### plot fotprints
    plt.figure()
    plt.plot(x, com_elec_1.footprint,'--',color='b', label='COMSOL')
    plt.plot(x, fen_elec_1.footprint,color='g', label='FEniCS')
    plt.legend()
    plt.savefig('./unitary_tests/figures/151_A.png')
    #plt.show()
