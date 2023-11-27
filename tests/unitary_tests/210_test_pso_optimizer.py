
import nrv
from nrv.utils.nrv_function import sphere

my_cost = sphere()

test_prob = nrv.Problem()

test_prob.costfunction = my_cost
print(test_prob.compute_cost(1)==1)

test_prob.optimizer = nrv.PSO_optimizer()

dimensions = 2
N_it = 1000
n_particles = 10
opt_type = "local"
res = test_prob(dimensions=dimensions, N_it=N_it, n_particles=n_particles, opt_type=opt_type)

print(res.best_position)