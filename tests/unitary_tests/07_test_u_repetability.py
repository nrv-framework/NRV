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
    dt_fem = t_sim/(3*n_proc_global-1) # ms


    parameters = {"x_rec":x_rec, "dt_fem":dt_fem,"n_proc_global":n_proc_global, "l_elec":l_elec, "l_fem":l_fem, "i_drive":i_drive}

    fig, axs = plt.subplots(3, figsize=(8,6))

    for i in range(3):
        eit_instance = eit.EIT3DProblem(nerves_fname, res_dname=res_dir, label=test_id+f"_{i}", **parameters)

        ## Nerve simulation
        sim_param = {"t_sim":t_sim}
        nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)

        ## Impedance simulation
        eit_instance._define_problem()
        # Build mesh
        eit_instance.build_mesh()
        # Simulate nerve
        fem_res = eit_instance.simulate_eit()


        # Plot results
        t =  fem_res["t"]
        v_elecs = fem_res.v_eit(i_e=0)
        dv_elecs = fem_res.dv_eit(i_e=0)

        axs[0].plot(t, v_elecs, color="r", alpha=1-i*0.2)
        axs[1].plot(t, dv_elecs, color="r", alpha=1-i*0.2)
        nrn_res.recorder.plot(axs[2], 0, color="r", alpha=1-i*0.2)

    axs[0].set_ylabel("$V_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")
    fig.savefig(f"figures/{test_id}_m1_nerve.pdf")
    del eit_instance
    plt.show()