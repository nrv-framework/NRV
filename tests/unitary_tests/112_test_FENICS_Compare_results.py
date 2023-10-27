import nrv
from dolfinx import fem, io
import time
import numpy as np

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/112_mesh"
out_file1 = "./unitary_tests/results/outputs/112_simfile1"
out_file2 = "./unitary_tests/results/outputs/112_simfile2"
out_file = "./unitary_tests/results/outputs/112_simfile.xdmf"

## Mesh creation
is_mesh = False

if not is_mesh:
    t0 = time.time()
    L=7500         #um
    Outer_D = 15    #mm
    Nerve_D = 5000  #um

    size_elec = (1000, 500)
    #
    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

    mesh.reshape_outerBox(res=2000)
    mesh.reshape_nerve(res=500)
    mesh.reshape_fascicle(D=2000, y_c=1000, z_c=0, ID=1, res=100)
    #mesh.reshape_axon(D=5, y_c=1200, z_c=100, ID=1, res=2)
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
param.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")
param.add_domain(mesh_domain=1002,mat_file="silicone")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")
param.add_domain(mesh_domain=108,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='jstim')
param.add_boundary(mesh_domain=107, btype='Neuman', value=None, variable='_jstim')

data = param.save_SimParameters()
print(data)
sim1 = nrv.FEMSimulation(data=data)


jstim = 20
sim1.prepare_sim(jstim=jstim, _jstim=-jstim)


sim1.solve_and_save_sim(out_file1)

t2 = time.time()
print('FEM 1 solved in '+str(t2 - t1)+' s')

## second FEM Simulation 
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")
param.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")
param.add_domain(mesh_domain=1002,mat_file="platinum")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")
param.add_domain(mesh_domain=108,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='jstim')
param.add_boundary(mesh_domain=107, btype='Neuman', value=None, variable='_jstim')

data = param.save_SimParameters()
print(data)
sim2 = nrv.FEMSimulation(data=data)


jstim = 20
sim2.prepare_sim(jstim=jstim, _jstim=-jstim)


sim2.solve_and_save_sim(out_file2)

t3 = time.time()
print('FEM 2 solved in '+str(t3 - t2)+' s')


## Result comparison
vout2_expr = fem.Expression(sim2.vout, sim1.V.element.interpolation_points())
vout2 = fem.Function(sim1.V)
vout2.interpolate(vout2_expr)

u_expr = fem.Expression(sim1.vout-vout2, sim1.V.element.interpolation_points())
u = fem.Function(sim1.V)
u.interpolate(u_expr)


with io.XDMFFile(sim1.domain.comm, out_file, "w") as file:
    file.write_mesh(sim1.domain)
    file.write_function(u)


t4 = time.time()
print('Substraction done in '+str(t4 - t3)+' s')

#print(sim1.vout.x.array[:])
#print(sim2.vout.x.array[:])
print(np.allclose(sim1.vout.x.array, sim2.vout.x.array))