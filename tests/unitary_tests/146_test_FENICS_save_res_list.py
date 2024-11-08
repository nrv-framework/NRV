import nrv
import time
from tqdm import tqdm

if __name__ == "__main__":
    nrv.parameters.set_nrv_verbosity(2)

    ## Set parameters
    filename = "./unitary_tests/sources/127_mesh"
    fname0 = "./unitary_tests/sources/131_0.csv"
    fname1 = "./unitary_tests/sources/131_1.csv"
    fnameres = "./unitary_tests/results/outputs/146_res"

    param = nrv.FEMParameters(D=3, mesh_file=filename)
    param.add_domain(mesh_domain=0,mat_pty="saline")
    param.add_domain(mesh_domain=2,mat_pty=1)
    param.add_domain(mesh_domain=12,mat_pty=fname0)

    param.add_domain(mesh_domain=1000,mat_pty=fname0)
    N_elec = 4
    for i_elec in range(N_elec):
        param.add_domain(mesh_domain=100+(2*i_elec),mat_pty=1)


    t1 = time.time()

    param.add_boundary(mesh_domain=1, btype="Dirichlet", value=0, variable=None, ID=0)

    for i_elec in range(N_elec):
        param.add_boundary(mesh_domain=101 + (2*i_elec), btype="Neuman", value=None, variable="E"+str(i_elec))


    data = param.save()
    jstim = 20

    ## Test modify domain FEM
    sim1 = nrv.FEMSimulation(data=data, elem=("Lagrange", 1))
    res = []
    elec = {"E0":jstim, "E1":0, "E2":0, "E3":0}
    for i in tqdm(range(4)):
        elec["E"+str(i%4)] = jstim
        elec["E"+str((i-1)%4)] = 0
        sim1.setup_sim(**elec)
        res += [sim1.solve()]
        E11_ref = round(sim1.get_domain_potential(101), 6)

    nrv.save_sim_res_list(sim_res_list=res, fname=fnameres)
