import nrv
from nrv.utils.nrv_function import sphere, rosenbock

import matplotlib.pyplot as plt

N_test = "211"
figdir = "./unitary_tests/figures/" + N_test + "_"

fnam1 = "./unitary_tests/results/json/" + N_test + "_optim_sphere.json"
fnam2 = "./unitary_tests/results/json/" + N_test + "_optim_rosenbock.json"

test_prob = nrv.Problem(save_problem_results=True)

my_cost1 = sphere()
my_cost2 = rosenbock()
test_prob.optimizer = nrv.scipy_optimizer(method="CG")

cg_kwargs = {
    "dimensions" : 2,
    "maxiter":2,
}

test_prob.costfunction = my_cost1
print(test_prob.compute_cost(1)==1)
res1 = test_prob(problem_fname=fnam1, **cg_kwargs)
print(res1.x)




test_prob.costfunction = my_cost2
print(test_prob.compute_cost(1)==0)
res2 = test_prob(problem_fname=fnam2, **cg_kwargs)
print(res2.x)



plt.figure()
res1.plot_cost_history(label="sphere")
res2.plot_cost_history(label="rosenbock")
plt.legend()
plt.savefig(figdir+"A.png")
#plt.show()