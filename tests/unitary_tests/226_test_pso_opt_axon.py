import sys 
sys.path.append("../")     #data path
import nrv

import matplotlib.pyplot as plt
import numpy as np
import os


if __name__ == "__main__":
    np.random.seed(444)

    N_test = "226"
    figdir = f"./unitary_tests/figures/{N_test}_"

    res_dir = f"./unitary_tests/results/json/{N_test}"

    ## Cost function definition
    my_cost0 = nrv.cost_function()

    axon_file = res_dir + "myelinated_axon.json"

    ax_l = 10000 # um
    ax_d=10
    ax_y=50
    ax_z=0
    axon_1 = nrv.myelinated(L=ax_l, d=ax_d, y=ax_y, z=ax_z)


    LIFE_stim0 = nrv.FEM_stimulation()
    LIFE_stim0.reshape_nerve(Length=ax_l)
    life_d = 25 # um
    life_length = 1000 # um
    life_x_0_offset = life_length/2
    life_y_c_0 = 0
    life_z_c_0 = 0
    elec_0 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_0_offset, life_y_c_0, life_z_c_0)

    dummy_stim = nrv.stimulus()
    dummy_stim.pulse(0, 0.1, 1)
    LIFE_stim0.add_electrode(elec_0, dummy_stim)

    axon_1.attach_extracellular_stimulation(LIFE_stim0)
    axon_1.get_electrodes_footprints_on_axon()
    _ = axon_1.save(save=True, fname=axon_file, extracel_context=True)

    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    axon_1.plot(ax)
    ax.set_xlim((-1.2*ax_y, 1.2*ax_y))
    ax.set_ylim((-1.2*ax_y, 1.2*ax_y))
    plt.savefig(figdir+"A.png")

    del axon_1

    static_context = axon_file
    t_sim = 5
    dt = 0.005
    kwarg_sim = {
        "dt":dt,
        "t_sim":t_sim,
    }

    my_cost0.set_static_context(axon_file, **kwarg_sim)

    t_start = 1
    I_max_abs = 100

    cm_0 = nrv.biphasic_stimulus_CM(start=t_start, s_cathod="0", t_cathod="1", s_anod=0)
    my_cost0.set_context_modifier(cm_0)

    test_points = np.array([[70, 0.5], [50, 1], [30, 1.5], [10, 2]])

    fig, ax = plt.subplots()
    ax.grid()
    for X in test_points:
        axon_x = cm_0(X, static_context)
        stim = axon_x.extra_stim.stimuli[0]
        stim.plot(ax, label=f"X={X}")
        ax.legend()
        del axon_x
    plt.savefig(figdir+"B.png")

    costR = nrv.recrutement_count_CE(reverse=True)
    costC = nrv.stim_energy_CE()

    cost_evaluation = costR + 0.01 * costC
    my_cost0.set_cost_evaluation(cost_evaluation)


    pso_kwargs = {
        "maxiter" : 50,
        "n_particles" : 20,
        "opt_type" : "local",
        "options": {'c1': 0.6, 'c2': 0.6, 'w': 0.8, 'k': 3, 'p': 1},
        "bh_strategy": "reflective",
    }
    pso_opt = nrv.PSO_optimizer(**pso_kwargs)


    # Problem definition
    my_prob = nrv.Problem(n_proc=4)
    my_prob.costfunction = my_cost0
    my_prob.optimizer = pso_opt


    t_end = 0.5
    duration_bound = (0.01, t_end)
    bounds0 = (
        (0, I_max_abs),
        duration_bound
    )
    pso_kwargs_pb_0 = {
        "dimensions" : 2,
        "bounds" : bounds0,
        "comment":"pulse"}

    res0 = my_prob(**pso_kwargs_pb_0)


    print("best input vector:", res0["x"], "\nbest cost:", res0["best_cost"])

    fig_costs, axs_costs = plt.subplots(2, 1)

    stim = cm_0(res0.x, static_context).extra_stim.stimuli[0]
    stim.plot(axs_costs[0], label="rectangle pulse")
    axs_costs[0].set_xlabel("best stimulus shape")
    axs_costs[0].set_xlabel("time (ms)")
    axs_costs[0].set_ylabel("amplitude (µA)")
    axs_costs[0].grid()

    res0.plot_cost_history(axs_costs[1])
    axs_costs[1].set_xlabel("optimization iteration")
    axs_costs[1].set_ylabel("cost")
    axs_costs[1].grid()
    fig_costs.tight_layout()
    plt.savefig(figdir+"C.png")

    simres = res0.compute_best_pos(my_cost0)
    simres.rasterize("V_mem")
    plt.figure()
    plt.scatter(simres["V_mem_raster_time"], simres["V_mem_raster_x_position"], color='darkslateblue')
    plt.xlabel('Times (ms)')
    plt.ylabel('Membrane voltage $V_{mem} (mV)$')
    plt.xlim(0, t_sim)
    plt.ylim(0, simres["L"])
    plt.grid()
    plt.tight_layout()
    plt.savefig(figdir+"D.png")


