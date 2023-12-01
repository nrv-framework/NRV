#pragma parallel
import nrv
import numpy as np

import matplotlib.pyplot as plt

## Cost function definition
N_test = "215"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

t_sim = 6
t_end = t_sim-2
t_bound = (0, t_end)
I_bound = (-500, 0)


static_context = "./unitary_tests/sources/200_fascicle_1.json"

kwrgs_interp = {
    "dt": 0.005,
    "amp_start": 0,
    "amp_stop": 0,
    "intertype": "Spline",
    "bounds": I_bound,
    "fixed_order": False,
    "t_end": t_end,
    }
test_stim_CM = nrv.stimulus_CM(interpolator=nrv.interpolate_2pts, intrep_kwargs=kwrgs_interp, t_sim=t_sim)

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
test_prob = nrv.Problem(save_problem_results=True, problem_fname=fnam1)
test_prob.optimizer = nrv.PSO_optimizer()
bounds = (t_bound, I_bound, t_bound, I_bound)
pso_kwargs = {
    "dimensions" : 4,
    "maxiter" : 2,
    "n_particles" : 2,
    "opt_type" : "global",
    "bounds" : bounds,
}

test_prob.costfunction = my_cost1
res = test_prob(**pso_kwargs)

if nrv.MCH.do_master_only_work():
    print(res.x)
    plt.figure()
    res.plot_cost_history()
    plt.legend()
    plt.savefig(figdir+"A.png")
