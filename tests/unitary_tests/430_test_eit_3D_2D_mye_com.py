import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
import nrv

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1max_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    overwrite_rfile = True

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3


    i_e = np.arange(1)
    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
    r_list = []

    l_ner = 20000 # um
    l_fem = 2600 # um
    l_elec = 2000 # um
    x_rec = 10250 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=1 # ms
    t_iclamp = 0 # ms
    dt_fem = t_sim/(2*n_proc_global-1) # ms
    e_elt_r = 0.1
    n_elt_r = 0.1
    f_elt_r = 0.1
    sim_param = {"t_sim":t_sim}
    # sim_param = {"t_sim":t_sim}
    use_gnd_elec = True


    parameters = {
        "x_rec":x_rec,
        "dt_fem":dt_fem,
        "n_proc_global":n_proc_global,
        "l_elec":l_elec,
        "l_fem":l_fem,
        "l_nerve":l_ner,
        # "e_elt_r":e_elt_r,
        # "n_elt_r":n_elt_r,
        # "f_elt_r":f_elt_r,
        "i_drive":i_drive,
        "use_gnd_elec":use_gnd_elec,
    }

    eit_instance = eit.EIT3DProblem(nerves_fname, res_dname=res_dir, label=test_id+"_3D_mye", **parameters)
    ## Nerve simulation
    # print(eit_instance.fem_res_file)
    if os.path.isfile(eit_instance.fem_res_file) and not overwrite_rfile:
        r_list += [eit_instance.fem_res_file]
        print("3D results loaded")
    else:
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
    del eit_instance


    # parameters["e_elt_r"] = 0.2
    # parameters["n_elt_r"] = 0.2
    # parameters["f_elt_r"] = 0.2
    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+"_2D_mye", **parameters)
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

    del eit_instance

    i_r_ = np.arange(len(r_list))
    r_list = eit.eit_results_list(results=r_list)
    labels = [r["label"] for r in r_list.res_info.values()]

    fig, axs = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axs = eit.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))
    dv_pc = r_list.get_res(i_res=i_r_, which="dv_eit",pc=True)
    eit.plot_all_elec(axs=axs, t=r_list.t(), res_list=dv_pc, i_res=i_r_, which="dv_eit")
    axs = eit.scale_axs(axs=axs, unit_y="%", zerox=True)
    axs[0].legend(labels)
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    fig, axs = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axs = eit.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))
    dv = r_list.get_res(i_res=i_r_, which="dv_eit",pc=False)
    eit.plot_all_elec(axs=axs, t=r_list.t(), res_list=dv, i_res=i_r_,linestyle=":", alpha=.5)

    axs = eit.scale_axs(axs=axs, unit_y="V", zerox=False)
    fig.savefig(f"./unitary_tests/figures/{test_id}_C.png")

    fig, axs = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axs = eit.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))
    v_ = r_list.get_res(i_res=i_r_, which="v_eit")
    eit.plot_all_elec(axs=axs, t=r_list.t(), res_list=v_, i_res=i_r_,linestyle=":", alpha=.5)

    # axs = eit.plot_all_elec(axs=axs, res_list=r_list, i_res=np.array([0,1]), which="dv_eit")
    axs = eit.scale_axs(axs=axs, unit_y="V", zerox=False)
    fig.savefig(f"./unitary_tests/figures/{test_id}_C.png")

    # plt.show()