import nrv.eit as eit
import matplotlib.pyplot as plt

__fname__ = __file__[__file__.find("tests/")+6:]
test_id = __fname__[:__fname__.find("_")]

use_filter = True

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    src_f = [f"./sources/REC_{i}_fem.json" for i in range(3,6)]
    overwrite_rfile = False

    r_list = eit.eit_results_list(results=src_f, include_rec=True)
    print(r_list.has_nerve_res, r_list["v_rec"].shape)
    print(r_list.has_nerve_res, r_list.get_res(which="v_rec").shape)
    reccap_ppt = r_list.get_reccap_ppt()

    _which="v_rec"

    fig, axs = plt.subplots(len(src_f))
    i_e=8
    for i_r_ in range(len(src_f)):
        ax = axs[i_r_]
        expr=eit.get_query(**{"i_res":i_r_, "mye_cap":0})
        sub_df = reccap_ppt.query(expr)
        i_tu = sub_df["i_start"].min(), sub_df["i_stop"].max()
        t_u = r_list["t"][slice(*i_tu)]
        expr=eit.get_query(**{"mye_cap":1, "i_res":i_r_})
        sub_df = reccap_ppt.query(expr)
        i_tm = sub_df["i_start"].min(), sub_df["i_stop"].max()
        t_m = r_list["t"][slice(*i_tm)]
        t_ = r_list["t"]
        dv_pc = r_list.get_res(i_res=i_r_, i_e=i_e,which=_which).squeeze()
        dv_pc_avg = r_list.mean(i_res=i_r_, i_e=i_e, which=_which).squeeze()
        dv_pc_std = .5*r_list.std(i_res=i_r_, i_e=i_e, which=_which).squeeze()
        std_1= dv_pc_avg + dv_pc_std
        std_2= dv_pc_avg - dv_pc_std
        ax.plot(t_, dv_pc_avg, color="k", alpha=1)
        ax.fill_between(t_, dv_pc_avg-dv_pc_std,dv_pc_avg+dv_pc_std, color="k", alpha=.2)
        ax.plot(t_, dv_pc.T, color="k", alpha=.1)
        # ax.set_ylim(-25e-6,0)

        dv_pc = r_list.get_res(i_res=i_r_, i_e=i_e, i_t=i_tu, which=_which).squeeze()
        dv_pc_avg = r_list.mean(i_res=i_r_, i_e=i_e, i_t=i_tu, which=_which).squeeze()
        dv_pc_std = .5*r_list.std(i_res=i_r_, i_e=i_e, i_t=i_tu, which=_which).squeeze()
        std_1= dv_pc_avg + dv_pc_std
        std_2= dv_pc_avg - dv_pc_std
        ax.plot(t_u, dv_pc_avg, color="r", alpha=1)
        ax.fill_between(t_u, dv_pc_avg-dv_pc_std,dv_pc_avg+dv_pc_std, color="r", alpha=.2)
        ax.plot(t_u, dv_pc.T, color="r", alpha=.1)
        # ax_u.set_ylim(-25e-6,0)

        dv_pc = r_list.get_res(i_res=i_r_, i_e=i_e, i_t=i_tm, which=_which).squeeze()
        dv_pc_avg = r_list.mean(i_res=i_r_, i_e=i_e, i_t=i_tm, which=_which).squeeze()
        dv_pc_std = .5*r_list.std(i_res=i_r_, i_e=i_e, i_t=i_tm, which=_which).squeeze()
        std_1= dv_pc_avg + dv_pc_std
        std_2= dv_pc_avg - dv_pc_std
        ax.plot(t_m, dv_pc_avg, color="b", alpha=1)
        ax.fill_between(t_m, dv_pc_avg-dv_pc_std,dv_pc_avg+dv_pc_std, color="b", alpha=.2)
        ax.plot(t_m, dv_pc.T, color="b", alpha=.1)
        ax.axvline(r_list["t"][757])
    # ax_m.set_ylim(-25e-6,0)
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")

    # plt.show()