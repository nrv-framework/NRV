import nrv
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys

import pyeit.eit.bp as bp
import pyeit.eit.jac as jac
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh

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


test_num = "403"
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
fascicle.define_circular_contour(D=30,y_c=20)

t_start = 1
duration = 0.1
amplitude = 2
fascicle.insert_I_Clamp(0, t_start, duration, amplitude)
fasc_dic = fascicle.save(save=False, intracel_context=True)

nerve = nrv.nerve(Length=nerve_l, D=nerve_d, t_sim=t_sim, dt=dt, Nseg_per_sec=2)
nerve.set_ID(test_num)
nerve.add_fascicle(fasc_dic, ID=1, intracel_context=True)

if nrv.MCH.do_master_only_work():
    ## Generate the mesh from the nerve
    n_elec = 8
    mesh1 = nrv.mesh_from_nerve(nerve=nerve)
    mesh1.add_electrode(elec_type="CUFF MP", N=n_elec,  x_c=nerve_l/2, contact_length=nerve_l/3, is_volume=False)
    mesh1.compute_mesh()
    mesh1.save(save=True, fname=mesh_file)

    ## Setup the FEMsimulation


    sim1 = nrv.FEMSimulation(D=3, mesh=mesh1, elem=("Lagrange", 2))
    sim1.add_domain(mesh_domain=0,mat_pty="saline")
    sim1.add_domain(mesh_domain=2,mat_pty="perineurium")
    sim1.add_domain(mesh_domain=10,mat_pty=0.2)

    # Boundaries Conditions
    sim1.add_boundary(mesh_domain=1, btype='Dirichlet', value=0)
    electrodes = {}
    for E in range(n_elec):
        E_label = "E"+str(E)
        electrodes[E_label] = 0
        e_dom = nrv.ENT_DOM_offset["Surface"] + nrv.ENT_DOM_offset["Electrode"]+2*E
        sim1.add_boundary(mesh_domain=e_dom, btype="Neuman", variable=E_label)
    check_sim_dom(sim=sim1, mesh=mesh1)

    j_stim = 1e-6
    e_offset = 3
    fem_res = []
    V = np.zeros((n_elec, n_elec))
    for i_patern in tqdm(range(n_elec)):
        for E in electrodes:
            if "E"+str(i_patern) == E:
                electrodes[E] = j_stim
            elif "E"+str((i_patern + e_offset)%n_elec) == E:
                electrodes[E] = -j_stim
            else:
                electrodes[E] = 0
        sys.stdout.flush()

        sim1.setup_sim(**electrodes)
        fem_res += [sim1.solve()]
        for i_elec in range(n_elec):
            e_dom = nrv.ENT_DOM_offset["Surface"] + nrv.ENT_DOM_offset["Electrode"]+2*i_elec
            V[i_patern, i_elec] = sim1.get_domain_potential(e_dom)


    sim1.add_domain(mesh_domain=10,mat_pty=1.2)


    V1 = np.zeros((n_elec, n_elec))
    dV1 = np.zeros((n_elec, n_elec))
    for i_patern in tqdm(range(n_elec)):
        for E in electrodes:
            if "E"+str(i_patern) == E:
                electrodes[E] = j_stim
            elif "E"+str((i_patern + e_offset)%n_elec) == E:
                electrodes[E] = -j_stim
            else:
                electrodes[E] = 0
        sys.stdout.flush()

        sim1.setup_sim(**electrodes)
        fem_res += [sim1.solve()]
        for i_elec in range(n_elec):
            e_dom = nrv.ENT_DOM_offset["Surface"] + nrv.ENT_DOM_offset["Electrode"]+2*i_elec
            V1[i_patern, i_elec] = sim1.get_domain_potential(e_dom)


    nrv.save_sim_res_list(fem_res,fname=sim_file)
    plt.figure()
    plt.plot(V)
    plt.plot(V1)


    prot = nrv.simple_pyeit_protocol(n_elec=n_elec, inj_offset=e_offset)-1
    v0 = []
    v1 = []
    for inj, rec in prot:
        print(inj, rec)
        v0 += [V[inj[0], rec[0]] - V[inj[0], rec[1]]]
        v1 += [V1[inj[0], rec[0]] - V1[inj[0], rec[1]]]
    v0 = np.array(v0)
    v1 = np.array(v1)
    mesh_obj = mesh.create(n_elec, h0=0.05)
    protocol_obj = protocol.create(n_elec, dist_exc=e_offset, step_meas=1, parser_meas="std")
    eit = jac.JAC(mesh_obj, protocol_obj)
    eit.setup(p=0.50, lamb=1e-3, method="kotre")
    # the normalize for BP when dist_exc>4 should always be True
    ds = eit.solve(v1, v0, normalize=True)



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
    #plt.show()



