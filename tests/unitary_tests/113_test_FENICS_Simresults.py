import nrv
import numpy as np
from dolfinx import io
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/113_mesh"
out_file = "./unitary_tests/results/outputs/113_simfile"

## Mesh creation
is_mesh = False

if not is_mesh:
    t0 = time.time()
    L=15000         #um
    Outer_D = 15    #mm
    Nerve_D = 5000  #um

    size_elec = (1000, 500)
    #
    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

    mesh.reshape_outerBox(res=2000)
    mesh.reshape_nerve(res=500)

    mesh.reshape_fascicle(D=2000, y_c=1000, z_c=0, ID=1, res=100)


    mesh.add_electrode(elec_type="CUFF MEA", N=5, x_c=L/2, y_c=0, z_c=0, size = size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)

    mesh.compute_mesh()



    mesh.save(mesh_file)
    #mesh.visualize()
    del mesh

    t1 = time.time()
    print(t1-t0)
else:
    t1 = time.time()

## first FEM Simulation 
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")
param.add_domain(mesh_domain=12,mat_file="silicone")


param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")
param.add_domain(mesh_domain=108,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='jstim')
param.add_boundary(mesh_domain=107, btype='Neuman', value=None, variable='_jstim')

data = param.save()
#print(data)
sim1 = nrv.FEMSimulation(data=data)


jstim = 20
sim1.setup_sim(jstim=jstim, _jstim=-jstim)

res1 = sim1.solve_and_save_sim(out_file)



t2 = time.time()
print('FEM 1 solved in '+str(t2 - t1)+' s')

## second FEM Simulation 
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")
param.add_domain(mesh_domain=12,mat_file="platinum")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")
param.add_domain(mesh_domain=108,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='jstim')
param.add_boundary(mesh_domain=107, btype='Neuman', value=None, variable='_jstim')

data = param.save()
#print(data)
sim2 = nrv.FEMSimulation(data=data)
sim2.setup_sim(jstim=jstim, _jstim=-jstim)

res2 = sim2.solve()

t3 = time.time()
print('FEM 2 solved in '+str(t3 - t2)+' s')

## third FEM Simulation 
sim3 = nrv.FEMSimulation(data=data)
sim3.setup_sim(jstim=jstim, _jstim=-jstim)
res3 = sim3.solve()

t4 = time.time()
print('FEM 3 solved in '+str(t4 - t3)+' s')

## test simresult operations
u = res1 - res2
t5 = time.time()

print('Substraction done in '+str(t5 - t4)+' s')

print(np.shape(res2.vector()))
print(res1 != res2)
print(res2 == res3)
print(res3 == 2 * res2 - res2)

