import nrv
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/117_mesh"
fig_file = "./unitary_tests/figures/017_A.png"
out_file = "./unitary_tests/results/outputs/117_res.xdmf"

## Mesh creation
is_mesh = False
if not is_mesh:
    print('Building mesh')
    t1 = time.time()

    L=5000          #um
    Outer_D = 10    #mm
    Nerve_D = 5000  #um

    size_elec = (1000, 500)
    #
    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

    mesh.reshape_nerve(res=500)

    mesh.reshape_fascicle(D=2000, y_c=1000, z_c=0, ID=1, res=200)
    mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2, res=200)

    #mesh.reshape_axon(D=10, y_c=1100, z_c=200, ID=1, res=3)

    mesh.add_electrode(elec_type="CUFF MEA", N=3, x_c=L/2, y_c=0, z_c=0, size = size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)

    mesh.compute_geo()
    mesh.compute_domains()
    mesh.compute_res()


    mesh.save(mesh_file)
    # mesh.visualize()
    # exit()
    del mesh

    t2 = time.time()
    print('mesh generated in '+str(t2 - t1)+' s')


# FEM Simulation
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=0,mat_file="saline")
param.add_domain(mesh_domain=2,mat_file="epineurium")
param.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")
param.add_domain(mesh_domain=14,mat_file="endoneurium_ranck")
#param.add_domain(mesh_domain=1002,mat_file="endoneurium_ranck")

param.add_domain(mesh_domain=100,mat_file="platinum")
param.add_domain(mesh_domain=102,mat_file="platinum")
param.add_domain(mesh_domain=104,mat_file="platinum")

# Adding internal boundaries
param.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=0.005, in_domains=[12])
param.add_inboundary(mesh_domain=15,mat_file="perineurium", thickness=0.005, in_domains=[14])

param.add_boundary(mesh_domain=0, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=101, btype='Neuman', value=None, variable='jstim')
param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='_jstim')



data = param.save_SimParameters()
print(data)

print(param.get_mixedspace_domain())
print(param.get_mixedspace_mat_file())

print(param.get_mixedspace_domain(0))
print(param.get_mixedspace_domain(1))
print(param.get_mixedspace_domain(0, 2))
print(param.get_mixedspace_mat_file(0, 2))
print(param.get_mixedspace_domain(1))
print(param.get_mixedspace_mat_file(1))

print(param.get_space_of_domain(2))
print(param.get_space_of_domain(14))

sim1 = nrv.FEMSimulation(data=data)
jstim = 20
sim1.prepare_sim(jstim=jstim, _jstim=-jstim)



sim1.solve_and_save_sim(out_file,plot=False, overwrite=True)

t3 = time.time()
print('FEM solved in '+str(t3 - t2)+' s')


