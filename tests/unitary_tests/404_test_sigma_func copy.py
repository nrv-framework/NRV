import nrv
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys

import pyeit.eit.jac as jac
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh

test_num = "404"
mesh_file = f"./unitary_tests/results/mesh/{test_num}_mesh"
sim_file = "./unitary_tests/results/outputs/" + test_num + "_simres"
fig_file = f"./unitary_tests/figures/{test_num}_"

dir_res = "./unitary_tests/figures/"

sig_cst = 0.2

## Generate the nerve 
nerve_d = 100
nerve_l = nrv.get_length_from_nodes(10, 3)
nerve = nrv.nerve(Length=nerve_l, D=nerve_d)
nerve.set_ID(test_num)


fascicle = nrv.fascicle()
# 1 axon fascicle
fascicle.define_circular_contour(D=30,y_c=20)
fasc_dic = fascicle.save(save=False, intracel_context=True)
nerve.add_fascicle(fasc_dic, ID=1, intracel_context=True)

if nrv.MCH.do_master_only_work():
    ## Generate the mesh from the nerve
    n_elec = 8
    j_stim = 1e-6

    mesh1 = nrv.mesh_from_nerve(nerve=nerve)
    mesh1.add_electrode(elec_type="CUFF MP", N=n_elec,  x_c=nerve_l/2, contact_length=nerve_l/3, is_volume=False)
    mesh1.compute_mesh()
    mesh1.save(save=True, fname=mesh_file)



    ## Setup the FEMsimulation
    sim1 = nrv.FEMSimulation(D=3, mesh=mesh1, elem=("Lagrange", 2))
    sim1.add_domain(mesh_domain=0,mat_pty="saline")
    sim1.add_domain(mesh_domain=2,mat_pty="perineurium")
    sim1.add_domain(mesh_domain=10,mat_pty=sig_cst)

    # Boundaries Conditions
    sim1.add_boundary(mesh_domain=1, btype='Dirichlet', value=0)
    sim1.add_boundary(mesh_domain=101, btype="Neuman", variable="E0")
    sim1.add_boundary(mesh_domain=105, btype="Neuman", variable="E1")
    nrv.check_sim_dom(sim=sim1, mesh=mesh1)

    V1 = np.zeros(n_elec, dtype=float)
    sim1.setup_sim(E0=j_stim, E1=-j_stim)
    fem_res1 = sim1.solve()
    for i_elec in range(n_elec):
        e_dom = nrv.ENT_DOM_offset["Surface"] + nrv.ENT_DOM_offset["Electrode"]+2*i_elec
        V1[i_elec] = sim1.get_domain_potential(e_dom)
    del sim1


    X_ = np.linspace(0, nerve_l, 100, dtype=float)
    Y_ = sig_cst * np.ones(100, dtype=float)
    sigma_fct = nrv.mat_from_interp(X_, Y_)

    sim2 = nrv.FEMSimulation(D=3, mesh=mesh1, elem=("Lagrange", 2))
    sim2.add_domain(mesh_domain=0,mat_pty="saline")
    sim2.add_domain(mesh_domain=2,mat_pty="perineurium")
    sim2.add_domain(mesh_domain=10,mat_pty=sigma_fct)

    # Boundaries Conditions
    sim2.add_boundary(mesh_domain=1, btype='Dirichlet', value=0)
    sim2.add_boundary(mesh_domain=1, btype='Dirichlet', value=0)
    sim2.add_boundary(mesh_domain=101, btype="Neuman", variable="E0")
    sim2.add_boundary(mesh_domain=105, btype="Neuman", variable="E1")

    nrv.check_sim_dom(sim=sim2, mesh=mesh1)
    V2 = np.zeros(n_elec, dtype=float)
    sim2.setup_sim(E0=j_stim, E1=-j_stim)
    fem_res1 = sim2.solve()
    for i_elec in range(n_elec):
        e_dom = nrv.ENT_DOM_offset["Surface"] + nrv.ENT_DOM_offset["Electrode"]+2*i_elec
        V2[i_elec] = sim2.get_domain_potential(e_dom)
    del sim2

    print(np.allclose(V1, V2))
    plt.plot((V1-V2)/V1)
    plt.show()



