import nrv
import time
import numpy as np
import matplotlib.pyplot as plt

#nrv.parameters.set_nrv_verbosity(3)
#nrv.parameters.set_gmsh_ncore(1)
## Results filenames
mesh_file = "./unitary_tests/results/mesh/140_mesh"
fig_file1 = "./unitary_tests/figures/140_A.png"

## Parameters
t1 = time.time()
L=15000         #um
Outer_D = 15    #mm
Nerve_D = 5000 #um

x_E1 = 3*L/8
x_E2 = 5*L/8

## Callback function
sigma = 1.5 * (x_E2 - x_E1)
mu = L/2

f =  (1-nrv.gate(mu, sigma, N=5)) + 0.5
meshSizeCallback = nrv.MeshCallBack(f)

X = np.linspace(0,L,L//4)
m = max(f(X))

plt.plot(X, f(X), label="f")
plt.legend()
plt.savefig(fig_file1)

## Mesh generation
mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

mesh.reshape_fascicle(d=700, y_c=700, z_c=0, ID=1)
mesh.reshape_fascicle(d=1000, y_c=-1000, z_c=0, ID=2)
mesh.reshape_axon(d=10, y=500, z=100, ID=1, res=4)

mesh.add_electrode(elec_type="CUFF MP", N=12, x_c=x_E1, contact_length=1000, contact_width=1000,\
    contact_thickness=100,is_volume=False, insulator=True, insulator_thickness=500, insulator_length=3000,res=200)
mesh.add_electrode(elec_type="CUFF", is_volume=False,x_c=x_E2, contact_length=400,\
    contact_thickness=100, insulator=True, insulator_length=1500, insulator_thickness=600, res=30)

mesh.refinement_callback(meshSizeCallback)

mesh.compute_mesh()

mesh.save(mesh_file)
t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')
#mesh.visualize()

