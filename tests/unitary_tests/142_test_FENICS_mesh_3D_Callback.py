import nrv
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

## Results filenames
mesh_file1 = "./unitary_tests/results/mesh/142_mesh1"
mesh_file2 = "./unitary_tests/results/mesh/142_mesh2"
mesh_file3 = "./unitary_tests/results/mesh/142_mesh3"

fig_file1 = "./unitary_tests/figures/142_A.png"

## Parameters
t1 = time.time()
L=10000         #um
Outer_D = 15    #mm
Nerve_D = 5000  #um
fasc_D=[2000, 1000]
fasc_y_c=[-500, 1500]
fasc_z_c=[0, 100]
N_ax = 2

## Callback function
sigma_x = L/3     # std
mu_x = L/2        # avg
f_x =   2*(1-nrv.gate(mu_x, sigma_x)) + 1
f_yz = 0
for i in range(N_ax):

    sigma_yz = 150
    mu_yz = fasc_D[i]/2

    g = nrv.gaussian(sigma=sigma_yz,mu=mu_yz)
    S = nrv.sphere([fasc_y_c[i], fasc_z_c[i]])
    f_yz += g(S)

fmin = 0.3
f_yz = (1-fmin) * (1-f_yz)
f_yz += fmin


f = lambda *X : (f_x(X[0])*f_yz(*X[1:]))**0.5


meshSizeCallback1 = nrv.MeshCallBack(f_yz, axis='yz')
meshSizeCallback2 = nrv.MeshCallBack(f, axis='xyz')
_ = 1
t = np.linspace(-Nerve_D,Nerve_D,100*Outer_D)
Y,Z = np.meshgrid(t, t)
plt.figure()
im = plt.imshow(f_yz(Y,Z),cmap=mpl.cm.viridis)
plt.savefig(fig_file1)

print(f_yz(Y,Z).min(), f_yz(Y,Z).max())

## Mesh generation
mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
mesh.set_chara_blen()
mesh.reshape_outerBox(res=Nerve_D/10)
mesh.reshape_nerve(res=fasc_D[0]/10)
mesh.reshape_fascicle(D=fasc_D[0], y_c=fasc_y_c[0], z_c=fasc_z_c[0], res=fasc_D[0]/10)
mesh.reshape_fascicle(D=fasc_D[1], y_c=fasc_y_c[1], z_c=fasc_z_c[1], res=fasc_D[1]/10)

mesh.refinement_callback(meshSizeCallback2)
mesh.compute_mesh()

m1 = mesh.get_info(verbose=True)
mesh.save(mesh_file1)
t2 = time.time()
print('mesh 1 generated in '+str(t2 - t1)+' s')

#plt.show()
#mesh.visualize()
del mesh
