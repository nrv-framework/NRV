import eit
import matplotlib.pyplot as plt
import numpy as np
import os

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    overwrite_rfile = True

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 4

    i_e = 4
    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
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
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    # Plot results
    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[2], i_e=i_e, which="v_rec", linestyle=":")
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")
    fem_res = r_list[-1]

    print("m nerve sim time :", fem_res['computation_time'], "s")
    i_e =  3
    t =  fem_res.t()
    v_elecs = fem_res.v_eit(i_e=i_e)
    dv_elecs = fem_res.dv_eit(i_e=i_e)

    fig, axs = plt.subplots(3, 2, figsize=(12,6))
    eit.plot_array(axs[0,0], t, v_elecs, marker="o")
    eit.plot_array(axs[1,0], t, dv_elecs, marker="o")
    axs[2,0].plot(fem_res["t_rec"], fem_res["v_rec"][:,0], color="r")
    axs[0,0].set_ylabel("$V_{EIT}$ (V)")
    axs[1,0].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,0].set_ylabel("$V_{REC}$ (mV)")
    axs[2,0].set_xlabel("time (ms)")

    t = fem_res.t(dt=0.1)
    v_elecs = fem_res.v_eit(t, i_e=i_e)
    dv_elecs = fem_res.dv_eit(t, i_e=i_e, pc=True)
    v_rec = fem_res.v_rec(t, i_e=i_e)

    eit.plot_array(axs[0,1], t, v_elecs, marker="o")
    eit.plot_array(axs[1,1], t, dv_elecs, marker="o")
    axs[2,1].plot(t, v_rec, ".-")

    axs[0,1].set_ylabel("$V_{EIT}$ (V)")
    axs[1,1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,1].set_ylabel("$V_{REC}$ (mV)")
    axs[2,1].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    del fem_res
