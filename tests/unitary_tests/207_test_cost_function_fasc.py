import nrv
import matplotlib.pyplot as plt
import numpy as np

fig_DIR = "./unitary_tests/results/"

test_stim_CM = nrv.biphasic_stimulus_CM(s_cathod="0", t_cathod="1")
t_sim=5
static_context = "./unitary_tests/sources/200_fascicle_1.json"

test_CE = nrv.recrutement_count_CE()
X = np.array([
    [1, 0.6],
    [1, 0.6],
    [1, 0.6],
    [1, 0.6],
])

kwarg_sim = {
    "save_path":fig_DIR, 
    "return_parameters_only":False,
    "save_results":False,
    "postproc_script":"is_recruited"
}

cost_function = nrv.cost_function(
    static_context=static_context,
    context_modifier=test_stim_CM,
    cost_evaluation=test_CE,
    kwargs_S=kwarg_sim,
    t_sim=10,
)

"""
x = X[-1]
print(x)
fasc = test_stim_CM(x, static_context)
fasc.ID = 1
results = fasc(**kwarg_sim)
nrv.rm_sim_dir_from_results(results)
del fasc
"""


results = []
# simulate the axon
plt.figure(1)
plt.figure(2)
for i, x in enumerate(X[:2]):
    print(x)
    print(cost_function(x))

#plt.show()