import nrv
import time
import os
import matplotlib.pyplot as plt
import numpy as np
if __name__ == "__main__":
    ## Results filenames
    N_test = "160"
    mesh_file = "./unitary_tests/results/mesh/" + N_test + "_mesh"
    sigma_file = "./unitary_tests/results/outputs/" + N_test + "_sigma"
    sim_file = "./unitary_tests/results/outputs/" + N_test + "_simres"




    nrv.parameters.set_gmsh_ncore(3)
    ## Mesh generation
    t1 = time.time()
    L=nrv.get_length_from_nodes(10,3)         #um

    ax1 = nrv.myelinated(d=10, L=L, rec="all", t_sim=5, Nseg_per_sec=1,record_g_mem=True)

    res = ax1()
    del ax1
    res.compute_f_mem()
    res.get_myelin_properties(endo_mat="endoneurium_bhadra")


    mye = res.g_mye # S.cm-2

    mye = nrv.to_nrv_unit(mye,"S/cm**2")
    mye = nrv.from_nrv_unit(mye,"S/m**2")
    #mye = np.array([0.2 for _ in range(len(mye))])
    lab = [res.get_index_myelinated_sequence(x) for x in range(len(res.x_rec))]
    xlim = (0.95*L/2, 1.05*L/2)
    plt.xticks(ticks=res.x_rec, labels=lab, rotation=90)
    plt.xlim(xlim)
    plt.twiny()
    plt.plot(res.x_rec, [1 for _ in res.x_rec], '|', markersize=300)
    plt.xlim((0.95*L/2, 1.05*L/2))


    mat_myel = nrv.mat_from_interp(X=res.x_rec, Y=mye, kind="previous")

    npts = 30000
    X = np.array([[L*x/npts, 4, 0] for x in range(npts)]).T
    sig_nrv = mat_myel.sigma_func(X)

    Outer_D = None    #mm
    Nerve_D = 100 #um

    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

    #mesh.reshape_fascicle(d=700, y_c=0, z_c=0, ID=0)

    mesh.reshape_axon(d=10*0.6, y=0, z=0, ID=0, res=3)
    mesh.reshape_axon(d=10, y=0, z=0, ID=1, res=3)


    mesh.add_electrode(elec_type="CUFF MP", N=4,  x_c=L/2, contact_length=100, is_volume=False)
    mesh.compute_mesh()

    mesh.save(mesh_file)

    t2 = time.time()
    mesh.get_info(verbose=True)
    print('mesh generated in '+str(t2 - t1)+' s')

    param = nrv.FEMParameters(D=3, mesh_file=mesh_file)
    param.add_domain(mesh_domain=2,mat_pty="epineurium")
    #param.add_domain(mesh_domain=10,mat_pty="endoneurium_ranck")
    param.add_domain(mesh_domain=1000,mat_pty="endoneurium_bhadra")
    data = param.save()

    sig_sim = nrv.FEMSimulation(D=3, data=data, mesh_file=mesh_file, mesh=mesh, elem=('DG', 2))
    sig_sim.add_domain(mesh_domain=1002,mat_pty=mat_myel)
    sigma = []
    fig, axs = plt.subplots(2)

    for order in [1, 2, 3, 4]:
        sigma += sig_sim.compute_conductance(order=order)

        sig_fen = sigma[order-1].eval(X.T)
        axs[0].plot(X[0, :], sig_fen, label="FEM interpolation " + str(order))
        axs[1].plot(X[0, :], sig_fen, label="FEM interpolation " + str(order))
    axs[0].plot(X[0, :], sig_nrv, "--k", label="NRV interpolation")
    axs[1].plot(X[0, :], sig_nrv, "--k", label="NRV interpolation")
    axs[1].plot(res.x_rec, [sig_nrv[0] for _ in res.x_rec], '|', markersize=300)
    lab = [res.get_index_myelinated_sequence(x) for x in range(len(res.x_rec))]
    axs[1].set_xticks(ticks=res.x_rec, labels=lab, rotation=90)
    axs[1].set_xlim((0.995*L/2, 1.005*L/2))

    nrv.save_sim_res_list(sigma, sigma_file)
    plt.legend()

    del sig_sim

    sim2 = nrv.FEMSimulation(D=3, data=data, mesh_file=mesh_file, mesh=mesh, elem=('Lagrange', 2))
    sim2.add_domain(mesh_domain=1002,mat_pty=mat_myel)
    sim2.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim2.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)

    sim2.setup_sim(jstim=100)
    #print(sim2.a)
    res2 = sim2.solve()

    sim1 = nrv.FEMSimulation(D=3, data=data, mesh=mesh, elem=('Lagrange', 2))
    # Adding internal boundaries
    sim1.add_domain(mesh_domain=1002,mat_pty=0.2e7)
    sim1.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)
    #sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim_', ID=1)

    # simulating
    sim1.setup_sim(jstim=100)
    #print(sim1.a)
    res1 = sim1.solve()
    del sim1



    resdiff = res2 - res1
    print(not np.allclose(res1.vector, res2.vector))
    resdiff.save(sim_file)

    #plt.show()
