import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    src_f = [f"./sources/SA_{i}_fem.json" for i in range(3)]
    overwrite_rfile = False

    r_list = eit.eit_results_list(results=src_f)
    i_r_ = np.arange(r_list.shape[0])
    cap_mask = r_list.get_cap_mask(i_res=i_r_)
    cap_i_t = r_list.get_cap_i_t(i_res=i_r_)
    cap_i_t_lim = r_list.get_cap_i_t_lim(i_res=i_r_)
    print(cap_i_t_lim)
    cap_i_t_lim_u = r_list.get_cap_i_t_lim(i_res=i_r_, i_cap=0)
    print(cap_i_t_lim_u)
    cap_i_t_lim_m = r_list.get_cap_i_t_lim(i_res=i_r_, i_cap=1)
    print(cap_i_t_lim_m)

    labels = [r["label"] for r in r_list.res_info.values()]

    __which="dv_eit_pc"
    dv_pc = r_list.get_res(i_res=i_r_, which=__which)
    dv_pc_cap, t_cap = r_list.get_cap_res(i_res=[1,2], which=__which, with_t=True)

    print(f"dv_pc {dv_pc.shape}")
    print(f"dv_pc_cap {dv_pc_cap.shape}")
    figdvpc_ = eit.Figure_elec(n_e=16, figsize=(10,9))
    figdvpc_.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figdvpc_.plot_all_elec(t=r_list.t(), data=dv_pc, i_res=i_r_,)

    figdvpc_.plot_all_elec(t=t_cap, data=dv_pc_cap, i_res=i_r_, linestyle="--")
    figdvpc_.fig.savefig(f"./unitary_tests/figures/{test_id}_A.pdf")

    dv_pc_capm, t_capm = r_list.get_cap_res(i_res=[1,2], which=__which, with_t=True, expr={"i_cap":0,"":"duration < 1."})
    dv_pc_capm15, t_capm15 = r_list.get_cap_res(i_res=[1,2], which=__which, with_t=True, expr={"i_e":[3,4], "i_cap":0}, ext_factor=1.5)

    figemye = eit.Figure_elec(n_e=16, figsize=(10,9))
    figemye.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figemye.plot_all_elec(t=t_capm15, data=dv_pc_capm15, i_res=i_r_, linestyle="--")
    figemye.plot_all_elec(t=t_capm, data=dv_pc_capm, i_res=i_r_, linestyle="--")
    figemye.fig.savefig(f"./unitary_tests/figures/{test_id}_B.pdf")



    dv_pc_capu, t_capu = r_list.get_cap_res(i_res=None, which=__which, with_t=True, expr={"i_cap":1,"":"duration > 2."})
    dv_pc_capu15, t_capu15 = r_list.get_cap_res(i_res=None, which=__which, with_t=True, expr={"i_e":[3,4], "i_cap":1}, ext_factor=1.5)
    print(dv_pc_capu.shape, t_capu.shape)
    print(dv_pc_capu15.shape, t_capu15.shape)
    # dv_pc_capumean, t_capu15 = r_list.mean(i_res=[1,2], which=__which+"_cap", expr={"i_e":[3,4], "i_cap":1},ext_factor=1.5)

    figeunm = eit.Figure_elec(n_e=16, figsize=(10,9))
    figeunm.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figeunm.plot_all_elec(t=t_capu15, data=dv_pc_capu15, i_res=i_r_, linestyle="--")
    figeunm.plot_all_elec(t=t_capu, data=dv_pc_capu, i_res=i_r_, linestyle="--")
    figeunm.fig.savefig(f"./unitary_tests/figures/{test_id}_C.pdf")

    # figemye.plot_all_elec(t=t_capu15, data=dv_pc_capumean, i_res=i_r_, color="k",linestyle="-")

    plt.show()
