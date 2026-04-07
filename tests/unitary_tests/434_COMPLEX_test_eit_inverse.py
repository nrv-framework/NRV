import sys
sys.path.append("/Users/thomascouppey/_offline/Codes/Libraries/NRV")
import nrv
import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]
nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
res_dir  = f"./unitary_tests/results/outputs/"

if __name__ == "__main__":
    print(eit.static_env)

    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3

    # -------------------------- #
    # ------- PARAMETERS ------- #
    # -------------------------- #

    # Nerve definition
    outer_d = 5     # mm
    nerve_d = 105  # um
    nerve_l = 15010  # um
    percent_unmyel = .7
    unmyelinated_nseg = 3000

    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d, postproc_label="sample_keys", record_g_mem=True)

    # Adding first fascicle
    n_ax1=30
    fasc1_d = (40, 60)   # um
    fasc1_y = 25     # um
    fasc1_z = 0     # um
    fascicle_1 = nrv.fascicle(diameter=fasc1_d, ID=1, unmyelinated_nseg=unmyelinated_nseg)
    fascicle_1.fill(n_ax=n_ax1, percent_unmyel=percent_unmyel, M_stat="Ochoa_M", U_stat="Ochoa_U", fit_to_size=False,delta=.5, delta_trace=3)
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

    # Adding second fascicle
    n_ax2=10
    fasc2_d = 30   # um
    fasc2_y = -20     # um
    fasc2_z = -10     # um
    fascicle_2 = nrv.fascicle(diameter=fasc2_d, ID=2, unmyelinated_nseg=unmyelinated_nseg)
    fascicle_2.fill(n_ax=n_ax2, percent_unmyel=percent_unmyel, M_stat="Ochoa_M", U_stat="Ochoa_U", fit_to_size=False,delta=.5, delta_trace=3)
    nerve_1.add_fascicle(fascicle=fascicle_2, y=fasc2_y, z=fasc2_z)

    nerve_data = nerve_1.save(save=False)

    fig, ax = plt.subplots(figsize=(6, 6))
    nerve_1.plot(ax)

    del nerve_1

    # EIT protocol
    n_proc_global = 3 


    l_elec = 1000 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    n_fem_step = 10*n_proc_global
    freqs = [1-3, 1, 1e3]

    dt_fem = [
        (2, .75),
        (7,.4),
        (-1,.75),
            ]

    n_elec = 16


    sigma_method = "mean"
    inj_protocol_type = "simple"
    use_gnd_elec = True
    parameters = {
    "x_rec":x_rec,
    "dt_fem":dt_fem,
    "freqs":freqs,
    "inj_protocol_type":inj_protocol_type,
    "n_proc_global":n_proc_global,
    "l_elec":l_elec,
    "i_drive":i_drive,
    "sigma_method":sigma_method,
    "use_gnd_elec":use_gnd_elec,
    "n_elec":n_elec,
    }

    # -------------------------- #
    # ------- SIMULATION ------- #
    # -------------------------- #

    eit_instance = eit.EIT2DProblem(nerve_data, res_dname=res_dir, label=test_id, **parameters)
    ## Nerve simulation
    sim_param = {"t_sim":t_sim}
    nrn_res = eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param, fasc_list=[1])
    fig, ax = plt.subplots(figsize=(6, 6))
    nrn_res.plot_recruited_fibers(ax)
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")


    ## Impedance simulation
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()

    # Simulate nerve
    fem_res = eit_instance.simulate_eit()
    pat = fem_res["p"][0]
    dv_pc = fem_res.dv_eit(i_p=0)

    fig = plt.figure()
    _, axs2 = eit.utils.gen_fig_elec(n_e=fem_res.n_e, fig=fig, )

    eit.utils.add_nerve_plot(axs=axs2, data=nerve_data, drive_pair=pat)
    eit.utils.plot_all_elec(axs=axs2, t=fem_res.t(), res_list=dv_pc,)
    eit.utils.scale_axs(axs=axs2, e_gnd=[0], has_nerve=True)
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")


    # -------------------------- #
    # ----- RECONSTRUCTION ----- #
    # -------------------------- #

    inv_pb = eit.pyeit_inverse(data=fem_res)

    print(fem_res.v_eit(i_t=0,signed=True).shape)
    plt.figure()
    plt.plot(fem_res.v_eit(i_t=0,i_f=0,signed=True))

    plt.xlabel("# drive electrode pair")
    plt.ylabel("voltage (V)")
    plt.title("Single ended measurements")
    plt.figure()
    plt.plot(inv_pb.fromat_data())
    plt.xlabel("# drive electrode pair")
    plt.ylabel("voltage (V)")
    plt.title("Diferentrial measurements")

    _dv = fem_res.dv_eit(i_e=fem_res.n_e//2, i_p=0,)

    i_tmax = np.argmax(np.abs(_dv))

    ds = inv_pb.solve(i_t=i_tmax, i_f=0)[0]

    fig, ax2 = plt.subplots(figsize=(11, 9))

    inv_pb.plot(ax=ax2, i_t=i_tmax, filter=eit.utils.thr_window)