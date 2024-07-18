#pragma parallel
import nrv
import numpy as np

import matplotlib.pyplot as plt

def bound_generator(amp_b,relative_amp_b,phase_b,n_tones):
    bounds = [amp_b]
    for k in range(n_tones):
        bounds.append(relative_amp_b)
        bounds.append(phase_b)
    return(bounds)

## Cost function definition
N_test = "223"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim1.json"

t_sim=5
start = 1
t_pulse = 100e-3
static_context = "./unitary_tests/sources/200_fascicle_1.json"
test_stim_CM = nrv.harmonic_stimulus_CM(start = start,t_pulse=t_pulse,dt = 0.005)
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
amp_bounds = (10,500)
relative_amp_bounds = (0,1)
phase_bounds = (np.pi,0)
n_tones = 3
bounds = bound_generator(amp_bounds,relative_amp_bounds,phase_bounds,n_tones)


pso_kwargs = {
    "dimensions" : 1+n_tones*2,
    "maxiter" : 2,
    "n_particles" : 2,
    "opt_type" : "global",
    "bounds" : bounds,
}

test_prob.costfunction = my_cost1
res = test_prob(**pso_kwargs)

if nrv.MCH.do_master_only_work():
    print(res.x)
    fig,ax = plt.subplots(1)
    res.plot_cost_history(ax)
    ax.legend()
    fig.savefig(figdir+"A.png")

#plt.show()