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



    parameters = {
        "x_rec":x_rec,
        "dt_fem":dt_fem,
        "l_nerve":l_nerve_sim,
        "n_proc_global":n_proc_global,
        "l_elec":l_elec,
        "l_fem":l_fem,
        "i_drive":i_drive,
        "use_gnd_elec":use_gnd_elec,
    }
    x_rec_list = [2*k*1000 for k in range(1,4)]
    r_list = []
    sim_label =test_id+"_N1"
    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id+sim_label, **parameters)
    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(save=False, t_start=t_iclamp, sim_param=sim_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    r_list += [eit_instance.simulate_eit()]

    sim_label =test_id+"_N2"
    eit_instance.clear_fem_res()
    eit_instance.set_parameters(label=sim_label)
    r_list += [eit_instance.simulate_eit()]

    r_list[-1].plot(axs[0], i_e=i_e, which="v_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[1], i_e=i_e, which="dv_eit", marker=".", linestyle=":")
    r_list[-1].plot(axs[2], i_e=i_e, which="v_rec", linestyle=":")
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.pdf")

    del eit_instance

    r_list = eit.eit_results_list(results=r_list)
    i_r_ = np.arange(r_list.shape[0])

    labels = [r["label"] for r in r_list.res_info.values()]


    ###
    __which="dv_eit_pc"
    ###
    figdvpc_, axsdvpc_ = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axsdvpc_ = eit.add_nerve_plot(axs=axsdvpc_, data=nerves_fname, drive_pair=(0,5))
    dv_pc = r_list.get_res(i_res=i_r_, which=__which)
    eit.plot_all_elec(axs=axsdvpc_, t=r_list.t(), res_list=dv_pc, i_res=i_r_, which="dv_eit")
    axsdvpc_ = eit.scale_axs(axs=axsdvpc_, unit_y="%", zerox=True)
    figdvpc_.text(0.5,0.7,__which,ha="center",va="center")
    figdvpc_.savefig(f"figures/{test_id}_A.pdf")


    ###
    __which="dv_eit"
    ###
    figdv_, axsdv_ = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axsdv_ = eit.add_nerve_plot(axs=axsdv_, data=nerves_fname, drive_pair=(0,5))
    dv = r_list.get_res(i_res=i_r_, which=__which,pc=False)
    eit.plot_all_elec(axs=axsdv_, t=r_list.t(), res_list=dv, i_res=i_r_,linestyle=":", alpha=.5)
    axsdv_ = eit.scale_axs(axs=axsdv_, unit_y="V", zerox=False)
    figdv_.text(0.5,0.7,__which,ha="center",va="center")
    figdv_.savefig(f"figures/{test_id}_B.pdf")



    ###
    __which="v_eit"
    ###
    figv_, axsv_ = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axsv_ = eit.add_nerve_plot(axs=axsv_, data=nerves_fname, drive_pair=(0,5))
    v_ = r_list.get_res(i_res=i_r_, which=__which)
    eit.plot_all_elec(axs=axsv_, t=r_list.t(), res_list=v_, i_res=i_r_,linestyle=":", alpha=.5)
    axs = eit.scale_axs(axs=axsv_, unit_y="V", zerox=False)
    figv_.text(0.5,0.7,__which,ha="center",va="center")
    figv_.savefig(f"figures/{test_id}_C.pdf")

    ###
    __which="dv_eit_normalized"
    ###
    figv_, axsv_ = eit.gen_fig_elec(n_e=8, figsize=(10,9))
    axsv_ = eit.add_nerve_plot(axs=axsv_, data=nerves_fname, drive_pair=(0,5))
    v_ = r_list.get_res(i_res=i_r_, which=__which)
    eit.plot_all_elec(axs=axsv_, t=r_list.t(), res_list=v_, i_res=i_r_,linestyle="--", alpha=.5)
    axs = eit.scale_axs(axs=axsv_, unit_y="V", zerox=False)

    v_ = r_list.get_res(i_res=i_r_, which=__which, axis=(-2,-1))
    eit.plot_all_elec(axs=axsv_, t=r_list.t(), res_list=v_, i_res=i_r_,linestyle=":", alpha=.5)
    axs = eit.scale_axs(axs=axsv_, unit_y="V", zerox=False)

    figv_.text(0.5,0.7,__which,ha="center",va="center")
    figv_.savefig(f"figures/{test_id}_C.pdf")

    plt.show()
