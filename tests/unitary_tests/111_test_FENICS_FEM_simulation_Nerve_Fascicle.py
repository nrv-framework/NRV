import nrv
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/111_mesh"
out_file = "./unitary_tests/results/outputs/111_simfile"

## Mesh creation
is_mesh = False
if not is_mesh:
    t1 = time.time()

    L=5000         #um
    Outer_D = 10    #mm
    Nerve_D = 5000  #um

    size_elec = (1000, 500)
    #
    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

    mesh.reshape_nerve(res=500)

    mesh.reshape_fascicle(D=2000, y_c=1000, z_c=0, ID=1, res=100)
    mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2)

    #mesh.reshape_axon(D=10, y_c=1100, z_c=200, ID=1, res=3)



    mesh.add_electrode(elec_type="CUFF MEA", N=5, x_c=L/2, y_c=0, z_c=0, size = size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)

    mesh.compute_mesh()


    mesh.save(mesh_file)
    #mesh.visualize()
    #exit()

    t2 = time.time()
    print('mesh generated in '+str(t2 - t1)+' s')
else:
    t2 = time.time()

## FEM Simulation
jstim = 20

param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")
param.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")
param.add_domain(mesh_domain=14,mat_file="endoneurium_ranck")
param.add_domain(mesh_domain=1002,mat_file="endoneurium_ranck")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")
param.add_domain(mesh_domain=106,mat_file="platinum")
param.add_domain(mesh_domain=108,mat_file="platinum")

param.add_boundary(mesh_domain=101, btype='Dirichlet', value=0)
param.add_boundary(mesh_domain=103, btype='Neuman', value=jstim)
param.add_boundary(mesh_domain=107, btype='Neuman', value=-jstim)

data = param.save_SimParameters()

#print(data)
sim1 = nrv.FEMSimulation(data=data, mesh=mesh, elem=('Lagrange', 1))

sim1.set_solver_opt(ksp_type=None, pc_type='ilu')

sim1.prepare_sim()
sim1.solve_and_save_sim(out_file)

t3 = time.time()
print('FEM solved in '+str(t3 - t2)+' s')


