import nrv
import time
import numpy as np 
import matplotlib.pyplot as plt

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/118_mesh"
fig_file = "./unitary_tests/figures/118_A.png"
out_file = "./unitary_tests/results/outputs/118_res"


## Mesh creation
print('Building mesh')
t1 = time.time()

L=5000          #um
Outer_D = 5     #mm
Nerve_D = 250   #um

#
mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

mesh.reshape_nerve(res=25)
mesh.reshape_fascicle(d=200, y_c=0, z_c=0, res=100)
mesh.add_electrode(elec_type="LIFE", x_c=L/2, y_c=0, z_c=0, length=1000, d=25, res=3)
mesh.compute_mesh()

mesh.save(mesh_file)
#print(mesh.get_parameters())

t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')
#mesh.visualize()

mesh.get_info(True)

# FEM Simulation

sim1 = nrv.FEMSimulation(D=3, mesh_file=mesh_file, mesh=mesh, elem=('Lagrange', 2))
sim1.add_domain(mesh_domain=0,mat_file="saline")
sim1.add_domain(mesh_domain=2,mat_file="endoneurium_ranck")
sim1.add_domain(mesh_domain=10,mat_file="endoneurium_ranck")

# Adding internal boundaries
sim1.add_inboundary(mesh_domain=11,mat_file="perineurium", thickness=0.005, in_domains=[10])
#sim1.add_inboundary(mesh_domain=3,mat_file="perineurium", thickness=5, in_domains=[2])

sim1.add_boundary(mesh_domain=1, btype='Dirichlet', value=0, variable=None)
sim1.add_boundary(mesh_domain=101, btype='Neuman', value=None, variable='jstim', mesh_domain_3D=0)

data = sim1.save()

Istim = 1
jstim = Istim / (np.pi * 1000 * 25e-3)
sim1.setup_sim(jstim=jstim, _jstim=-jstim)
res1 = sim1.solve_and_save_sim(out_file)


t3 = time.time()
print('FEM solved in '+str(t3 - t2)+' s')

z_ax = 0
y_ax1 = 30
y_ax2 = 100
X_ax = np.linspace(0, L, 3000)

ax1 = [[x_ax, y_ax1, z_ax] for x_ax in X_ax]
ax2 = [[x_ax, y_ax2, z_ax] for x_ax in X_ax]

V1 = res1.eval(ax1)
V2 = res1.eval(ax2)

plt.figure()
plt.plot(X_ax, V1)
plt.plot(X_ax, V2)


plt.savefig('./unitary_tests/figures/118_A.png')

z_ax = 0
Y_ax = np.linspace(12.5, 500, 1000)
Y_ax = np.concatenate((np.flip(-Y_ax), Y_ax))
x_ax = 2500

ax3 = [[x_ax, y_ax, z_ax] for y_ax in Y_ax]


V3 = res1.eval(ax3)


plt.figure()
plt.plot(Y_ax, V3)

plt.savefig('./unitary_tests/figures/118_B.png')
#plt.show()
