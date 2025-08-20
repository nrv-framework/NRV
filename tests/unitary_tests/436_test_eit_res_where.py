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
    overwrite_rfile = True

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3

    i_e = 4
    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")

    l_nerve_sim = 10_000
    l_fem = 2600 # um
    l_elec = 2000 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    dt_fem = t_sim/(3*n_proc_global-1) # ms
    e_elt_r = 0.1
    n_elt_r = 0.1
    f_elt_r = 0.1
    sim_param = {"t_sim":t_sim}
    # sim_param = {"t_sim":t_sim}
    use_gnd_elec = True

    freqs = np.logspace(-3,3,3) # kHz


    parameters = {
        "x_rec":x_rec,
        "dt_fem":dt_fem,
        "l_nerve":l_nerve_sim,
        "n_proc_global":n_proc_global,
        "l_elec":l_elec,
        "l_fem":l_fem,
        "i_drive":i_drive,
        "use_gnd_elec":use_gnd_elec,
        "freqs":freqs,
    }

    r_list = []
    for x_rec in [2*k*1000 for k in range(1,4)]:
        sim_label = f"xr{x_rec}"
        parameters["x_rec"] = x_rec
        eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sim_label, **parameters)
        ## Nerve simulation

        nrn_res =eit_instance.simulate_nerve(save=False, t_start=t_iclamp, sim_param=sim_param)
        ## Impedance simulation
        eit_instance._setup_problem()
        # Build mesh
        eit_instance.build_mesh()


        r_list += [eit_instance.simulate_eit()]

        eit_instance.clear_fem_res()
        eit_instance.set_parameters(label=sim_label, x_rec=x_rec)

        r_list += [eit_instance.simulate_eit()]
        # Plot results

        r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle=":")
        r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle=":")
        r_list[-1].plot(axs[2], i_e=i_e, which="v_rec", linestyle=":")
        fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

        del eit_instance

    r_list = eit.eit_results_list(results=r_list)
    print(r_list.res_argwhere({"x_rec":2000}))
    print(r_list.res_argwhere("xr2000"))
    print(r_list.res_argwhere({"x_rec":6000}))
    print(r_list.res_argwhere(["xr2000", "xr6000"]))
    print(r_list.res_argwhere({"l_elec":2000}))



