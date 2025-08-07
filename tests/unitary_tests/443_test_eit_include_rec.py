import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
from time import perf_counter
from scipy.signal import savgol_filter, lfilter

__fname__ = __file__[__file__.find("tests/")+6:]
test_id = __fname__[:__fname__.find("_")]

use_filter = True

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    src_f = [f"./sources/REC_{i}_fem.json" for i in range(3,5)]
    overwrite_rfile = False

    r_list = eit.eit_results_list(results=src_f, include_rec=True)
    print(r_list.has_nerve_res, r_list["v_rec"].shape)
    print(r_list.has_nerve_res, r_list.get_res(which="v_rec").shape)
    r_list.get_reccap_ppt()

    figbplot = eit.Figure_elec(n_e=16, figsize=(10,9))
    figbplot.add_nerve_plot(data=nerves_fname, drive_pair=(0,5))
    figbplot.plot_all_elec(data=r_list, which="v_rec", i_res=[0,1,3])
    figbplot.scale_axs()
    
    i_e = 4
    fig, ax = plt.subplots()

    figu, axu = plt.subplots()
    figm, axm = plt.subplots()
    stim_duration=.2
    t_stim = 0.
    dt = r_list.dt
    c = ["r","g", "b", "orange"]
    for _i_r in range(4):
        v_rec = r_list.get_res(which="v_rec", i_e=i_e, i_res=_i_r).squeeze()
        ax.plot(r_list["t"], v_rec,color=c[_i_r],alpha=.2)

        i_offset_m = int((t_stim + stim_duration) / dt) + 1 
        _v_rec_nrm = v_rec[i_offset_m:].copy()
        _v_rec_nrm /= -_v_rec_nrm.min()
        i_t_m = np.argwhere(_v_rec_nrm<-0.05).squeeze()
        if len(i_t_m)==0:
            print("No mylinated cap detected")
        di_t_m= np.diff(i_t_m[:-1], prepend=-1,append=0)
        
        i_cut = np.squeeze(np.where(di_t_m!=1))
        print(i_cut)
        if not np.iterable(i_cut):
            i_start_m,i_stop_m = i_t_m[0], i_t_m[i_cut]
        else:
            i_start_m, i_stop_m = i_t_m[i_cut[:2]]
        i_start_m += i_offset_m
        i_stop_m += i_offset_m
        print(i_start_m, i_stop_m)
        i_t_min, i_t_max = np.argmin(v_rec[i_start_m:i_stop_m])+i_start_m, np.argmax(v_rec[i_start_m:i_stop_m])+i_start_m
        i_cap = i_start_m,i_t_min, i_t_max,i_stop_m
        print(i_cap)
        axm.plot(r_list["t"][i_offset_m:], _v_rec_nrm)


        r_u = Rectangle((r_list["t"][i_cap[0]], v_rec[i_cap[2]]), r_list["t"][i_cap[3]]-r_list["t"][i_cap[0]], v_rec[i_cap[1]]-v_rec[i_cap[2]], color=(0,0,.9,.2))
        ax.add_artist(r_u)

        i_start = np.argwhere(v_rec[i_cap[-1]:]>0)[0][0]+i_cap[-1]
        dv_rec_dt = np.diff(v_rec[i_start:])
        dv_rec_dt_f = savgol_filter(dv_rec_dt, 1000, 3)
        dv_rec_dt_f /= np.max(abs(dv_rec_dt_f))
        t_ = r_list["t"][i_start+1:]
        axu.plot(t_, dv_rec_dt/np.max(abs(dv_rec_dt)) ,color=c[_i_r],alpha=0.2)
        axu.plot(t_, dv_rec_dt_f, "--",color=c[_i_r],alpha=0.5)
        figu.savefig(f"figures/{test_id}_B.pdf")

        if use_filter:
            dv_rec_dt = dv_rec_dt_f
        else:
            dv_rec_dt /= np.max(abs(dv_rec_dt)) 

        i_t_u = np.argwhere(dv_rec_dt>0.05).squeeze()+i_start
        i_t_start, i_t_stop = i_t_u[0], i_t_u[-1]
        print(i_t_start, i_t_stop, i_t_u)
        i_t_min, i_t_max = np.argmin(v_rec[i_t_start:i_t_stop])+i_t_start, np.argmax(v_rec[i_t_start:i_t_stop])+i_t_start
        i_cap = i_t_start,i_t_min, i_t_max,i_t_stop
        print(i_cap)




        r_u = Rectangle((r_list["t"][i_cap[0]], v_rec[i_cap[2]]), r_list["t"][i_cap[3]]-r_list["t"][i_cap[0]], v_rec[i_cap[1]]-v_rec[i_cap[2]], color=(.9,0,0,.2))
        ax.add_artist(r_u)


        


    plt.show()
