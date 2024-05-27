import nrv
import time

## Results filenames
mesh_file = "./unitary_tests/results/mesh/109_mesh"

## Mesh generation

t1 = time.time()
L=15000         #um
Outer_D = 10    #mm
Nerve_D = 5000 #um

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

mesh.reshape_fascicle(d=1700, y_c=700, z_c=0, ID=1)
mesh.reshape_fascicle(d=1000, y_c=-1000, z_c=0, ID=2)

#mesh.reshape_axon(d=10, y=1100, z=200, ID=1, res=3)



mesh.add_electrode(elec_type="LIFE", x_c=L/4, y_c=1100, z_c=-300, length = 1000, d=25, res=5)
mesh.add_electrode(elec_type="LIFE", x_c=3*L/4, y_c=1100, z_c=-300, length = 1000, d=25, res=5)
mesh.add_electrode(elec_type="LIFE", x_c=L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)
mesh.add_electrode(elec_type="LIFE", x_c=3*L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)

mesh.add_electrode(elec_type="CUFF MP", N=5, x_c=L/4, contact_width = 1000, contact_length=500,\
    insulator=True, insulator_length=3000, insulator_thickness=500,res=50)

mesh.add_electrode(elec_type="CUFF MEA", N=5, x_c=3*L/4, y_c=0, z_c=0, size = (1000, 500),\
    inactive=True, inactive_L=3000, inactive_th=500,res=50)

mesh.add_electrode(elec_type="CUFF", is_volume=True,x_c=L/2, contact_length=50, contact_thickness=100,\
    insulator=True, insulator_length=1000, insulator_thickness=200, res=30)

mesh.compute_geo()
mesh.compute_domains()
mesh.compute_res()
mesh.generate()
#mesh.compute_mesh()


mesh.save(mesh_file)
t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')
print(mesh.electrodes)
#mesh.visualize()

