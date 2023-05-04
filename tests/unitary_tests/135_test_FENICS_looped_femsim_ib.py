import nrv
import time

nrv.NRV_param.set_nrv_verbosity(2)

## Set parameters
filename = "./unitary_tests/sources/127_mesh"
fname0 = './unitary_tests/sources/131_0.csv'
fname1 = './unitary_tests/sources/131_1.csv'


param = nrv.SimParameters(D=3, mesh_file=filename)
param.add_domain(mesh_domain=0,mat_pty="saline")
param.add_domain(mesh_domain=2,mat_pty=1)
param.add_domain(mesh_domain=12,mat_pty=fname0)

param.add_domain(mesh_domain=1000,mat_pty=fname0)
N_elec = 4
for i_elec in range(N_elec):
    param.add_domain(mesh_domain=100+(2*i_elec),mat_pty=1)


t1 = time.time()
E = 0
E_ = 4
Eref = 2

param.add_boundary(mesh_domain=101 + Eref, btype='Dirichlet', value=0, variable=None, ID=0)
param.add_boundary(mesh_domain=101 + E_, btype='Neuman', value=None, variable='jstim', ID=1)
param.add_boundary(mesh_domain=101 + E, btype='Neuman', value=None, variable='_jstim', ID=2)
param.add_inboundary(mesh_domain=13,mat_pty="perineurium", thickness=5, in_domains=[12, 1000])

data = param.save_SimParameters()
jstim = 20





## Test modify domain FEM

sim1 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim1.prepare_sim(jstim=jstim, _jstim=-jstim)
sim1.solve()
E1_ref = round(sim1.get_domain_potential(101), 6)

param.add_domain(mesh_domain=12,mat_pty=fname1)
param.add_domain(mesh_domain=2,mat_pty=100)
param.add_inboundary(mesh_domain=13,mat_pty=0.003, thickness=5, in_domains=[12, 1000])
sim2 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim2.prepare_sim(jstim=jstim, _jstim=-jstim)
sim2.solve()
E2_ref = round(sim2.get_domain_potential(101), 6)


param.add_domain(mesh_domain=12,mat_pty=fname0)
param.add_domain(mesh_domain=2,mat_pty=1)
param.add_inboundary(mesh_domain=13,mat_pty="perineurium", thickness=5, in_domains=[12, 1000])
sim3 = nrv.FEMSimulation(data=data, elem=('Lagrange', 1))
sim3.prepare_sim(jstim=jstim, _jstim=-jstim)
sim3.solve()
E1 = round(sim3.get_domain_potential(101), 6)
print(E1_ref == E1)
sim3.add_domain(mesh_domain=12,mat_pty=fname1)
sim3.add_domain(mesh_domain=2,mat_pty=100)
sim3.add_inboundary(mesh_domain=13,mat_pty=0.003, thickness=5, in_domains=[12, 1000])

sim3.prepare_sim(jstim=jstim, _jstim=-jstim)
sim3.solve()
E2 = round(sim3.get_domain_potential(101), 6)

print(not E1_ref == E2_ref)
print(E1_ref == E1)
print(E2_ref == E2)

## Test looped FEM
# With ibound

param.add_domain(mesh_domain=12,mat_pty=1000)
sim1 = nrv.FEMSimulation(data=param.save_SimParameters(), elem=('Lagrange', 1))
sim1.prepare_sim(jstim=jstim, _jstim=-jstim)
sim1.solve()
E1_ref = round(sim1.get_domain_potential(101), 6)

param.add_domain(mesh_domain=12,mat_pty=0.01)
sim2 = nrv.FEMSimulation(data=param.save_SimParameters(), elem=('Lagrange', 1))
sim2.prepare_sim(jstim=jstim, _jstim=-jstim)
sim2.solve()
E2_ref = round(sim2.get_domain_potential(101), 6)

ilim = 90
test = True
i = 0
while test and i < ilim/2: 
    i+=1
    print(" "+str(i)+ "/"+str(ilim//2), end="\r")
    sim1.add_domain(mesh_domain=12,mat_pty=1000)
    #sim1.prepare_sim(jstim=jstim, _jstim=-jstim)
    sim1.solve()
    test = (E1_ref == round(sim1.get_domain_potential(101), 6))
    sim1.add_domain(mesh_domain=12,mat_pty=0.01)
    #sim1.prepare_sim(jstim=jstim, _jstim=-jstim)
    sim1.solve()
    test = test and (E2_ref == round(sim1.get_domain_potential(101), 6))
print()
print(E1_ref != E2_ref)
print(test)



