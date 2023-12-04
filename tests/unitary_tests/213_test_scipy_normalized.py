import nrv
from nrv.utils.nrv_function import sphere, rosenbock, rastrigin
import numpy as np
import matplotlib.pyplot as plt

N_test = "213"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim_notscale.json"
fnam2 = "./unitary_tests/results/json/" + N_test + "_optim_scale.json"

test_prob = nrv.Problem(save_problem_results=True)

sp = rastrigin()
def my_cost1(x):
    y = np.array([x[0]+30, -x[1]/0.001, 0.1+x[2]])
    return sp(y)

test_prob.optimizer = nrv.scipy_optimizer(method="Powell")
bounds = ((-300, 300), (-0.001,.001), (-1000,0))
x0 = [np.random.uniform(min, max) for min, max in bounds]

cg_kwargs = {
    "bounds" : bounds,
    "x0" : x0,
    "maxiter" : 2,
}
test_prob.costfunction = my_cost1
res1 = test_prob(problem_fname=fnam1, **cg_kwargs)
print("scale bound",res1["scaled_bounds"], "scale_translation", res1.scale_translation, "scale_homothety", res1.scale_homothety)
print("best position",res1.x, "best cost", res1.best_cost)


test_prob.optimizer = nrv.scipy_optimizer(method="Powell")
cg_kwargs["normalize"] = True
res2 = test_prob(problem_fname=fnam2, **cg_kwargs)
print("scale bound",res2["scaled_bounds"], "scale_translation", res2.scale_translation, "scale_homothety", res2.scale_homothety)
print("best position",res2.x, "best cost", res2.best_cost)




plt.figure()
res1.plot_cost_history(label="sphere")
res2.plot_cost_history(label="rosenbock")
plt.legend()
plt.savefig(figdir+"A.png")
#plt.show()