import eit as eit
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from time import perf_counter

__fname__ = __file__[__file__.find("tests/")+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./nerves/u1_nerve.json"
    res_dir  = f"./results/{test_id}/"
    src_f = [f"./sources/SA_{i}_fem.json" for i in range(3)]
    overwrite_rfile = False

    r_list = eit.eit_results_list(results=src_f)
    i_r_ = np.arange(r_list.shape[0])

    t0 = perf_counter()
    cap_ppt=r_list.get_acap_v_ppt(i_res=None)
    t1 = perf_counter()
    print(cap_ppt)


    fig, axs = plt.subplots(1,2, layout="constrained")
    sns.boxplot(ax=axs[0],data=cap_ppt, x="i_e", y="duration", hue="i_cap", fill=True)
    sns.boxplot(ax=axs[1],data=cap_ppt, x="i_e", y="dv_pc_min", hue="i_cap", fill=True)
    fig.savefig(f"figures/{test_id}_A.pdf")



    _expr = eit.get_query(i_cap=0, _="duration < 1.")


    figbplot = eit.Figure_elec(n_e=16, figsize=(10,9))
    figbplot.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figbplot.boxplot(data=cap_ppt, expr="", hue="i_cap", y="dv_pc_min", palette=["#0000ee", "#ee0000"])
    figbplot.scale_axs(zerox=True)

    figbplot = eit.Figure_elec(n_e=16, figsize=(10,9))
    figbplot.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figbplot.boxplot(data=cap_ppt, expr="", hue="i_cap", y="duration", palette=["r", "b"])
    figbplot.scale_axs(zerox=True)

    figbplot.fig.savefig(f"figures/{test_id}_B.pdf")

    dv_pc_capu15, t_capu15 = r_list.get_cap_res(i_res=None, which="dv_eit_pc", with_t=True, expr={"i_e":[3,4], "i_cap":1}, ext_factor=1.5)
    dv_pc_capm15, t_capm15 = r_list.get_cap_res(i_res=None, which="dv_eit_pc", with_t=True, expr={"i_e":[3,4], "i_cap":0}, ext_factor=1.5)
    fig2 = eit.Figure_elec(n_e=16, figsize=(10,9))
    fig2.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    fig2.plot_all_elec(t=t_capu15, data=dv_pc_capu15, i_res=None, linestyle="--", color="r")
    fig2.plot_all_elec(t=t_capm15, data=dv_pc_capm15, i_res=None, linestyle="--", color="b")
    fig2.scale_axs(zerox=True)
    fig2.fig.savefig(f"figures/{test_id}_C.pdf")
    

    plt.show()