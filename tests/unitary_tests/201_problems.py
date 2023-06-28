import nrv
import nrv

def my_nerve_context(X):
    return X

def my_cost(results):
    return 1

test_prob = nrv.Problem()
test_prob.context_and_cost(my_nerve_context, my_cost)

print(test_prob.compute_cost(1))
