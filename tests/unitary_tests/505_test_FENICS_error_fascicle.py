import nrv
import time

if __name__ == "__main__":
    t0 = time.time()
    source_file = './unitary_tests/sources/56_fasc.json'
    my_model = 'Nerve_1_Fascicle_1_LIFE'
    Ntest = 505
    ###########################
    ## extracellular context ##
    ###########################
    test_stim = nrv.FEM_stimulation()
    # ### Simulation box size
    Outer_D = 5
    test_stim.reshape_outerBox(Outer_D)
    #### Nerve and fascicle geometry
    L = 10000
    Nerve_D = 250
    Fascicle_D = 220
    test_stim.reshape_nerve(Nerve_D, L)
    test_stim.reshape_fascicle(Fascicle_D)
    ##### electrode and stimulus definition
    D_1 = 25
    length_1 = 1000
    y_c_1 = 50
    z_c_1 = 50
    x_1_offset = 4500
    elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    start = 1
    I_cathod = 40
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    test_stim.add_electrode(elec_1, stim1)

    ##########################
    ## Fascicle declaration ##
    ##########################
    fascicle_1 = nrv.fascicle()
    fascicle_1.load(source_file)

    fascicle_1.define_length(L)
    fascicle_1.set_ID(Ntest)
    # extra cellular stimulation
    fascicle_1.attach_extracellular_stimulation(test_stim)
    fascicle_1.axons["types"][12] = -1
    # simulation
    #print(fascicle_1.compute_electrodes_footprints())
    try:
        fascicle_1.simulate(t_sim=5)
        assert 1==0, "should complete the simulation"
    except AssertionError:
        print("...Expected error")
    except Exception as e:
        nrv.rise_error(e)