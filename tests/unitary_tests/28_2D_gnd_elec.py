import eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os

__fname__ = __file__[__file__.find('tests/')+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./nerves/1uax_nerve.json"
    res_dir  = f"./results/{test_id}/"

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
    dt_fem = t_sim/(5*n_proc_global-1) # ms

    use_gnd_elec = True
    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive, "use_gnd_elec":use_gnd_elec}
    sim_param = {"t_sim":t_sim}


    i_e = np.arange(8)
    fig, axs = plt.subplots(3, figsize=(8,6))
    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
    r_list = []

    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id, **parameters)
    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    del eit_instance
    # Plot results
    t =  r_list[-1]["t"]
    v_elecs = r_list[-1].v_eit(i_e=i_e)
    dv_elecs = r_list[-1].dv_eit(i_e=i_e)

    axs[0].plot(t, v_elecs, color="k")
    axs[1].plot(t, dv_elecs, color="k")
    nrn_res.recorder.plot(axs[2], 0, color="k")

    eit_instance = eit.EIT3DProblem(nerves_fname, res_dname=res_dir, label=test_id, **parameters)
    ## Nerve simulation
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)
    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()
    # Simulate nerve
    r_list += [eit_instance.simulate_eit()]
    del eit_instance
    # Plot results
    t =  r_list[-1]["t"]
    v_elecs = r_list[-1].v_eit(i_e=i_e)
    dv_elecs = r_list[-1].dv_eit(i_e=i_e)

    axs[0].plot(t, v_elecs, color="k")
    axs[1].plot(t, dv_elecs, color="k")
    nrn_res.recorder.plot(axs[2], 0, color="k")


    fig.savefig(f"figures/{test_id}_u1_nerve.pdf")

    r_list = eit.eit_results_list(results=r_list)
    fig, axs = eit.gen_fig_elec(n_e=8, figsize=(10,9))

    axs = eit.add_nerve_plot(axs=axs, data=nerves_fname, drive_pair=(0,5))

    axs = eit.plot_all_elec(axs=axs, res_list=r_list, i_res=np.array([0,1]), which="dv_eit")
    axs = eit.scale_axs(axs=axs)
    plt.show()