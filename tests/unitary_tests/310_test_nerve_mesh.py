import nrv
import numpy as np
import matplotlib.pyplot as plt



test_num = 310
mesh_file_u = f"./unitary_tests/results/mesh/{test_num}_umesh"
mesh_file_m = f"./unitary_tests/results/mesh/{test_num}_mmesh"


fascicle = nrv.fascicle(ID=test_num)
fascicle.axons_diameter = np.asarray([10 ,3, 4])
fascicle.axons_type = np.asarray([1, 1, 1])
fascicle.axons_y = np.asarray([0, 0, 10])
fascicle.axons_z = np.asarray([0, 10, 0])
fascicle.define_circular_contour(D=50)

fig, ax = plt.subplots(figsize=(5,5))
fascicle.plot(ax)
#plt.show()

mesh = nrv.mesh_from_fascicle(fascicle, Length=300,Outer_D=None, Nerve_D=400)
print(mesh.n_core)
mesh.compute_mesh()
mesh.save(mesh_file_m)

fascicle = nrv.fascicle(ID=test_num)
fascicle.axons_diameter = np.asarray([1, 1, 2])
fascicle.axons_type = np.asarray([0, 0, 0])
fascicle.axons_y = np.asarray([0, 0, 5])
fascicle.axons_z = np.asarray([0, 2, 0])
fascicle.define_circular_contour(D=50)


fig, ax = plt.subplots(figsize=(5,5))
fascicle.plot(ax)
#plt.show()

mesh = nrv.mesh_from_fascicle(fascicle, Length=100,Outer_D=None, Nerve_D=400)
print(mesh.n_core)
mesh.compute_mesh()
mesh.save(mesh_file_u)
# plt.show()


