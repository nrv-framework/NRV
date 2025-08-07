import nrv
import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
from copy import deepcopy

import pyeit.eit.jac as jac
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":

    # nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    figdir = f"./figures/{test_id}_"

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3


    l_fem = 1000 # um
    l_elec = 300 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    n_fem_step = 10*n_proc_global
    # dt_fem = [
    #     (2.5, .5),
    #     (8,.1),
    #     (-1,.5),
    #         ]# ms

    dt_fem = [
        (2.5, .75),
        (8,.4),
        (-1,.75),
            ]# ms

    n_elec = 16


    sigma_method = "mean"
    inj_protocol_type = "simple"
    use_gnd_elec = True
    parameters = {"x_rec":x_rec,
    "dt_fem":dt_fem,
    "inj_protocol_type":inj_protocol_type,
    "n_proc_global":n_proc_global,
    "l_elec":l_elec,
    "l_fem":l_fem,
    "i_drive":i_drive,
    "sigma_method":sigma_method,
    "use_gnd_elec":use_gnd_elec,
    "n_elec":n_elec,
    }

    ne = nrv.load_nerve(nerves_fname)
    # ne.fascicles["1"].define_circular_contour(15)
    # ne.define_circular_contour(20)
    ne.fascicles["1"].axons_y += 30
    fig, ax = plt.subplots()

    ne.plot(ax)
    fig.savefig(figdir+"A.png")
    nerves_fname = ne.save(save=False)
    del ne


    eit_instance = eit.EIT2DProblem(nerves_fname, res_dname=res_dir, label=test_id, **parameters)


    ## Nerve simulation
    sim_param = {"t_sim":t_sim}
    nrn_res =eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)


    ## Impedance simulation
    eit_instance._define_problem()
    # Build mesh
    eit_instance.build_mesh()

    # Simulate nerve
    fem_res = eit_instance.simulate_eit()

    if n_elec in [8, 16]:
        fig = plt.figure(figsize=(20, 9))#, layout="constrained")
        subfigs = fig.subfigures(n_elec//4, 4)
        axs = np.array([])
        for i_p, pat in enumerate(fem_res["p"]):
            dv_pc = fem_res.dv_eit(i_p=i_p)#, signed=True)
            _, axs2 = eit.gen_fig_elec(n_e=fem_res.n_e, fig=subfigs[i_p//4, i_p%4], small_fig=True)
            eit.add_nerve_plot(axs=axs2, data=nerves_fname, drive_pair=pat)
            eit.plot_all_elec(axs=axs2, t=fem_res.t(), res_list=dv_pc,)
            axs = np.concatenate([axs, axs2[1:-1]])

            eit.scale_axs(axs=axs2, e_gnd=[0], has_nerve=True)
        fig.savefig(f"./unitary_tests/figures/{test_id}_A.pdf")


    def extract_pyEIT_meas(res:eit.eit_class_results, i_t:int=0, i_f:int=0, verbose:bool=False)->np.ndarray:
        if not res.is_multi_patern:
            return None
        i_p0 = res["p"][0]
        i_off = i_p0[1] - i_p0[0]
        if i_off < 0:
            i_off += res.n_e
        if i_off == 1:
            i_e_skiped = 2
        else:
            i_e_skiped = 3
        n_rec_per_inj = res.n_e - (i_e_skiped + 1)
        v_forward = np.zeros(res.n_e * n_rec_per_inj)

        i_rec = np.arange(n_rec_per_inj)
        mask = (i_e_skiped-1)*(1+i_rec>=(i_off-1))

        for i_p, (i_ep, i_en) in enumerate(res["p"]):
            i_e2 = np.sort((1 + i_ep + i_rec + mask) % res.n_e)
            i_e1 = (i_e2+1)% res.n_e
            if verbose:
                for _i in range(n_rec_per_inj):
                    print((i_ep, i_en), (i_e1[_i], i_e2[_i]))

            v_forward[i_p*n_rec_per_inj : (i_p+1)*n_rec_per_inj] = (
                res.v_eit(i_t=i_t, i_f=i_f, i_p=i_p, i_e=i_e1, signed=True) -
                res.v_eit(i_t=i_t, i_f=i_f, i_p=i_p, i_e=i_e2, signed=True)
            )
        return v_forward


    extract_pyEIT_meas(res=fem_res)

    print(fem_res["v_eit_phase"],)
    print(fem_res.v_eit(i_t=0,signed=True).shape)
    plt.figure()
    plt.plot(fem_res.v_eit(i_t=0,signed=True))

    plt.xlabel("# electrod")
    plt.ylabel("voltage (V)")
    plt.title("Single ended measurements")
    plt.figure()
    plt.plot(extract_pyEIT_meas(fem_res))
    plt.xlabel("# electrod pair")
    plt.ylabel("voltage (V)")
    plt.title("Diferentrial measurements")

    _dv = fem_res.dv_eit(i_e=fem_res.n_e//2, i_p=0,)

    i_tmax = np.argmax(np.abs(_dv))

    print(f"t_max={fem_res["t"][i_tmax]}ms, (i_tmax={i_tmax})")

    v0 = extract_pyEIT_meas(res=fem_res, i_t=0)
    v1 = extract_pyEIT_meas(res=fem_res, i_t=i_tmax)

    fig, axs = plt.subplots(2)
    axs[0].plot(v0, "-o")
    axs[0].plot(v1, "-o")

    axs[1].plot(v1-v0)


    mesh_obj = mesh.create(fem_res.n_e, h0=0.025)
    protocol_obj = protocol.create(fem_res.n_e, dist_exc=5, step_meas=1, parser_meas="std")


    eit_invers = jac.JAC(mesh_obj, protocol_obj)
    eit_invers.setup(p=0.50, lamb=1e-3, method="kotre")
    ds = eit_invers.solve(v1, v0, normalize=True)


    # extract node, element, alpha
    pts = mesh_obj.node
    tri = mesh_obj.element

    # draw
    fig = plt.figure(figsize=(11, 9))
    # reconstructed
    ax2 = plt.subplot(111)
    im = ax2.tripcolor(pts[:, 0], pts[:, 1], tri, ds)
    ax2.axis("equal")
    # fig.savefig('../doc/images/demo_bp.png', dpi=96)
    fig.colorbar(im)
    #plt.savefig(DIR_res+"reconstruction.png", dpi=500)
    plt.tight_layout()
    fig.savefig(figdir+"B.png")

    def filt(X, alpha=.4): 
        thr = X.max()*alpha
        _X = deepcopy(X)
        print(thr)
        _X[_X < thr] *= 0
        return _X
    print(ds)
    ds_filtred = filt(ds)
    # draw
    fig = plt.figure(figsize=(11, 9))
    # reconstructed
    ax2 = plt.subplot(111)
    im2 = ax2.tripcolor(pts[:, 0], pts[:, 1], tri, ds_filtred)
    ax2.axis("equal")
    # fig.savefig('../doc/images/demo_bp.png', dpi=96)
    _cb = fig.colorbar(im2)
    #plt.savefig(DIR_res+"reconstruction.png", dpi=500)
    plt.tight_layout()
    fig.savefig(figdir+"C.png")
