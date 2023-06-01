import nrv
import time
import numpy as np
import matplotlib.pyplot as plt

## Results filenames
mesh_file1 = "./unitary_tests/results/mesh/139_mesh1"
mesh_file2 = "./unitary_tests/results/mesh/139_mesh2"
mesh_file3 = "./unitary_tests/results/mesh/139_mesh3"

fig_file1 = "./unitary_tests/figures/139_A.png"

## Parameters
t1 = time.time()
L=15000         #um
Outer_D = 15    #mm
Nerve_D = 5000  #um

## Callback function
sigma = L/8     # std
mu = L/2        # avg

# Type 1 : User-define function
f1 = lambda x: 1-np.exp(-((x - mu)/sigma)**2/2) + 0.2
# Type 2 : str to eval in a lambda function
f2 = '1-np.exp(-((x - '+str(mu)+')/'+str(sigma)+')**2/2) + 0.2'
# Type 3 : nrv.function_1D
f3 =  1-nrv.gaussian(mu, sigma) + 0.2

meshSizeCallback1 = nrv.MeshCallBack(f1)
meshSizeCallback2 = nrv.MeshCallBack(f2)
meshSizeCallback3 = nrv.MeshCallBack(f3)
_ = 1
X = np.linspace(0,L,L//4)
plt.plot(X, meshSizeCallback1(_,_,X,_,_,_), label="f1")
plt.plot(X, meshSizeCallback2(_,_,X,_,_,_), '--',label="f2")
plt.plot(X, meshSizeCallback3(_,_,X,_,_,_), ':',label="f3")
plt.legend()
plt.savefig(fig_file1)

## Mesh generation
mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2)
mesh.refinement_callback(meshSizeCallback1)
mesh.compute_mesh()

m1 = mesh.get_info(verbose=True)
mesh.save(mesh_file1)
t2 = time.time()
print('mesh 1 generated in '+str(t2 - t1)+' s')
del mesh

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2)
mesh.refinement_callback(meshSizeCallback2)
mesh.compute_mesh()

m2 = mesh.get_info(verbose=True)
mesh.save(mesh_file2)
t3 = time.time()
print('mesh 2 generated in '+str(t3 - t2)+' s')
del mesh

mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
mesh.reshape_fascicle(D=1000, y_c=-1000, z_c=0, ID=2)
mesh.refinement_callback(meshSizeCallback3)
mesh.compute_mesh()

m3 = mesh.get_info(verbose=True)
mesh.save(mesh_file3)
t4 = time.time()
print('mesh 3 generated in '+str(t4 - t3)+' s')
del mesh

#mesh.visualize()

