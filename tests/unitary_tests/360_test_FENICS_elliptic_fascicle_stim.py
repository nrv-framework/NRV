import nrv
import time
import matplotlib.pyplot as plt
#nrv.parameters.set_nrv_verbosity(4)


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = test_dir+ "figures/" + test_num + "_"
meshfname = test_dir+ "results/mesh/" + test_num+ "_mesh.msh"

if __name__ == '__main__':
    t0 = time.time()

    geom = nrv.create_cshape((0,0), radius=(15, 11), rot=60, degree=True)
    ###########################
    ## extracellular context ##
    ###########################
    test_stim = nrv.FEM_stimulation()
    # ### Simulation box size
    Outer_D = 5
    test_stim.reshape_outerBox(Outer_D)
    #### Nerve and fascicle geometry
    L = 10_000
    Nerve_D = 250
    test_stim.reshape_nerve(Nerve_D, L)

    test_stim.reshape_fascicle(geometry=geom)
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
    fascicle_1.set_geometry(geometry=geom)
    fascicle_1.fill(n_ax=35)

    fascicle_1.define_length(L)
    fascicle_1.set_ID(124)
    # extra cellular stimulation
    fascicle_1.attach_extracellular_stimulation(test_stim)
    # simulation
    fascicle_1.compute_electrodes_footprints()
    # Save the mesh
    fascicle_1.extra_stim.model.mesh.save(fname=meshfname)
    #fascicle_1.extra_stim.run_model()

    res = fascicle_1.simulate(t_sim=10,postproc_script='is_recruited')
    t1 = time.time()
    print('simulation done in ' + str(t1-t0))

    fig, ax = plt.subplots()
    res.plot_recruited_fibers(ax)
    fig.savefig(fname=figdir+"A.png")

    del test_stim
    # plt.show()