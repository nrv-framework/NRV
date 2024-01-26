import nrv
import time
import numpy as np 
import matplotlib.pyplot as plt

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/119_mesh"
fig_file = "./unitary_tests/figures/119_A.png"
out_file = "./unitary_tests/results/outputs/119_res"


## Mesh creation
print('Building mesh')
t1 = time.time()

L=15000          #um
Outer_D = 10    #mm
Nerve_D = 5000  #um



size_elec = (1000, 500)
#
mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

mesh.reshape_nerve(res=500)

mesh.reshape_fascicle(D=3000, y_c=0, z_c=0, ID=1, res=300)
mesh.add_electrode(elec_type="LIFE", x_c=L/2, y_c=0, z_c=0, length = 1000, D=25, res=3)

mesh.compute_mesh()


mesh.save(mesh_file)
#mesh.visualize()
#print(mesh.get_parameters())

t2 = time.time()
print('mesh generated in '+str(t2 - t1)+' s')


# FEM Simulation

sim1 = nrv.FEMSimulation(D=3, mesh_file=mesh_file, mesh=mesh, elem=('Lagrange', 2))
sim1.add_domain(mesh_domain=0,mat_file="saline")
sim1.add_domain(mesh_domain=2,mat_file="epineurium")
sim1.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")

# Adding internal boundaries
#sim1.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=0.005, in_domains=[12])

sim1.add_boundary(mesh_domain=1, btype='Dirichlet', value=0, variable=None)
sim1.add_boundary(mesh_domain=101, btype='Neuman', value=None, variable='jstim', mesh_domain_3D=12)

data = sim1.save()

jstim = 20e-3
sim1.setup_sim(jstim=jstim, _jstim=-jstim)
res1 = sim1.solve_and_save_sim(out_file)





t3 = time.time()
print('FEM solved in '+str(t3 - t2)+' s')

sim2 = nrv.FEMSimulation(data=data, mesh=mesh, elem=('Lagrange', 2))

sim2.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=0.005, in_domains=[12])
sim2.setup_sim(jstim=jstim)
res2 = sim2.solve_and_save_sim(out_file)

t4 = time.time()
print('FEM solved in '+str(t4 - t3)+' s')

z_ax = 0
y_ax1 = 100
y_ax2 = 1500
X_ax = np.linspace(0, L, 3000)

ax1 = [[x_ax, y_ax1, z_ax] for x_ax in X_ax]
ax2 = [[x_ax, y_ax2, z_ax] for x_ax in X_ax]

V11 = res1.eval(ax1)
V21 = res1.eval(ax2)

V12 = res2.eval(ax1)
V22 = res2.eval(ax2)

print(not np.allclose(V11, V12))
print(not np.allclose(V21, V22))
print(max(V11-V12))
print(max(V21-V22))

plt.figure()
plt.plot(X_ax, V11)
plt.plot(X_ax, V21)
plt.plot(X_ax, V12)
plt.plot(X_ax, V22)
plt.savefig('./unitary_tests/figures/119_A.png')
plt.figure()
plt.plot(X_ax, V11-V12)
plt.plot(X_ax, V21-V22)
plt.savefig('./unitary_tests/figures/119B.png')
#plt.show()
