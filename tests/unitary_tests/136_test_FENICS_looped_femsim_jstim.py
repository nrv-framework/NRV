import nrv
import time

nrv.parameters.set_nrv_verbosity(2)

## Set parameters
filename = "./unitary_tests/sources/127_mesh"
fname0 = './unitary_tests/sources/131_0.csv'
fname1 = './unitary_tests/sources/131_1.csv'


param = nrv.FEMParameters(D=3, mesh_file=filename)
param.add_domain(mesh_domain=0,mat_pty="saline")
param.add_domain(mesh_domain=2,mat_pty=1)
param.add_domain(mesh_domain=12,mat_pty=fname0)

param.add_domain(mesh_domain=1000,mat_pty=fname0)
N_elec = 4
for i_elec in range(N_elec):
    param.add_domain(mesh_domain=100+(2*i_elec),mat_pty=1)


t1 = time.time()

param.add_boundary(mesh_domain=1, btype='Dirichlet', value=0, variable=None, ID=0)

for i_elec in range(N_elec):
    param.add_boundary(mesh_domain=101 + (2*i_elec), btype='Neuman', value=None, variable='E'+str(i_elec))


data = param.save()
jstim = 20

## Test modify domain FEM

sim1 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim1.setup_sim(E0=jstim, E1=0, E2=-jstim, E3=0)
sim1.solve()
E11_ref = round(sim1.get_domain_potential(101), 6)


sim2 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim2.setup_sim(E0=-jstim, E1=0, E2=jstim, E3=0)
sim2.solve()
E12_ref = round(sim2.get_domain_potential(101), 6)
print(E11_ref, E12_ref)

sim3 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim3.setup_sim(E0=jstim, E1=0, E2=-jstim, E3=0)
sim3.solve()
E11 = round(sim3.get_domain_potential(101), 6)
sim3.setup_sim(E0=-jstim, E1=0, E2=jstim, E3=0)
sim3.solve()
E12 = round(sim3.get_domain_potential(101), 6)

print(not E11_ref == E12_ref)
print(E11_ref == E11)
print(E12_ref == E12)


# With ibound
param.add_inboundary(mesh_domain=13,mat_pty="perineurium", thickness=5, in_domains=[12, 1000])

data = param.save()

sim1 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim1.setup_sim(E0=jstim, E1=0, E2=-jstim, E3=0)
sim1.solve()
E11_ref = round(sim1.get_domain_potential(101), 6)


sim2 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim2.setup_sim(E0=-jstim, E1=0, E2=jstim, E3=0)
sim2.solve()
E12_ref = round(sim2.get_domain_potential(101), 6)
print(E11_ref, E12_ref)

sim3 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim3.setup_sim(E0=jstim, E1=0, E2=-jstim, E3=0)
sim3.solve()
E11 = round(sim3.get_domain_potential(101), 6)
sim3.setup_sim(E0=-jstim, E1=0, E2=jstim, E3=0)
sim3.solve()
E12 = round(sim3.get_domain_potential(101), 6)

print(not E11_ref == E12_ref)
print(E11_ref == E11)
print(E12_ref == E12)
