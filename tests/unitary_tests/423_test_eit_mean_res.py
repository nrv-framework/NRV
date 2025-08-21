import nrv.eit as eit
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    i_e = np.arange(1)


    labelu = "S0_2Dv1_static_0"
    labelm = "S0_3D_static_0"

    res_fname_1  = f"./unitary_tests/sources/SA_1_fem.json"
    res_fname_2  = f"./unitary_tests/sources/SA_1_fem.json"

    fem_res_1 = eit.results.eit_forward_results(data=res_fname_1)
    fem_res_2 = eit.results.eit_forward_results(data=res_fname_2)
    l_res = eit.results.eit_results_list(results=[fem_res_1, fem_res_2])


    t = l_res.t()

    dv_0 = l_res.dv_eit(i_res=0, i_e=i_e)
    dv_1 = l_res.dv_eit(i_res=1, i_e=i_e)
    dv_2 = l_res.dv_eit(i_res=[0, 1], i_e=i_e)
    dv_err = l_res.error(which="dv_eit", i_e=i_e, v_abs=True)
    dv_avg = l_res.mean(which="dv_eit", i_e=i_e)

    dv_std = l_res.std(which="dv_eit", i_e=i_e)
    fig, axs = plt.subplots(2, figsize=(12,6))

    axs[0].plot(t, dv_0,"-", label="dv1")
    axs[0].plot(t, dv_1,"-", label="dv2")
    axs[0].plot(t, dv_avg,"r", label="avg")
    axs[0].fill_between(t, dv_avg-dv_std, dv_avg+dv_std, color="r", alpha=.4)
    axs[0].legend()

    axs[1].plot(t, dv_0,"-", label="dv1")
    axs[1].plot(t, dv_1,"-", label="dv2")
    axs[1].plot(t, dv_err,"r", label="diff")
    axs[1].legend()


    axs[0].set_ylabel("$dV_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[1].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")
    # plt.show()