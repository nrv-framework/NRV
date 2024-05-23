#pragma parallel
import nrv
import numpy as np

import matplotlib.pyplot as plt

## Cost function definition
N_test = "215"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

t_sim = 5
t_end = 0.5
I_max_abs = 100
t_bound = (0, t_end)
I_bound = (-I_max_abs, 0)
dt = 0.005


static_context = "./unitary_tests/sources/200_fascicle_1.json"

kwrgs_interp = {
    "dt": dt,
    "amp_start": 0,
    "amp_stop": 0,
    "intertype": "Spline",
    "bounds": I_bound,
    "fixed_order": False,
    "t_end": t_end,
    "t_sim":t_sim,
    "strict_bounds":False,
    }
test_stim_CM = nrv.stimulus_CM(interpolator=nrv.interpolate_Npts, intrep_kwargs=kwrgs_interp, t_sim=t_sim)

costR = nrv.recrutement_count_CE(reverse=True)
costC = nrv.charge_quantity_CE()
cost_evaluation = costR + 0.01*costC
kwarg_sim = {
    "return_parameters_only":False,
    "save_results":False,
    "postproc_script":"is_excited"
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

dt = 0.005
t_sim = 1
I_max_abs = 100
t_bound = (0, 1)
I_bound = (-I_max_abs, 0)

kwrgs_interp2 = {
    "dt": dt,
    "amp_start": 0,
    "amp_stop": 0,
    "intertype": "Spline",
    "bounds": I_bound,
    "fixed_order": False,
    "t_sim":t_sim,
    "strict_bounds":True,
    }

test_stim_CM2 = nrv.stimulus_CM(interpolator=nrv.interpolate_Npts, intrep_kwargs=kwrgs_interp2, t_sim=t_sim)
my_cost2 = nrv.cost_function(
    static_context=static_context,
    context_modifier=test_stim_CM2,
    cost_evaluation=cost_evaluation,
    kwargs_S=kwarg_sim,
    t_sim=t_sim,
)
t_bound1 = (0,1)
t_end = (0.01, 0.5)
bounds2 = (t_bound, I_bound, t_bound, I_bound, t_end)
pso_kwargs = {
    "dimensions" : 5,
    "maxiter" : 2,
    "n_particles" : 2,
    "opt_type" : "global",
    "bounds" : bounds2,
}
test_prob.cost_function = my_cost2

res = test_prob(**pso_kwargs)

if nrv.MCH.do_master_only_work():
    print(res.x)
    plt.figure()
    res.plot_cost_history()
    plt.legend()
    plt.savefig(figdir+"B.png")
