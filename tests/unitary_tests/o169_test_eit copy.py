import nrv
import numpy as np
import matplotlib.pyplot as plt

def check_sim_dom(sim:nrv.FEMSimulation, mesh:nrv.NerveMshCreator):
    uset_dom = []
    mdom = mesh.domains_3D
    if sim.D == 2:
        mdom = mesh.domains_2D

    for i in mdom:
        if not i in sim.domains_list:
            uset_dom += [i]
    if len(uset_dom):
        print(f"Warning: the following domains are not set {uset_dom}")


test_num = "169"
mesh_file = f"./unitary_tests/results/mesh/{test_num}_mesh"
sim_file = "./unitary_tests/results/outputs/" + test_num + "_simres"
dir_res = "./unitary_tests/figures/"
## Generate the nerve 
t_sim, dt = 10, 0.005
fascicle = nrv.fascicle()
fascicle.set_axons_parameters()
nerve_d = 100
nerve_l = nrv.get_length_from_nodes(10, 3)
# 1 axon fascicle
fascicle.axons_diameter = np.asarray([10])
fascicle.axons_type = np.asarray([1])
#fascicle.NoR_relative_position = np.asarray([0.5])
fascicle.axons_y = np.asarray([0])
fascicle.axons_z = np.asarray([0])
fascicle.define_circular_contour(D=50)

t_start = 1
duration = 0.1
amplitude = 2
fascicle.insert_I_Clamp(0, t_start, duration, amplitude)
fasc_dic = fascicle.save(save=False, intracel_context=True)

nerve = nrv.nerve(Length=nerve_l, D=nerve_d, t_sim=t_sim, dt=dt, Nseg_per_sec=2)
nerve.set_ID(test_num)
nerve.add_fascicle(fasc_dic, ID=1, intracel_context=True)


## Simulate the nerve to compute g_mem
res = nerve.simulate(save_path=dir_res, postproc_script="save_gmem", record_g_mem=True, return_parameters_only=False)


if nrv.MCH.do_master_only_work():
    plt.plot(res.fascicle1.axon0['t'], res.fascicle1.axon0['g_mem'].T)


    ## Generate the mesh from the nerve
    n_elec = 8
    mesh = nrv.mesh_from_nerve(nerve=nerve)
    mesh.add_electrode(elec_type="CUFF MP", N=n_elec,  x_c=nerve_l/2, contact_length=nerve_l/3, is_volume=False)
    mesh.compute_mesh()
    mesh.save(save=True, fname=mesh_file)

    ## Setup the FEMsimulation
    """
    for i_fasc in nerve.fascicles:
        for i_ax in range(n_ax):
            fgx = nrv.rmv_ext(param['fgx']) + str(i_ax)+".csv"
            X_sigma += [np.loadtxt(fgx, delimiter=",")]
    """

    g_mye_mat = nrv.material()
    g_mye_mat.set_isotropic_conductivity(sigma=0.001)
    g_node_t0 = res.fascicle1.axon0['g_mem'][:,0]

    sim1 = nrv.FEMSimulation(D=3, mesh=mesh, elem=('Lagrange', 2))
    sim1.add_domain(mesh_domain=0,mat_pty="saline")
    sim1.add_domain(mesh_domain=2,mat_pty="perineurium")
    sim1.add_domain(mesh_domain=10,mat_pty="endoneurium_bhadra")
    sim1.add_domain(mesh_domain=1000,mat_pty="endoneurium_bhadra")
    for i_ax, ax in mesh.axons.items():
        print(ax["n_nodes"])
        for i_node in range(ax["n_nodes"]):
            id_node = "1000" + str(2*i_node)
            print(id_node)
            sim1.add_domain(mesh_domain=int(id_node),mat_pty=g_node_t0[i_node])
    electrodes = {}
    for E in range(n_elec):
        E_label = "E"+str(E)
        electrodes[E_label] = 0
        e_dom = nrv.ENT_DOM_offset['Surface'] + nrv.ENT_DOM_offset['Electrode']+2*E
        sim1.add_boundary(mesh_domain=e_dom, btype='Neuman', variable=E_label)
    check_sim_dom(sim=sim1, mesh=mesh)

    jstim = 1e-3
    electrodes["E1"] = jstim
    electrodes["E4"] = - jstim

    sim1.setup_sim(**electrodes)
    res = sim1.solve()

    res.save(file=sim_file)
    plt.show()
    