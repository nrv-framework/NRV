import eit
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

__fname__ = __file__[__file__.find('tests/')+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./nerves/1uax_nerve.json"
    i_e = np.arange(8)


    labelu = "S0_2Dv1_static_0"
    labelm = "S0_3D_static_0"

    res_dir  = f"./results/"

    fem_resu = eit.load_res(label=labelu,res_dname=res_dir)
    fem_resm = eit.load_res(label=labelm,res_dname=res_dir)
    l_res = eit.eit_results_list(results=[fem_resu, fem_resm])
    print(l_res.shape==l_res.v_eit(i_res=None, i_e=i_e).shape)
    print(l_res.v_eit(i_res=0, i_e=i_e).shape)
    print(l_res.dv_eit(i_res=0, i_e=i_e).shape)


    
    print("all ok")
    # new_t = eit.synchronize_times(fem_resu, fem_resm)

    
    # print(new_t)
    # print(fem_resu.shape, fem_resm.shape, new_t.shape)
    # print("m nerve sim time :", fem_resu['computation_time'], "s")
    # dv = fem_resu.dv_eit(t=new_t, i_e=i_e) - fem_resm.dv_eit(t=new_t, i_e=i_e)
    # fig, axs = plt.subplots(3, figsize=(12,6))
    # fem_resu.plot(axs[0], i_e=i_e, which="dv_eit", color="r", marker=".")
    # fem_resm.plot(axs[1], i_e=i_e, which="dv_eit", color="b", marker=".")
    # axs[2].plot(new_t, dv,".-")
    # axs[0].set_ylabel("$dV_{EIT}$ (V)")
    # axs[1].set_ylabel("$dV_{EIT}$ (V)")
    # axs[2].set_ylabel("$V_{REC}$ (mV)")
    # axs[2].set_xlabel("time (ms)")




    # plt.show()