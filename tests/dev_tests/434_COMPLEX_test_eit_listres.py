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
    r_list = []

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



    # parameters["e_elt_r"] = 0.2
    # parameters["n_elt_r"] = 0.2
    # parameters["f_elt_r"] = 0.2
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
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    del eit_instance


    ##########
    ## plot ##
    ##########

    print(r_list[-1].v_0().shape)

    i_r_ = np.arange(len(r_list))
    r_list = eit.results.eit_results_list(results=r_list)
    labels = [r["label"] for r in r_list.res_info.values()]
    figdvpc_, axsdvpc_ = eit.utils.gen_fig_elec(n_e=8, figsize=(10,9))
    figdv_, axsdv_ = eit.utils.gen_fig_elec(n_e=8, figsize=(10,9))
    figv_, axsv_ = eit.utils.gen_fig_elec(n_e=8, figsize=(10,9))

    for i_ in range(len(freqs)):
        axsdvpc_ = eit.utils.add_nerve_plot(axs=axsdvpc_, data=nerves_fname, drive_pair=(0,5))
        dv_pc = r_list.get_res(i_res=i_r_, which="dv_eit",pc=True, i_f=i_)
        eit.utils.plot_all_elec(axs=axsdvpc_, t=r_list.t(), res_list=dv_pc, i_res=i_r_, which="dv_eit")
        axsdvpc_ = eit.utils.scale_axs(axs=axsdvpc_, unit_y="%", zerox=True)
        axsdvpc_[0].legend(labels)
        figdvpc_.savefig(f"./unitary_testsfigures/{test_id}_A.png")

        axsdv_ = eit.utils.add_nerve_plot(axs=axsdv_, data=nerves_fname, drive_pair=(0,5))
        dv = r_list.get_res(i_res=i_r_, which="dv_eit",pc=False, i_f=i_)
        eit.utils.plot_all_elec(axs=axsdv_, t=r_list.t(), res_list=dv, i_res=i_r_,linestyle=":", alpha=.5)

        axsdv_ = eit.utils.scale_axs(axs=axsdv_, unit_y="V", zerox=False)
        figdv_.savefig(f"./unitary_testsfigures/{test_id}_B.png")

        axsv_ = eit.utils.add_nerve_plot(axs=axsv_, data=nerves_fname, drive_pair=(0,5))
        v_ = r_list.get_res(i_res=i_r_, which="v_eit", i_f=i_)
        eit.utils.plot_all_elec(axs=axsv_, t=r_list.t(), res_list=v_, i_res=i_r_,linestyle=":", alpha=.5)

        # axs = eit.utils.plot_all_elec(axs=axs, res_list=r_list, i_res=np.array([0,1]), which="dv_eit")
        axs = eit.utils.scale_axs(axs=axsv_, unit_y="V", zerox=False)
        figv_.savefig(f"./unitary_testsfigures/{test_id}_C.png")

    # plt.show()
