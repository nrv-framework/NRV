import nrv
import time
import os
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":

    ## Results filenames
    N_test = "163"
    mesh_file = "./unitary_tests/results/mesh/" + N_test + "_mesh"
    sim_file = "./unitary_tests/results/outputs/" + N_test + "_simres"

    ## Mesh generation
    t1 = time.time()
    L=300#nrv.get_length_from_nodes(10,4)         #um


    nrv.parameters.set_gmsh_ncore(3)
    Outer_D = None    #mm
    Nerve_D = 50 #um


    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
    mesh.reshape_axon(d=10, y=0, z=0, ID=0, myelinated=True,res=3)
    mesh.add_electrode(elec_type="CUFF MP", N=4,  x_c=L/2, contact_length=L/3, is_volume=False)
    mesh.compute_mesh()
    mesh.save(mesh_file)

    t2 = time.time()
    mesh.get_info(verbose=True)


    ax1 = nrv.myelinated(d=10, L=L, rec="all", t_sim=5, Nseg_per_sec=1,record_g_mem=True)

    res = ax1()
    del ax1
    Nnodes = res.axonnodes

    res.compute_f_mem()
    res.get_myelin_properties(endo_mat="endoneurium_bhadra")



    mye = nrv.convert(res.g_mye, "S/cm**2", "S/m**2")
    g_mye = min(mye)
    g_nodes = 0.09

    mat_myel = nrv.mat_from_interp(X=res.x_rec, Y=mye, kind="previous")

    npts = 30000
    X = np.array([[L*x/npts, 4, 0] for x in range(npts)]).T
    sig_nrv = mat_myel.sigma_func(X)

    print('mesh generated in '+str(t2 - t1)+' s')


    sim1 = nrv.FEMSimulation(D=3, mesh=mesh, elem=('Lagrange', 2))
    sim1.add_domain(mesh_domain=2,mat_pty="endoneurium_bhadra")
    sim1.add_domain(mesh_domain=1000,mat_pty=g_mye)
    for i in range(Nnodes):
        id_node = "1000" + str(2*i)
        print(id_node)
        sim1.add_domain(mesh_domain=int(id_node),mat_pty=g_nodes)



    sim1.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)
    #sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim_', ID=1)

    # simulating
    sim1.setup_sim(jstim=1e-3)
    res0 = sim1.solve()

    sim1.add_domain(mesh_domain=10002,mat_pty=0.5*g_nodes)
    sim1.setup_sim(jstim=1e-3)
    # simulating
    res1 = sim1.solve()


    sim1.add_domain(mesh_domain=10002,mat_pty=g_nodes)
    sim1.add_domain(mesh_domain=10004,mat_pty=0.5*g_nodes)
    sim1.setup_sim(jstim=1e-3)
    # simulating
    res2 = sim1.solve()


    X = np.array([[L*x/npts, 0, 0] for x in range(npts)]).T

    plt.figure()
    plt.plot(X[0, :], res0.eval(X.T), label="inactive")
    plt.plot(X[0, :], res1.eval(X.T), label="node 1 active")
    plt.plot(X[0, :], res2.eval(X.T), label="node 2 active")


    resdiff = [res1 - res0]
    resdiff += [res2 - res0]
    nrv.save_sim_res_list(resdiff, sim_file)

    plt.figure()
    plt.plot(X[0, :], resdiff[0].eval(X.T), label="node 1 active")
    plt.plot(X[0, :], resdiff[1].eval(X.T), label="node 2 active")

    # plt.show()
