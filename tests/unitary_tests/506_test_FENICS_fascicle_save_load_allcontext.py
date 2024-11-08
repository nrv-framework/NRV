import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":

#nrv.parameters.set_nrv_verbosity(4)
    test_num = 506
    DIR = "./unitary_tests/"
    fasc_file = DIR + "figures/506_fascicle_1.json"

    ##########################
    ## Fascicle declaration ##
    ##########################
    N = 17
    t0 = time.time()
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N, M_stat="Ochoa_M")


    t1 = time.time()
    print("Population of "+str(N)+" axons generated in "+str(t1 - t0)+" s")


    d = 500				# diameter, in um
    L = 10000 			# length, in um

    fascicle_1 = nrv.fascicle(ID=test_num)
    fascicle_1.define_length(L)
    fascicle_1.define_circular_contour(d)
    fascicle_1.fill_with_population(axons_diameters, axons_type, delta=5)
    fascicle_1.fit_circular_contour(delta = 0.1)
    fascicle_1.generate_random_NoR_position()
    t2 = time.time()

    print("Filled fascicle generated in "+str(t2 - t1)+" s")


    ##################################
    ##### Intracellular context ######
    ##################################
    position = 0.
    t_start = 1
    duration = 0.5
    amplitude = 4
    fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)

    ##################################
    ####### recording context ########
    ##################################
    testrec = nrv.recorder("endoneurium_bhadra")
    testrec.set_recording_point(L/4, 0, 100)
    testrec.set_recording_point(L/2, 0, 100)
    testrec.set_recording_point(3*L/4, 0, 100)
    fascicle_1.attach_extracellular_recorder(testrec)
    ##################################
    ##### extracellular context ######
    ##################################
    LIFE_stim = nrv.FEM_stimulation()
    # ### Simulation box size
    Outer_D = 5
    LIFE_stim.reshape_outerBox(Outer_D)
    #### Nerve and fascicle geometry
    Nerve_D = 250
    Fascicle_D = 220
    LIFE_stim.reshape_nerve(Nerve_D, L)
    LIFE_stim.reshape_fascicle(Fascicle_D)
    ##### electrode and stimulus definition
    D_1 = 25
    length_1 = 1000
    y_c_1 = 0
    z_c_1 = 0
    x_1_offset = (L-length_1)/2
    elec_1 = nrv.LIFE_electrode("LIFE_1", D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    start = 1
    I_cathod = 40
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    LIFE_stim.add_electrode(elec_1, stim1)
    fascicle_1.attach_extracellular_stimulation(LIFE_stim)

    t3 = time.time()
    print("Context generated in "+str(t3 - t2)+" s")

    ########################
    ## Save/Load Fascicle ##
    ########################
    fascicle_1.save(fname=fasc_file,extracel_context=True,intracel_context=True, rec_context=True)
    nrv.synchronize_processes()
    #fascicle_2 = nrv.fascicle()
    fascicle_2 = nrv.load_any(fasc_file,extracel_context=True,intracel_context=True, rec_context=True)


    t4 = time.time()
    print("fascicle saved in "+str(t4 - t0)+" s")
    fascicle_2.simulate(t_sim=5, save_path="./unitary_tests/figures/", verbose=True)
    t5 = time.time()
    print("Total time "+str(t5 - t0)+" s")
    loaded_rec = fascicle_2.recorder
    print(loaded_rec.t is not None)

    for k in range(len(loaded_rec.recording_points)):
        print(len(loaded_rec.t)==len(loaded_rec.recording_points[k].recording))


    if nrv.MCH.do_master_only_work():
        fig, ax = plt.subplots(figsize=(6,6))
        fascicle_2.plot(ax, num=True)

        DIR_fasc = "./unitary_tests/figures/Fascicle_"+str(test_num)+"/"
        plt.savefig(DIR+ "figures/506_A.png")

        fasc_state = nrv.fascicular_state(DIR_fasc, save=True, saving_file=DIR_fasc+"506_Facsicular_state.json")
        fig, ax = plt.subplots(figsize=(8,8))
        nrv.plot_fasc_state(fasc_state, ax, num=True)
        plt.savefig("./unitary_tests/figures/506_B.png")

        fig = plt.figure(figsize=(8,6))
        axs = []
