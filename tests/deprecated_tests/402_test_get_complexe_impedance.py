# deprecated since at least v1.2.2
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 4 

# add path to nrvdev (remove ater realese)
import nrv

if __name__ == "__main__":
    test_num = "402"
    fig_file = f"./unitary_tests/figures/{test_num}_"

    def compute_Z(fc, g):
        return lambda f: 1/(g*(1+1j*f/fc))


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
    f_umem = u_res["f_mem"][C]
    t = u_res["t"]


    i_max = np.argmax(g_umem)
    f_umem_0 = f_umem[0]
    f_umem_max = f_umem[i_max]

    Z_umem0 = compute_Z(f_umem[0], g_umem[0])

    freq = np.logspace(-3,5, 100)
    Yu2 = abs(u_res.get_membrane_complexe_admitance(freq, x=Lu/2, t=2, unit="S/m"))
    Yu0 = abs(u_res.get_membrane_complexe_admitance(freq, x=Lu/2, t=0, unit="S/m"))

    print(np.allclose(1/Z_umem0(freq), u_res.get_membrane_complexe_admitance(freq, x=Lu/2, t=0, unit="S/cm**2")))


    #################
    # Myelinated axon
    #################

    ax_m = nrv.myelinated(d=dm,L=Lm,model=mmod,Nseg_per_sec=Nseg_per_sec, rec="all")
    ax_m.insert_I_Clamp_node(1, t_start+0.7, duration, amplitude)


    m_res = ax_m.simulate(dt=dt, t_sim=t_sim, record_particles=True, record_g_ions=True, record_g_mem=True)

    del ax_m
    C = m_res.find_central_index()
    x_C = m_res.find_central_node_coordinate()
    m_res.compute_f_mem()
    V_mmem = m_res["V_mem"][C]
    g_mmem = m_res["g_mem"][C]
    f_mmem = nrv.from_nrv_unit(m_res["f_mem"][C], "Hz")
    t = m_res["t"]

    i_max = np.argmax(g_mmem)
    f_mmem_0 = f_mmem[0]
    f_mmem_max = f_mmem[i_max]


    Ym2 = abs(m_res.get_membrane_complexe_admitance(freq, x=x_C, t=2, unit="S/m"))
    Ym0 = abs(m_res.get_membrane_complexe_admitance(freq, x=x_C, t=0, unit="S/m"))

    plt.figure()
    plt.loglog(freq, 1/Yu0, "r")
    plt.loglog(freq, 1/Yu2, ":r")

    plt.loglog(freq, 1/Ym0, "b")
    plt.loglog(freq, 1/Ym2, ":b")
    plt.savefig(fig_file+"A.png")

    Yu2 = abs(u_res.get_membrane_complexe_admitance(freq, x=Lu/2, t=2, unit="S/m"))
    Yu0 = abs(u_res.get_membrane_complexe_admitance(freq, x=Lu/2, t=0, unit="S/m"))



    ###################
    ##### Nerve #######
    ###################
    outer_d = 5 # mm
    nerve_d = 300 # um
    nerve_l = 5100 # um

    fasc1_d = 250 # um
    fasc1_y = 0
    fasc1_z = 0
    n_ax1 = 5

    t_sim, dt = 10, 0.001

    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d, t_sim=t_sim, dt=dt)

    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax1, percent_unmyel=1, M_stat="Ochoa_M", U_stat="Ochoa_U",)

    fascicle_1 = nrv.fascicle(ID=0)      #we can add diameter here / no need to call define_circular_contour (not tested)
    fascicle_1.define_circular_contour(fasc1_d)
    fascicle_1.fill_with_population(axons_diameters, axons_type, fit_to_size=True,delta=5)
    fascicle_1.generate_random_NoR_position()
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_1.plot(ax)
    fig.savefig(fig_file+"B.png")


    t_start = 1
    duration = 0.2
    amplitude = 5
    nerve_1.insert_I_Clamp(0, t_start, duration, amplitude)
    fasc_dic = nerve_1.save(save=False, intracel_context=True)

    res_nrv = nerve_1.simulate(save_path="", sample_dt=2*dt,postproc_script="sample_g_mem", record_g_mem=True, return_parameters_only=False, save_results=False)




    Ynrv0 = []
    Ynrv2 = []
    t1 = 1
    t2 = 5
    i_x_rec = res_nrv["fascicle0"]["axon0"]["g_mem"].shape[0]//2
    x_rec = nerve_l/2
    for f in freq:
        Ynrv0 += [abs(res_nrv.get_membrane_complexe_admitance(f, x=x_rec, t=t1, unit="S/m"))]
        Ynrv2 += [abs(res_nrv.get_membrane_complexe_admitance(f, x=x_rec, t=t2, unit="S/m"))]

    Ynrv0 = np.array(Ynrv0)
    Ynrv2 = np.array(Ynrv2)

    T = np.arange(len(res_nrv.fascicle0.axon0.t))

    get_sigma_c_t = lambda i_t: np.concatenate([[res_nrv[f_key][a_key]["g_mem"][i_x_rec, i_t] for a_key in res_nrv[f_key].get_axons_key()] for f_key in res_nrv.get_fascicle_key()])
    c = ["b", "y", "r", "g", "k"]

    for i in range(4):
        plt.figure(3)
        plt.plot(res_nrv.fascicle0.axon0.t[T], get_sigma_c_t(T)[i,:], color=c[i])
        plt.plot([t1],[res_nrv.get_membrane_conductivity(x_rec, t1)[i]], "o", color=c[i])
        plt.plot([t2],[res_nrv.get_membrane_conductivity(x_rec, t2)[i]], "o", color=c[i])

        plt.figure(4)
        plt.loglog(freq, 1/Ynrv0[:,i], color=c[i])
        plt.loglog(freq, 1/Ynrv2[:,i], ":", color=c[i])

    plt.figure(3)
    plt.savefig(fig_file+"C.png")
    plt.figure(4)
    plt.savefig(fig_file+"D.png")

