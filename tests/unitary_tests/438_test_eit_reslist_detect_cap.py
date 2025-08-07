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
    overwrite_rfile = False

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
    t_sim=15 # ms
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
    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=sim_label, **parameters)
    if os.path.isfile(eit_instance.fem_res_file) and not overwrite_rfile:
        r_list += [eit_instance.fem_res_file]
        sim_label =test_id+"_N2"
        eit_instance.clear_fem_res()
        eit_instance.set_parameters(label=sim_label)
        r_list += [eit_instance.fem_res_file]
        print("results loaded")
    else:
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
    cap_mask = r_list.get_cap_mask(i_res=i_r_)
    cap_i_t = r_list.get_cap_i_t(i_res=i_r_)
    print(cap_mask.shape, len(cap_i_t))

    labels = [r["label"] for r in r_list.res_info.values()]


    __which="dv_eit"
    figdvpc_ = eit.Figure_elec(n_e=8, figsize=(10,9))
    figdvpc_.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    dv_pc = r_list.get_res(i_res=i_r_, which=__which)
    figdvpc_.plot_all_elec(t=r_list.t(), data=dv_pc, i_res=i_r_,)

    dv_pc_cap, t_cap = r_list.get_cap_res(i_res=i_r_, which=__which, with_t=True)
    print(type(dv_pc_cap), type(t_cap))
    print(len(dv_pc_cap), len(t_cap))
    print(dv_pc_cap[0].shape, t_cap[0].shape)
    figdvpc_.plot_all_elec(t=t_cap, data=dv_pc_cap, i_res=i_r_, linestyle="--")


    figdvpc_.scale_axs(unit_y="%", zerox=True)
    figdvpc_.fig.text(0.5,0.7,__which,ha="center",va="center")
    figdvpc_.fig.savefig(f"./unitary_tests/figures/{test_id}_A.pdf")

    dv_pc = r_list.get_res(i_res=i_r_, i_e=i_e, which=__which)
    t_ = r_list.t()*np.ones(dv_pc.shape)
    dv_pc = dv_pc.T
    t_ = t_.T
    print(dv_pc.shape, t_.shape)
    cap_mask = dv_pc >0.05
    fig, ax = plt.subplots()
    ax.plot(t_, dv_pc)
    ax.plot(t_[cap_mask], dv_pc[cap_mask])

    plt.show()
