
#pragma parallel
import nrv
import numpy as np

import matplotlib.pyplot as plt

## Cost function definition
N_test = "215"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

t_sim=5
static_context = "./unitary_tests/sources/200_fascicle_1.json"
test_stim_CM = nrv.cathodic_stimulus_CM(start=0.1, I_cathod="0", T_cathod="1")
costR = nrv.recrutement_count_CE()
costC = nrv.charge_quantity_CE()
cost_evaluation = (15 - costR) + 0.01*costC
kwarg_sim = {
    "return_parameters_only":False,
    "save_results":False,
    "postproc_script":"is_excited"
}

my_cost1 = nrv.CostFunction(
    static_context=static_context,
    context_modifier=test_stim_CM,
    cost_evaluation=cost_evaluation,
    kwargs_S=kwarg_sim,
    t_sim=t_sim,
)

# Problem definition
test_prob = nrv.Problem()
test_prob.optimizer = nrv.PSO_optimizer()
bounds = (
    (0, 1000),
    (0.01, 2),
)
pso_kwargs = {
    "dimensions" : 2,
    "maxiter" : 4,
    "n_particles" : 3,
    "opt_type" : "global",
    "bounds":bounds,
}

test_prob.costfunction = my_cost1
res = test_prob(**pso_kwargs)

if nrv.MCH.do_master_only_work():
    print(res.x)
    plt.figure()
    res.plot_cost_history()
    plt.legend()
    plt.savefig(figdir+"A.png")
