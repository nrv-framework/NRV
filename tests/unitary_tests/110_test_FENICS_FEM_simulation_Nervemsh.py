import nrv
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/110_mesh"
out_file = "./unitary_tests/results/outputs/110_simfile"

## Mesh creation
t1 = time.time()

L=15000         #um
Outer_D = 10    #mm
Nerve_D = 5000 #um

size_elec = (1000, 500)

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

mesh.reshape_nerve(res=400)


mesh.add_electrode(elec_type="CUFF MEA", N=4, x_c=L/2, y_c=0, z_c=0, size = size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)

mesh.compute_mesh()
#mesh.save(mesh_file)
#mesh.visualize()

#del mesh

t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')

## FEM Simulation
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0)
param.add_boundary(mesh_domain=103, btype='Neuman', variable='jstim')
param.add_boundary(mesh_domain=107, btype='Neuman', variable='_jstim')

data = param.save()
sim1 = nrv.FEMSimulation(data=data, mesh=mesh)


jstim = 2e-3
sim1.setup_sim(jstim=jstim, _jstim=-jstim)

sim1.solve_and_save_sim(out_file)

t3 = time.time()
print('FEM solved in '+str(t3 - t2)+' s')



