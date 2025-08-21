import nrv.eit as eit
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"

    res_fname  = f"./unitary_tests/sources/SA_1_fem.json"
    fem_res = eit.results.eit_forward_results(data=res_fname)

    print("m nerve sim time :", fem_res['computation_time'], "s")
    i_e = np.arange(8)
    t =  fem_res.t()
    v_elecs = fem_res.v_eit(i_e=i_e)
    dv_elecs = fem_res.dv_eit(i_e=i_e)

    fig, axs = plt.subplots(3, 2, figsize=(12,6))
    axs[0,0].plot(t, v_elecs, ".-")
    axs[1,0].plot(t, dv_elecs, ".-")
    axs[2,0].plot(fem_res["t_rec"], fem_res["v_rec"][:,0], color="r")
    axs[0,0].set_ylabel("$V_{EIT}$ (V)")
    axs[1,0].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,0].set_ylabel("$V_{REC}$ (mV)")
    axs[2,0].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")

    t = fem_res.t(dt=0.1)
    v_elecs = fem_res.v_eit(t, i_e=i_e)
    dv_elecs = fem_res.dv_eit(t, i_e=i_e, pc=True)
    v_rec = fem_res.v_rec(t, i_e=i_e)

    axs[0,1].plot(t, v_elecs, ".-")
    axs[1,1].plot(t, dv_elecs, ".-")
    axs[2,1].plot(t, v_rec, ".-")


    axs[0,1].set_ylabel("$V_{EIT}$ (V)")
    axs[1,1].set_ylabel("$dV_{EIT}$ (V)")
    axs[2,1].set_ylabel("$V_{REC}$ (mV)")
    axs[2,1].set_xlabel("time (ms)")
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    del fem_res
