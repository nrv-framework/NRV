import nrv
from nrv.utils._nrv_function import sphere, rosenbock, rastrigin

import matplotlib.pyplot as plt

N_test = "210"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim_sphere.json"
fnam2 = "./unitary_tests/results/json/" + N_test + "_optim_rosenbock.json"
fnam3 = "./unitary_tests/results/json/" + N_test + "_optim_rastrigin.json"

test_prob = nrv.Problem(save_problem_results=True)

my_cost1 = sphere()
my_cost2 = rosenbock()
my_cost3 = rastrigin()
test_prob.optimizer = nrv.PSO_optimizer()

pso_kwargs = {
    "dimensions" : 4,
    "maxiter" : 100,
    "n_particles" : 20,
    "opt_type" : "local",
}

test_prob.costfunction = my_cost1
print(test_prob.compute_cost(1)==1)
res1 = test_prob(problem_fname=fnam1, **pso_kwargs)
print(res1.x)


test_prob.costfunction = my_cost2
print(test_prob.compute_cost(1)==0)
res2 = test_prob(problem_fname=fnam2, **pso_kwargs)
print(res2.x)


test_prob.costfunction = my_cost3
print(test_prob.compute_cost(1)==0)
res3 = test_prob(problem_fname=fnam3, **pso_kwargs)
print(res3.x)

fig,ax = plt.subplots(1)
res1.plot_cost_history(ax,label="sphere")
res2.plot_cost_history(ax,label="rosenbock")
res2.plot_cost_history(ax,label="rastrigin")
ax.legend()
fig.savefig(figdir+"A.png")

#plt.show()