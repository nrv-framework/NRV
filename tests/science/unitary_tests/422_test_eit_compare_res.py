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

    new_t = eit.results.synchronize_times(fem_res_1, fem_res_2)

    print(fem_res_1.shape, fem_res_2.shape, new_t.shape)
    print("m nerve sim time :", fem_res_1['computation_time'], "s")
    dv = fem_res_2.dv_eit(t=new_t, i_e=i_e) - fem_res_1.dv_eit(t=new_t, i_e=i_e)
    fig, axs = plt.subplots(3, figsize=(12,6))
    fem_res_1.plot(axs[0], i_e=i_e, which="dv_eit", color="r", marker=".")
    fem_res_2.plot(axs[1], i_e=i_e, which="dv_eit", color="b", marker=".")
    axs[2].plot(new_t, dv,".-")
    axs[0].set_ylabel("$dV_{EIT}$ (V)")
    axs[1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2].set_ylabel("$V_{REC}$ (mV)")
    axs[2].set_xlabel("time (ms)")

    l_res = eit.results.eit_results_list(results=[fem_res_1, fem_res_2])
    t = l_res.t()
    dv_0 = l_res.dv_eit(i_res=0, i_e=i_e)
    dv_1 = l_res.dv_eit(i_res=1, i_e=i_e)
    dv_err = l_res.error(which="dv_eit", i_e=i_e, v_abs=True)
    axs[0].plot(t, dv_0,"--")
    axs[1].plot(t, dv_1,"--")
    axs[2].plot(t, dv_err,"--")

    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")



    # plt.show()