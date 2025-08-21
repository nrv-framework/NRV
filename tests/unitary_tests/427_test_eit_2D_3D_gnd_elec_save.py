import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3


    l_fem = 1000 # um
    l_elec = 300 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    dt_fem = t_sim/(3*n_proc_global-1) # ms

    use_gnd_elec = True
    sim_param = {"t_sim":t_sim}


    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "use_gnd_elec":use_gnd_elec}
    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label="2D"+test_id, **parameters)

    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(save=False,t_start=t_iclamp, sim_param=sim_param)

    ## Impedance simulation
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    fem_res = eit_instance.run_and_savefem(sfile=res_dir+"2Dtest", with_axons=True)
    del eit_instance

    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "use_gnd_elec":use_gnd_elec}
    eit_instance = eit.EIT3DProblem(nerves_fname, res_dname=res_dir, label="3D"+test_id, **parameters)

    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(save=False,t_start=t_iclamp, sim_param=sim_param)

    ## Impedance simulation
    # Simulate nerve
    fem_res = eit_instance.run_and_savefem(sfile=res_dir+"3Dtest", with_axons=True)
    del eit_instance


    print("all ok")