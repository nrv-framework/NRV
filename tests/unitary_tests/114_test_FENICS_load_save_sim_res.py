import nrv
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/114_mesh"
out_file1 = "./unitary_tests/results/outputs/114_res1"
out_file2 = "./unitary_tests/results/outputs/114_res2"

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

    mesh.reshape_fascicle(d=2000, y_c=1000, z_c=0, ID=1, res=100)


    #mesh.add_electrode(elec_type="CUFF MEA", N=5, x_c=L/2, y_c=0, z_c=0, size=size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)
    mesh.add_electrode(elec_type="CUFF MP", N=5, x_c=L/2, contact_width = None, contact_length = 100,res=50)

    mesh.compute_mesh()
    mesh.save(mesh_file)
    #mesh.visualize()
    del mesh

    t1 = time.time()
    print(t1-t0)
else:
    t1 = time.time()

# FEM Simulation
param = nrv.FEMParameters(D=3, mesh_file=mesh_file)
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
res1 = sim1.solve()

## Check result savings
res1.save(out_file1, ftype='res')
print('res1 saved')
res2 = nrv.FEMResults()
res2.load(out_file1)
print('res1 loaded')

print(res1==res2)


res1.save(out_file2)
print('res2 saved')