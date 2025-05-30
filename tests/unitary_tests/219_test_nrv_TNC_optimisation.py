import nrv
import numpy as np

import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## Cost function definition
    N_test = "219"
    figdir = "./unitary_tests/figures/" + N_test + "_"

    fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

    t_sim=5
    #static_context = "./unitary_tests/sources/200_fascicle_1.json"
    static_context = "./unitary_tests/sources/200_myelinated_axon.json"

    test_stim_CM = nrv.biphasic_stimulus_CM(start=0.1, s_cathod="0", t_cathod="1")
    costR = nrv.recrutement_count_CE()
    costC = nrv.charge_quantity_CE()
    cost_evaluation = (15 - costR) + 0.01*costC
    kwarg_sim = {}

    my_cost1 = nrv.cost_function(
        static_context=static_context,
        context_modifier=test_stim_CM,
        cost_evaluation=cost_evaluation,
        kwargs_S=kwarg_sim,
        t_sim=t_sim,
    )

    # Problem definition
    test_prob = nrv.Problem(save_problem_results=True, problem_fname=fnam1)

    bounds = (
        (0, 1000),
        (0.01, 0.25),
    )
    test_prob.optimizer = nrv.scipy_optimizer(method="TNC")

    cg_kwargs = {
        "dimensions": 2,
        "bounds": bounds,
        "maxiter": 2,
        "option": {"disp": True}
    }
    test_prob.costfunction = my_cost1
    res = test_prob(**cg_kwargs)

    print(res.x)
    fig,ax = plt.subplots(1)
    res.plot_cost_history(ax)
    ax.legend()
    plt.savefig(figdir+"A.png")
