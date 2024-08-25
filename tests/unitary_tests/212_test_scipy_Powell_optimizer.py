import nrv
from nrv.utils._nrv_function import sphere, rosenbock

import matplotlib.pyplot as plt

N_test = "211"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim_sphere.json"
fnam2 = "./unitary_tests/results/json/" + N_test + "_optim_rosenbock.json"

test_prob = nrv.Problem(save_problem_results=True)

my_cost1 = sphere()
my_cost2 = rosenbock()
test_prob.optimizer = nrv.scipy_optimizer(method="Powell")

cg_kwargs = {
    "dimensions" : 2,
    "maxiter":2,
}

test_prob.costfunction = my_cost1
print(test_prob.compute_cost(1)==1)
res1 = test_prob(problem_fname=fnam1, **cg_kwargs)
print("best position",res1.x, "best cost", res1.best_cost)




test_prob.costfunction = my_cost2
print(test_prob.compute_cost(1)==0)
res2 = test_prob(problem_fname=fnam2, **cg_kwargs)
print("best position",res2.x, "best cost", res2.best_cost)



fig,ax = plt.subplots(1)
res1.plot_cost_history(ax,label="sphere")
res2.plot_cost_history(ax,label="rosenbock")
ax.legend()
fig.savefig(figdir+"A.png")
#plt.show()