import nrv
import numpy as np

import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## Cost function definition
    N_test = "215"
    figdir = "./unitary_tests/figures/" + N_test + "_"

    fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

    t_sim=5
    static_context = "./unitary_tests/sources/200_fascicle_1.json"

    test_stim_CM = nrv.biphasic_stimulus_CM(start=0.1, s_cathod="0", t_cathod="1")
    costR = nrv.recrutement_count_CE(reverse=True)
    costC = nrv.charge_quantity_CE()
    cost_evaluation = costR + 0.01*costC
    kwarg_sim = {
        "return_parameters_only":False,
        "save_results":False,
        "postproc_script":"is_recruited"
    }

    my_cost1 = nrv.cost_function(
        static_context=static_context,
        context_modifier=test_stim_CM,
        cost_evaluation=cost_evaluation,
        kwargs_S=kwarg_sim,
        t_sim=t_sim,
    )

    # Problem definition
    test_prob = nrv.Problem(save_problem_results=True, problem_fname=fnam1)
    test_prob.optimizer = nrv.PSO_optimizer()
    bounds = (
        (0, 250),
        (0.01, 0.25),
    )
    pso_kwargs = {
        "dimensions" : 2,
        "maxiter" : 3,
        "n_particles" : 3,
        "opt_type" : "global",
        "bounds" : bounds,
    }

    test_prob.costfunction = my_cost1
    res = test_prob(**pso_kwargs)

    print(res.x)
    fig,ax = plt.subplots(1)
    res.plot_cost_history(ax)
    ax.legend()
    fig.savefig(figdir+"A.png")
