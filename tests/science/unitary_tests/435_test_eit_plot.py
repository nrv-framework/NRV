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

    r_list = []


    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3

    n_elec = 14
    l_fem = 1000 # um
    l_elec = 300 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    dt_fem = t_sim/(20*n_proc_global-1) # ms
    unmyelinated_nseg = 1000
    sigma_method = "avg_ind"
    sim_param = {"t_sim":t_sim}
    ax_param = {"unmyelinated_nseg":unmyelinated_nseg}
    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "sigma_method":sigma_method, "n_elec":n_elec}

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sigma_method, **parameters)
    ## Nerve simulation

    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param, ax_param=ax_param)
    ## Impedance simulation
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    del eit_instance

    r_list = eit.results.eit_results_list(results=r_list)
    fig, axs = eit.utils.gen_fig_elec(n_e=n_elec, figsize=(10,9))

    axs = eit.utils.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))
    axs = eit.utils.plot_all_elec(axs=axs, res_list=r_list, i_res=0, which="dv_eit")
    axs = eit.utils.scale_axs(axs=axs)
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")

    # plt.show()