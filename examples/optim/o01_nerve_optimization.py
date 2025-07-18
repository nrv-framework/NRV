r"""
Optimization Pulse Stimulus on Nerve
====================================

This example is an extension of the Tutorial 5, the optimization formalism used in NRV is illustrated through a detailed example.

The objective of the first optimization problem is to **minimize a rectangle pulse stimulus energy required by a LIFE-electrode to trigger a single myelinated fibre**.

.. note::
    This example is run with only run on a 30-fibres nerve, for a small optimization (10 PSO particles, 15 iterations). Those parameters could be increase for a more realistic problem.

"""

import matplotlib.pyplot as plt
import numpy as np
import os
import nrv

np.random.seed(4444)

if __name__ == '__main__':
    # test_name = "Example_"
    # dir_res = f"./{test_name}/"
    # if not os.path.isdir(dir_res):
    #     os.mkdir(dir_res)

    ## Cost function definition
    my_cost0 = nrv.cost_function()

    # Static context
    # nerve_file = dir_res + "nerve.json"

    outer_d = 5 # mm
    nerve_d = 300 # um
    nerve_l = 5000 # um

    fasc1_d = 250 # um
    fasc1_y = 0
    fasc1_z = 0
    n_ax1 = 20


    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)
    nerve_1.verbose = False

    fascicle_1 = nrv.fascicle(diameter=fasc1_d, ID=0)      #we can add diameter here / no need to call define_circular_contour (not tested)
    fascicle_1.fill(n_ax=n_ax1, percent_unmyel=0, M_stat="Ochoa_M", U_stat="Ochoa_U",delta=5)
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

    # LIFE in neither of the two fascicles
    LIFE_stim0 = nrv.FEM_stimulation()
    LIFE_stim0.reshape_nerve(Length=nerve_l)
    life_d = 25 # um
    life_length = 1000 # um
    life_x_0_offset = life_length/2
    life_y_c_0 = 0
    life_z_c_0 = 0
    elec_0 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_0_offset, life_y_c_0, life_z_c_0)

    dummy_stim = nrv.stimulus()
    dummy_stim.pulse(0, 0.1, 10)
    LIFE_stim0.add_electrode(elec_0, dummy_stim)
    nerve_1.attach_extracellular_stimulation(LIFE_stim0)

    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_1.plot(ax)

    nerve_1.compute_electrodes_footprints()
    nerve_1.set_parameters(postproc_script="is_recruited")
    static_context = nerve_1.save(save=False, extracel_context=True)
    del nerve_1


    t_sim = 5
    dt = 0.005
    kwarg_sim = {
        "dt":dt,
        "t_sim":t_sim,
        "loaded_footprints":True,
    }

    my_cost0.set_static_context(static_context, **kwarg_sim)

    # Context modifier
    t_start = 1
    I_max_abs = 100

    cm_0 = nrv.biphasic_stimulus_CM(start=t_start, s_cathod="0", t_cathod="1", s_anod=0)
    my_cost0.set_context_modifier(cm_0)

    # Cost evaluation
    costR = nrv.recrutement_count_CE(reverse=True)
    costC = nrv.stim_energy_CE()

    cost_evaluation = costR + 0.01 * costC
    my_cost0.set_cost_evaluation(cost_evaluation)


    ## Optimizer
    pso_kwargs = {
        "maxiter" : 15,
        "n_particles" : 10,
        "opt_type" : "local",
        "options": {'c1': 0.55, 'c2': 0.55, 'w': 0.75, 'k': 2, 'p': 1},
        "bh_strategy": "reflective",
    }
    pso_opt = nrv.PSO_optimizer(**pso_kwargs)

    ## Problem definition
    my_prob = nrv.Problem()
    my_prob.costfunction = my_cost0
    my_prob.optimizer = pso_opt


    # Optimization
    t_end = 0.5
    bounds0 = (
        (0, I_max_abs),
        (0.01, t_end),
    )
    pso_kwargs_pb_0 = {
        "dimensions" : 2,
        "bounds" : bounds0,
        "comment":"pulse"}

    res0 = my_prob(**pso_kwargs_pb_0)

    res_sim = res0.compute_best_pos(my_cost0)

    # Plot results on master process
    fig_costs, axs_costs = plt.subplots(2, 1)

    stim = cm_0(res0.x, static_context).extra_stim.stimuli[0]
    stim.plot(axs_costs[0])
    axs_costs[0].set_xlabel("best stimulus shape")
    axs_costs[0].set_xlabel("time (ms)")
    axs_costs[0].set_ylabel("amplitude (µA)")

    res0.plot_cost_history(axs_costs[1])
    axs_costs[1].set_xlabel("optimization iteration")
    axs_costs[1].set_ylabel("cost")
    fig_costs.tight_layout()

    fig_best, ax_best = plt.subplots(figsize=(6,6))
    ax_best.set_title("recruited fibers")
    res_sim.plot_recruited_fibers(ax_best)

    plt.show()