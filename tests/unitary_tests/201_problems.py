import nrv
import numpy as np

if __name__ == "__main__":
    my_cost = nrv.sphere()

    test_prob = nrv.Problem()

    test_prob.costfunction = my_cost
    print(test_prob.compute_cost(0)== 0)
    print(test_prob.compute_cost(np.array([0,1,0])))
    print(np.allclose(test_prob.compute_cost(np.array([0,1,0])),1))
