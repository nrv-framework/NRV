import nrv
import time
import os


Ntest = 145
t0 = time.time()
## Results filenames
json_file = "./unitary_tests/figures/" + str(Ntest) + "_mesh.json"
mesh_file = "./unitary_tests/results/mesh/" + str(Ntest) + "_mesh"

## Mesh generation
L = 15000         #um
Outer_D = 10    #mm
Nerve_D = 5000 #um

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

mesh.reshape_fascicle(d=1700, y_c=700, z_c=0, ID=1)
mesh.reshape_fascicle(d=1000, y_c=-1000, z_c=0, ID=2)


mesh.add_electrode(elec_type="LIFE", x_c=L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)
mesh.add_electrode(elec_type="LIFE", x_c=3*L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)

mesh.add_electrode(elec_type="CUFF MP", N=5, x_c=L/4, contact_width = 1000, contact_length=500,\
    insulator=True, insulator_length=3000, insulator_thickness=500,res=50)


mesh_dic = mesh.save(save=True, fname=json_file)
print("save not meshed ok")
t1 = time.time()
print('mesh set in '+str(t1 - t0)+' s')
del mesh

mesh2 = nrv.load_any(json_file)
mesh2.compute_mesh()
print("load not meshed ok")

mesh2.save(mesh_file)
print("save meshed ok")

t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')
mesh2.get_mesh_info(verbose=True)
del mesh2


mesh3 = nrv.load_any(mesh_file)
mesh3.compute_mesh()
print("load meshed ok")

mesh3.save(mesh_file)

t3 = time.time()
print('mesh reloaded in '+str(t3 - t2)+' s')
mesh3.get_mesh_info(verbose=True)



#mesh.visualize()

