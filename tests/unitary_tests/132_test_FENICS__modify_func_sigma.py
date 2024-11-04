import nrv
import time


if __name__ == "__main__":
    filename = "./unitary_tests/sources/127_mesh"
    N_elec = 4
    N_ax = 1
    fname0 = './unitary_tests/sources/131_0.csv'
    fname1 = './unitary_tests/sources/131_1.csv'


    param = nrv.FEMParameters(D=3, mesh_file=filename)
    param.add_domain(mesh_domain=0,mat_pty="saline")
    param.add_domain(mesh_domain=2,mat_pty="epineurium")
    param.add_domain(mesh_domain=12,mat_pty=fname0)


    for i_ax in range(N_ax):
        param.add_domain(mesh_domain=1000+(2*i_ax),mat_pty="endoneurium_bhadra")

    for i_elec in range(N_elec):
        param.add_domain(mesh_domain=100+(2*i_elec),mat_pty=1e7)

    #param.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=5, in_domains=[12, 1000])


    t1 = time.time()
    E = 0%(2*N_elec)
    E_ = 4%(2*N_elec)
    Eref = 2%(2*N_elec)

    param.add_domain(mesh_domain=12,mat_pty=fname0)
    param.add_boundary(mesh_domain=101 + Eref, btype='Dirichlet', value=0, variable=None, ID=0)
    param.add_boundary(mesh_domain=101 + E_, btype='Neuman', value=None, variable='jstim', ID=1)
    param.add_boundary(mesh_domain=101 + E, btype='Neuman', value=None, variable='_jstim', ID=2)

    data = param.save()
    #print(data['boundaries'])

    sim1 = nrv.FEMSimulation(data=data, elem=('Lagrange', 2))
    jstim = 20
    sim1.setup_sim(jstim=jstim, _jstim=-jstim)

    res = sim1.solve_and_save_sim("./unitary_tests/results/outputs/132_results1")

    param.add_domain(mesh_domain=12,mat_pty=fname1)
    sim2 = nrv.FEMSimulation(data=data, elem=('Lagrange', 2))
    sim2.setup_sim(jstim=jstim, _jstim=-jstim)
    res -= sim2.solve_and_save_sim("./unitary_tests/results/outputs/132_results2")

    res.save("./unitary_tests/results/outputs/132_results")
    t2 = time.time()
    for E in range(N_elec):
        V1 = round(sim1.get_domain_potential(101+2*E), 2)
        V2 = round(sim2.get_domain_potential(101+2*E), 2)
        print(V1, V2, V1 -V2)
    print('FEM solved in '+str(t2 - t1)+' s')











