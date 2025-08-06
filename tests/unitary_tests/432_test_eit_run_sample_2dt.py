import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    res_dir  = f"./unitary_tests/results/{test_id}/"

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3

    t_sim=10 # ms
    t_1 = 2.4
    t_2 = 7.5
    dt_1 = 0.3
    dt_2 = 0.05



    l_fem = 1000 # um
    l_elec = 300 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_iclamp = 0 # ms
    dt_fem = [
        (t_1, dt_1),
        (t_2,dt_2),
        (-1,dt_1),
         ]# ms
    n_fem_step = 10*n_proc_global
    sigma_method = "mean"


    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "sigma_method":sigma_method}
    # parameters = {"x_rec":x_rec, "n_fem_step":n_fem_step,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "sigma_method":sigma_method}
    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id, **parameters)

    ## Nerve simulation
    sim_param = {"t_sim":t_sim}
    nrn_res = eit_instance.simulate_recording(t_start=t_iclamp, sim_param=sim_param)

    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    fem_res = eit_instance.simulate_eit()


    # Plot results
    i_e = np.arange(2)

    fig, axs = plt.subplots(3, figsize=(8,6))
    fem_res.plot(axs[0], i_e=i_e, which="v_eit", color="r", marker=".")
    fem_res.plot(axs[1], i_e=i_e, which="dv_eit", color="r", marker=".")
    fem_res.plot(axs[2], i_e=i_e, which="v_rec", color="r")
    axs[0].axvspan(t_1, t_2, color="k", alpha=.2)
    axs[1].axvspan(t_1, t_2, color="k", alpha=.2)
    axs[2].axvspan(t_1, t_2, color="k", alpha=.2)
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_u1_nerve.pdf")
    del eit_instance
    plt.show()