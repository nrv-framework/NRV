import nrv
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = test_dir+ "figures/" + test_num + "_"


if __name__ == "__main__":
    test_stim_CM = nrv.biphasic_stimulus_CM(s_cathod="0", t_cathod="1")
    t_sim=5
    static_context = "./unitary_tests/sources/200_fascicle_1.json"

    test_CE = nrv.recrutement_count_CE()
    X = np.array([
        [10, 0.6],
        [20, 0.6],
        [50, 0.6],
    ])

    kwarg_sim = {
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
    cost_function.keep_results = True

    results = []
    # simulate the axon

    fig, axs = plt.subplots(1,3)
    excepted_cost = [0,3,3]
    for i, x in enumerate(X):
        c = cost_function(x)
        cost_function.results.plot_recruited_fibers(axs[i])
        axs[i].set_title(f"X = {x}\ncost = {c}")
        assert excepted_cost[i]==c, f"Wrong cost computed: {c} should be {excepted_cost[i]}"

    fig.savefig(figdir+"A.png")
    # plt.show()