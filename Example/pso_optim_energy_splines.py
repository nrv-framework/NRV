## argv[1]
## select which optim to launch (every digit equal to one)
## default 111 (all)

#pragma parallel
import nrv
import numpy as np
import sys
import os
import csv

import matplotlib.pyplot as plt

do_opt0 = True
do_opt2 = True

dir_res = f"./Tutorial_5/"
if not os.path.isdir(dir_res):
    os.mkdir(dir_res)

nerve_file = dir_res + "nerve.json"

def check_fname(fname):
    if os.path.isfile(fname):
        for i in range(len(fname)):
            if fname[-i-1] == ".":
                try:
                    fname = fname[:-i-2] + str(1+int(fname[-i-2])) + fname[-i-1:]
                except:
                    fname = fname[:-i-1] + "0" + fname[-i-1:]
        return check_fname(fname)
    return fname

def cost_position_saver(data, file_name='document.csv'):
    save = [str(data['cost'])]
    position = data['position']
    dim = len(position)
    for i in range(dim):
        save += [position[i]]
    with open(file_name,'a', newline='') as fd:
        writer = csv.writer(fd)
        writer.writerow(save)


np.random.seed(seed=10)
## Cost function definition
static_context = "./fascicles/fascicle_M2.json"

fname0 = dir_res + "/energy_optim_pso_biphasic.json"
fname2 = dir_res + "/energy_optim_pso_spline2pts.json"

costfname0 = dir_res + "/energy_cost_biphasic.csv"
costfname2 = dir_res + "/energy_cost_spline2pts.csv"

t_sim = 5
t_start = 1
t_end = 0.5
I_max_abs = 100
t_bound = (0, t_end)
I_bound = (-I_max_abs, 0)
duration_bound = (0.01, 0.5)

costR = nrv.recrutement_count_CE(reverse=True)
costC = nrv.stim_energy_CE()
cost_evaluation = costR + 0.01 * costC

kwarg_sim = {
    "return_parameters_only":False,
    "save_results":False,
    "postproc_script":"is_excited",
    "dt":0.002,
}

pso_kwargs = {
    "maxiter" : 2,
    "n_particles" : 2,
    "opt_type" : "local",
    "options": {'c1': 0.45, 'c2': 0.45, 'w': 0.75, 'k': 5, 'p': 1},
    "bh_strategy": "reflective",
    }

# Problem definition
test_prob = nrv.Problem(save_problem_results=False)
test_prob.optimizer = nrv.PSO_optimizer()


## first optim (biphasic pulse)
if nrv.MCH.do_master_only_work():
    print("first optim (biphasic pulse)")
context_modifier0 = nrv.biphasic_stimulus_CM(start=t_start, s_cathod="0", t_cathod=0.1*t_end, s_anod=0)
my_cost0 = nrv.cost_function(
    static_context=static_context,
    context_modifier=context_modifier0,
    cost_evaluation=cost_evaluation,
    kwargs_S=kwarg_sim,
    t_sim=t_sim,
    saver=cost_position_saver,
    file_name=costfname0,
)
bounds0 = (
    (0, I_max_abs),
)
pso_kwargs0 = pso_kwargs
pso_kwargs0.update({"dimensions" : 1, "bounds" : bounds0, "comment":"pulse"})

test_prob.costfunction = my_cost0
res0 = test_prob( problem_fname=fname0,**pso_kwargs0)

if nrv.MCH.do_master_only_work():
    res0.save(save=True, fname=check_fname(fname0))
    print(res0.x)
    plt.figure()
    res0.plot_cost_history()
    plt.savefig("A.png")

## Second optim (splines)
kwrgs_interp = {
    "dt": 0.002,
    "amp_start": 0,
    "amp_stop": 0,
    "intertype": "Spline",
    "bounds": I_bound,
    "fixed_order": False,
    "t_sim":t_sim,
    "t_end": t_end,
    "t_shift": t_start,
    }

if False:# do_opt2:
    if nrv.MCH.do_master_only_work():
        print("Second optim (splines 2pts)")
    context_modifier2 = nrv.stimulus_CM(interpolator=nrv.interpolate_Npts, intrep_kwargs=kwrgs_interp, t_sim=t_sim)
    my_cost2 = nrv.cost_function(
        static_context=static_context,
        context_modifier=context_modifier2,
        cost_evaluation=cost_evaluation,
        kwargs_S=kwarg_sim,
        t_sim=t_sim,
        saver=cost_position_saver,
        file_name=costfname2,
    )

    bounds2 = (t_bound, I_bound, t_bound, I_bound)
    pso_kwargs2 = pso_kwargs
    pso_kwargs2.update({"dimensions" : 4, "bounds" : bounds2, "comment":"spline 2pt"})

    test_prob.costfunction = my_cost2
    res2 = test_prob( problem_fname=fname2,**pso_kwargs2)
    if nrv.MCH.do_master_only_work():
        res2.save(save=True, fname=check_fname(fname2))
        nrv.interpolate_Npts(res2.x, save=True, fname="results/bestpos2.png", **kwrgs_interp)
        plt.figure(1)
        res2.plot_cost_history()
        plt.legend()
        plt.savefig("A.png")
