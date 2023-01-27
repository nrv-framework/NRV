import nrv
import time

out_file = './unitary_tests/results/outputs/106_simfile.xdmf'

param = nrv.SimParameters(D=3, mesh_file="unitary_tests/sources/3cylinder")
"""
param.add_domain(mesh_domain=0,mat_file="material_1")
param.add_domain(mesh_domain=100,mat_file="material_2")
param.add_domain(mesh_domain=200,mat_file="material_1")
"""
param.add_domain(mesh_domain=0,mat_file=1)
param.add_domain(mesh_domain=100,mat_file="material_2")
param.add_domain(mesh_domain=200,mat_file=[1, 1, 1])

param.add_boundary(mesh_domain=11, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=22, btype='Neuman', value=None, variable='jstim')

data = param.save_SimParameters()

sim1 = nrv.FEMSimulation(elem=('Lagrange', 1), data=data)


jstim = 1
sim1.prepare_sim(jstim=jstim)
t1 = time.time()
sim1.solve_and_save_sim(out_file)

t2 = time.time()
print('solved in '+str(t2 - t1)+' s')