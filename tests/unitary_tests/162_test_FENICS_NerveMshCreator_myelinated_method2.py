import nrv
import time
import os
import matplotlib.pyplot as plt
import numpy as np
## Results filenames
N_test = "162"
mesh_file = "./unitary_tests/results/mesh/" + N_test + "_mesh"
sigma_file = "./unitary_tests/results/outputs/" + N_test + "_sigma"

## Mesh generation
t1 = time.time()
L=nrv.get_length_from_nodes(10,3)         #um


nrv.parameters.set_gmsh_ncore(3)
Outer_D = None    #mm
Nerve_D = 50 #um


mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
mesh.reshape_axon(d=10, y=0, z=0, ID=0, myelinated=True,res=3)
#mesh.add_electrode(elec_type="CUFF MP", N=4,  x_c=L/2, contact_length=100, is_volume=False)
mesh.compute_mesh()
mesh.save(mesh_file)

t2 = time.time()
mesh.get_mesh_info(verbose=True)


ax1 = nrv.myelinated(d=10, L=L, rec="all", t_sim=5, Nseg_per_sec=1,record_g_mem=True)

res = ax1()
del ax1
Nnodes = res.axonnodes

res.compute_f_mem()
res.get_myeline_properties(endo_mat="endoneurium_bhadra")



mye = nrv.convert(res.g_mye,"S/cm**2", "S/m**2")
g_mye = min(mye)

mat_myel = nrv.mat_from_interp(X=res.x_rec, Y=mye, kind="next")

npts = 30000
X = np.array([[L*x/npts, 4, 0] for x in range(npts)]).T
sig_nrv = mat_myel.sigma_func(X)

print('mesh generated in '+str(t2 - t1)+' s')

param = nrv.FEMParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=2,mat_pty="endoneurium_bhadra")
param.add_domain(mesh_domain=1000,mat_pty=g_mye)
for i in range(Nnodes):
    id_node = "1000" + str(2*i)
    print(id_node)
    param.add_domain(mesh_domain=int(id_node),mat_pty=70)


data = param.save()

sig_sim = nrv.FEMSimulation(D=3, data=data, mesh_file=mesh_file, mesh=mesh, elem=('DG', 2))
sig_sim.add_domain(mesh_domain=1002,mat_pty=mat_myel)
sigma = sig_sim.compute_conductance()
nrv.save_sim_res_list(sigma, sigma_file)


# Plot results
fig, axs = plt.subplots(2)
sig_fen = sigma[-1].eval(X.T)
axs[0].plot(X[0, :], sig_fen, label="FEM interpolation")
axs[0].plot(X[0, :], sig_nrv, "--k", label="NRV interpolation")

# Zoomed plo
lab = [res.get_index_myelinated_sequence(x) for x in range(len(res.x_rec))]

axs[1].plot(X[0, :], sig_fen, label="FEM interpolation")
axs[1].plot(X[0, :], sig_nrv, "--k", label="NRV interpolation")
axs[1].plot(res.x_rec, [sig_nrv[0] for _ in res.x_rec], '|', markersize=300)
axs[1].set_xticks(ticks=res.x_rec, labels=lab, rotation=90)
axs[1].set_xlim((0.995*L/2, 1.005*L/2))
plt.legend()
plt.savefig(f"./unitary_tests/figures/{N_test}_A.png")
del sig_sim


#plt.show()