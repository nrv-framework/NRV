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
    freqs = np.logspace(-3,3,3) # kHz
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    n_steps = 15 * n_proc_global


    parameters = {"x_rec":x_rec, "n_fem_step":n_steps,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "freqs":freqs}
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


    # Plot results
    t =  fem_res["t"]
    v_elecs = fem_res.v_eit(i_e=0)
    dv_elecs = fem_res.dv_eit(i_e=0)

    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].plot(t, v_elecs.T, color="k")
    axs[1].plot(t, dv_elecs.T, color="k")
    nrn_res.recorder.plot(axs[2], 0, color="k")

    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")
    if fem_res.is_multi_freqs:
        f = fem_res["f"]
        v_elecs = fem_res.v_eit(i_t=0, i_e=0)

        fig, ax = plt.subplots( figsize=(8,6))
        ax.plot(f, v_elecs, color="k")
        fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    del eit_instance
    # plt.show()