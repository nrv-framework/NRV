import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
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
    dt_fem = t_sim/(20*n_proc_global-1) # ms
    n_fem_step = 10*n_proc_global
    dt_fem = [
        (2.5, .5),
        (8,.1),
        (-1,.5),
         ]# ms

    sigma_method = "mean"
    inj_protocol_type = "simple"
    use_gnd_elec = True
    parameters = {"x_rec":x_rec,
    "dt_fem":dt_fem,
    "inj_protocol_type":inj_protocol_type,
    "n_proc_global":n_proc_global,
    "l_elec":l_elec,
    "l_fem":l_fem,
    "i_drive":i_drive,
    "sigma_method":sigma_method,
    "use_gnd_elec":use_gnd_elec,
    }

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id, **parameters)

    ## Nerve simulation
    sim_param = {"t_sim":t_sim}
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)

    ## Impedance simulation
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    fem_res = eit_instance.simulate_eit()
    del eit_instance
    fig = plt.figure(figsize=(20, 9))#, layout="constrained")
    subfigs = fig.subfigures(2, 4)
    axs = np.array([])
    for i_p, pat in enumerate(fem_res["p"]):
        dv_pc = fem_res.dv_eit(i_p=i_p)
        _, axs2 = eit.gen_fig_elec(n_e=fem_res.n_e, fig=subfigs[i_p%2, i_p//2], small_fig=True)
        eit.add_nerve_plot(axs=axs2, data=nerves_fname, drive_pair=pat)
        eit.plot_all_elec(axs=axs2, t=fem_res.t(), res_list=dv_pc,)
        axs = np.concatenate([axs, axs2[1:-1]])

    eit.scale_axs(axs=axs, e_gnd=[], has_nerve=False)
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")
    
    # plt.show()