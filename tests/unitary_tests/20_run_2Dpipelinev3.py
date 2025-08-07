import eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os

__fname__ = __file__[__file__.find('tests/')+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./nerves/u1_nerve.json"
    res_dir  = f"./results/{test_id}/"

    i_e = np.arange(1)
    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")

    r_list = []


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
    unmyelinated_nseg = 1000
    sigma_method = "avg_inter"
    sim_param = {"t_sim":t_sim}
    ax_param = {"unmyelinated_nseg":unmyelinated_nseg}
    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "sigma_method":sigma_method}

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sigma_method, **parameters)
    ## Nerve simulation

    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param, ax_param=ax_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".")
    r_list[-1].plot(axs[2], i_e=i_e, which="v_rec")
    del eit_instance

    sigma_method = "avg_interold"
    parameters["sigma_method"] = sigma_method

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sigma_method, **parameters)
    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param, ax_param=ax_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle="--")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle="--")
    r_list[-1].plot(axs[2], i_e=i_e, which="v_rec", linestyle="--")
    del eit_instance


    sigma_method = "avg_inter_approx"
    parameters["sigma_method"] = sigma_method

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sigma_method, **parameters)
    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param, ax_param=ax_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[2], i_e=i_e, which="v_rec", linestyle=":")

    fig.savefig(f"figures/{test_id}_u1_nerve.pdf")
    del eit_instance


    r_list = eit.eit_results_list(results=r_list)
    fig, axs = eit.gen_fig_elec(n_e=8, figsize=(10,9))

    axs = eit.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))

    axs = eit.plot_all_elec(axs=axs, res_list=r_list, i_res=np.array([0,1,2]), which="dv_eit")
    axs = eit.scale_axs(axs=axs)
    plt.show()