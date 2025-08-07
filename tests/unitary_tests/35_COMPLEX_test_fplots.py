import eit
import matplotlib.pyplot as plt
import numpy as np
import os

__fname__ = __file__[__file__.find('tests/')+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    res_dir  = f"./results/{test_id}/"
    overwrite_rfile = True

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 4


    r_list = []

    l_fem = 2600 # um
    l_elec = 2000 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    dt_fem = t_sim/(5*n_proc_global-1) # ms
    e_elt_r = 0.1
    n_elt_r = 0.1
    f_elt_r = 0.1
    sim_param = {"t_sim":t_sim}
    # sim_param = {"t_sim":t_sim}
    use_gnd_elec = True

    freqs = np.logspace(-3,3,10) # kHz


    parameters = {
        "x_rec":x_rec,
        "dt_fem":dt_fem,
        "n_proc_global":n_proc_global,
        "l_elec":l_elec,
        "l_fem":l_fem,
        "i_drive":i_drive,
        "use_gnd_elec":use_gnd_elec,
        "freqs":freqs,
    }

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+"2D_mye", **parameters)
    ## Nerve simulation

    nrn_res =eit_instance.simulate_nerve(save=False, t_start=t_iclamp, sim_param=sim_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    i_e = 4
    fig, axs = plt.subplots(2, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[1].set_xlabel("time (ms)")
    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle=":")
    fig.savefig(f"figures/{test_id}_A.pdf")
    fem_res = r_list[-1]

    i_t = r_list[-1].n_t//2
    fig, axs = plt.subplots(2, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[0].set_xscale("log")
    axs[1].set_xscale("log")
    axs[1].set_xlabel("freq (kHz)")
    r_list[-1].plot(axs[0], i_e=i_e, i_t=i_t, xtype="f",which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, i_t=i_t, xtype="f",which="dv_eit", marker=".", linestyle=":")
    fig.savefig(f"figures/{test_id}_B.pdf")
    fem_res = r_list[-1]

    i_t = None
    fig, axs = plt.subplots(2, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[0].set_xscale("log")
    axs[1].set_xscale("log")
    axs[1].set_xlabel("freq (kHz)")
    r_list[-1].plot(axs[0], i_e=i_e, i_t=i_t, xtype="f",which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, i_t=i_t, xtype="f",which="dv_eit", marker=".", linestyle=":")
    fig.savefig(f"figures/{test_id}_B.pdf")
    fem_res = r_list[-1]

    plt.show()

