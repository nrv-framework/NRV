
import nrv
import matplotlib.pyplot as plt
import numpy as np



## Cost function
# generate context modifier
def stimulus_generator(X, **kwargs):
    N_spike = X[0]
    I_cathod = 100
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim = nrv.stimulus()
    stim.biphasic_pulse(0.1,  I_cathod, T_cathod, I_anod, T_inter)
    for i in range(1,N_spike):
        stimi = nrv.stimulus()
        stimi.biphasic_pulse(3*i,  I_cathod, T_cathod, I_anod, T_inter)
        stim += stimi
    return stim

if __name__ == "__main__":
    context = "./unitary_tests/sources/202_axon.json"
    t_sim=20
    test_stim_CM = nrv.stimulus_CM(stim_gen=stimulus_generator)
    # generate cost_evaluation method
    cost_evaluation = - 2* nrv.raster_count_CE() + 3 * nrv.raster_count_CE()

    cost = nrv.cost_function(static_context=context, context_modifier=test_stim_CM, cost_evaluation=cost_evaluation, t_sim=20)
    N_test = 5
    X = np.array([[k] for k in range(N_test)]) + 1
    for i, x in enumerate(X):

        print(cost(x)==i+1)