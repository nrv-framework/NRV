import nrv
import time

## Results filenames
mesh_file = "./unitary_tests/results/mesh/108_mesh"

## Mesh generation
t1 = time.time()
L=15000         #um
Outer_D = 15    #mm
Nerve_D = 5000 #um

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

mesh.reshape_fascicle(D=1700, y_c=700, z_c=0, ID=1)
mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2)

#mesh.reshape_axon(D=10, y_c=1100, z_c=200, ID=1, res=3)
#mesh.reshape_axon(D=6, y_c=-900, z_c=150, ID=2, res=2)
#mesh.reshape_axon(D=12, y_c=1300, z_c=-300, ID=3, res=3)



mesh.add_electrode(elec_type="CUFF MEA", N=10, x_c=L/2, y_c=0, z_c=0, size = (1000, 500), inactive=True, inactive_L=3000, inactive_th=500,res=50)
mesh.add_electrode(elec_type="CUFF MEA", N=6, x_c=L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)
mesh.add_electrode(elec_type="CUFF MEA", N=4, x_c=3*L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)

mesh.compute_mesh()


mesh.save(mesh_file)
t2 = time.time()
print('solved in '+str(t2 - t1)+' s')
#mesh.visualize()

