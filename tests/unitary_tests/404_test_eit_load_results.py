import eit
import matplotlib.pyplot as plt
import numpy as np
test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    i_e = np.arange(2)


    labelu = "02"
    labelm = "03"

    res_dir  = f"./unitary_tests/results/{labelu}/"
    fem_resu = eit.eit_class_results(data=f"{res_dir}/{labelu}_fem.json")
    res_dir  = f"./unitary_tests/results/{labelm}/"
    fem_resm = eit.eit_class_results(data=f"{res_dir}/{labelm}_fem.json")
    print("m nerve sim time :", fem_resu['computation_time'], "s")
    fig, axs = plt.subplots(3, 2, figsize=(12,6))
    fem_resu.plot(axs[0,0], i_e=i_e, which="v_eit", color="r", marker=".")
    fem_resu.plot(axs[1,0], i_e=i_e, which="dv_eit", color="r", marker=".")
    fem_resu.plot(axs[2,0], i_e=i_e, which="v_rec", color="r")
    axs[0,0].set_ylabel("$V_{EIT}$ (V)")
    axs[1,0].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,0].set_ylabel("$V_{REC}$ (mV)")
    axs[2,0].set_xlabel("time (ms)")



    print("m nerve sim time :", fem_resm['computation_time'], "s")
    fem_resm.plot(axs[0,1], i_e=i_e, which="v_eit", color="b", marker=".")
    fem_resm.plot(axs[1,1], i_e=i_e, which="dv_eit", color="b", marker=".")
    fem_resm.plot(axs[2,1], i_e=i_e, which="v_rec", color="b")
    axs[0,1].set_ylabel("$V_{EIT}$ (V)")
    axs[1,1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,1].set_ylabel("$V_{REC}$ (mV)")
    axs[2,1].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_m1_nerve.pdf")

    plt.show()