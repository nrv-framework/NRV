import nrv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 4 

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]
if __name__ == "__main__":
    # add path to nrvdev (remove ater realese)
    fig_file = f"./unitary_tests/figures/{test_id}_"

    # myelinated specific
    du = 1
    Lu = 1000
    Nrec = 200
    umod = "Rattay_Aberham"

    # myelinated specific
    dm=10
    Lm=nrv.get_length_from_nodes(dm, 15)
    Nseg_per_sec = 2
    mmod = "MRG"
    # AP pties
    t_start = 1
    duration = 0.5
    amplitude = 1

    t_sim = 20
    dt = 0.001

    ###################
    # Unmyelinated axon
    ###################
    ax_u = nrv.unmyelinated(d=du,L=Lu,model=umod,Nsec=Nrec)
    ax_u.insert_I_Clamp(0, t_start, duration, amplitude)


    u_res = ax_u.simulate(dt=dt, t_sim=t_sim, record_particles=True, record_g_ions=True, record_g_mem=True)

    del ax_u
    C = u_res.find_central_index()
    u_res.compute_f_mem()
    V_umem = u_res["V_mem"][C]
    g_umem = u_res["g_mem"][C]
    f_umem = nrv.from_nrv_unit(u_res["f_mem"][C], "Hz")
    t = u_res["t"]
    x_rex = u_res["x_rec"]
    mat = u_res.get_membrane_material(t=2.5)
    

    x_ = np.linspace(0,Lu, 100)
    x_plot = np.vstack((x_, 0*x_, 0*x_))

    plt.figure()
    plt.plot(x_plot[0,:], mat.sigma_func(x_plot))
    plt.savefig(fig_file+"D_tocheck.png")


    i_max = np.argmax(g_umem)
    f_umem_0 = f_umem[0]
    f_umem_max = f_umem[i_max]



    print(u_res.get_membrane_conductivity(Lu/2, 2), "S/cm-2")
    print(u_res.get_membrane_conductivity(Lu/2, 2)*7e-7, "S/cm")
    print(u_res.get_membrane_conductivity(Lu/2, 2, unit="S/cm"), "S/m")
    print(u_res.get_membrane_conductivity(Lu/2, 2, unit="S/m"), "S/m")

    #################
    # Myelinated axon
    #################

    ax_m = nrv.myelinated(d=dm,L=Lm,model=mmod,Nseg_per_sec=Nseg_per_sec, rec="all")
    ax_m.insert_I_Clamp_node(1, t_start+0.7, duration, amplitude)


    m_res = ax_m.simulate(dt=dt, t_sim=t_sim, record_particles=True, record_g_ions=True, record_g_mem=True)

    del ax_m
    C = m_res.find_central_index()
    x_C = m_res["x_rec"][C]
    m_res.compute_f_mem()
    V_mmem = m_res["V_mem"][C]
    g_mmem = m_res["g_mem"][C]
    f_mmem = nrv.from_nrv_unit(m_res["f_mem"][C], "Hz")
    t = m_res["t"]

    i_max = np.argmax(g_mmem)
    f_mmem_0 = f_mmem[0]
    f_mmem_max = f_mmem[i_max]




    fig1, axs = plt.subplots()
    axs.plot(t, g_umem, color="r")
    axs.plot([1], [u_res.get_membrane_conductivity(Lu/2, 1)], "o",color="r")
    axs.plot([2], [u_res.get_membrane_conductivity(Lu/2, 2)], "o",color="r")
    axs.plot([3], [u_res.get_membrane_conductivity(Lu/2, 3)], "o",color="r")
    axs.plot([4], [u_res.get_membrane_conductivity(Lu/2, 4)], "o",color="r")

    axs.set_yscale("log")
    axs.set_xlim((0,5))
    #axs[0].set_xticklabels([])
    axs.set_yticklabels([])

    axs.plot(t, g_mmem, color="b")
    axs.plot([1], [m_res.get_membrane_conductivity(x_C, 1)], "o",color="b")
    axs.plot([2], [m_res.get_membrane_conductivity(x_C, 2)], "o",color="b")
    axs.plot([3], [m_res.get_membrane_conductivity(x_C, 3)], "o",color="b")
    axs.plot([4], [m_res.get_membrane_conductivity(x_C, 4)], "o",color="b")
    fig1.savefig(fig_file+"A.png")




    ###################
    ##### Nerve #######
    ###################
    outer_d = 5 # mm
    nerve_d = 300 # um
    nerve_l = 5100 # um

    fasc1_d = 250 # um
    fasc1_y = 0
    fasc1_z = 0
    n_ax1 = 10

    t_sim, dt = 10, 0.001

    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d, t_sim=t_sim, dt=dt)

    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax1, percent_unmyel=1, M_stat="Ochoa_M", U_stat="Ochoa_U",)

    fascicle_1 = nrv.fascicle(ID=0)      #we can add diameter here / no need to call define_circular_contour (not tested)
    fascicle_1.define_circular_contour(fasc1_d)
    fascicle_1.fill_with_population(axons_diameters, axons_type, fit_to_size=True,delta=5)
    fascicle_1.generate_random_NoR_position()
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

    fig2, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_1.plot(ax)
    fig2.savefig(fig_file+"B.png")


    t_start = 1
    duration = 0.2
    amplitude = 5
    nerve_1.insert_I_Clamp(0, t_start, duration, amplitude)
    fasc_dic = nerve_1.save(save=False, intracel_context=True)

    pp_kwgs = {"sample_dt":2*dt}

    res_nrv = nerve_1.simulate(save_path="",postproc_script="sample_g_mem", record_g_mem=True, return_parameters_only=False, save_results=False)



    i_x_rec = res_nrv.unmyelinated_nseg//3
    T = np.arange(len(res_nrv.fascicle0.axon0.t))

    get_sigma_c_t = lambda i_t: np.concatenate([[res_nrv[f_key][a_key]["g_mem"][i_x_rec, i_t] for a_key in res_nrv[f_key].get_axons_key()] for f_key in res_nrv.get_fascicle_key()])


    fig3, ax = plt.subplots(1, 1)
    g_t_4 = res_nrv.get_membrane_conductivity(nerve_l/3, 4)
    c = ["b", "y", "r", "g", "k"]
    for i in range(4):
        plt.plot(res_nrv.fascicle0.axon0.t[T], get_sigma_c_t(T)[i,:], color=c[i])


        ax.plot([3],[res_nrv.get_membrane_conductivity(nerve_l/3, 3)[i]], "o", color=c[i])
        ax.plot([4],[res_nrv.get_membrane_conductivity(nerve_l/3, 4)[i]], "o", color=c[i])
        ax.plot([5],[res_nrv.get_membrane_conductivity(nerve_l/3, 5)[i]], "o", color=c[i])
        ax.plot([6],[res_nrv.get_membrane_conductivity(nerve_l/3, 6)[i]], "o", color=c[i])

    ax.set_yscale("log")
    fig3.savefig(fig_file+"C.png")


    print(u_res.get_membrane_capacitance(), "uF/cm2")
    print(m_res.get_membrane_capacitance(), "uF/cm2")
    print(res_nrv.get_membrane_capacitance(), "uF/cm2")

    print(u_res.get_membrane_capacitance("F/m"), "F/m")
    print(m_res.get_membrane_capacitance("F/m"), "F/m")
    print(res_nrv.get_membrane_capacitance("F/m"), "F/m")
    # plt.show()
