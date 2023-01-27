import nrv
import time
import numpy as np

## Results filenames
mesh_file = "./unitary_tests/results/mesh/107_mesh"
out_file = "./unitary_tests/results/outputs/107_simfile"

## Mesh creation
mesh = nrv.MshCreator(D=3)

L = 20
R = 5

mesh.add_cylinder(x=0, y=0, z=0, L=L/2, R=R)
mesh.add_cylinder(x=L/2, y=0, z=0, L=L/2, R=R)

mesh.add_box((L-R)/2, -R/2, -R/2, R, R, R)
mesh.fragment()

volumes, Vcom = mesh.get_volumes(com=True)
print(volumes, Vcom)

mesh.add_domains(volumes[0][1],100, dim=3, name=None)
mesh.add_domains(volumes[2][1],101, dim=3, name=None)
mesh.add_domains([volumes[1][1], volumes[3][1]],102, dim=3, name=None)

faces, Fcom = mesh.get_faces(com=True)
print(faces, Fcom)
In_mask = np.argwhere(np.array(Fcom)[:,0]==0).tolist()
In_face = [faces[i[0]][1] for i in In_mask]
Out_mask = np.argwhere(np.array(Fcom)[:,0]==L).tolist()
Out_face = [faces[i[0]][1] for i in Out_mask]
print(In_mask, Out_mask)

mesh.add_domains(In_face, 11, dim=2, name=None)
mesh.add_domains(Out_face,22, dim=2, name=None)
print(In_face, Out_face)

feild_IDs = []
feild_IDs += [mesh.refine_entities(ent_ID=In_face, res_in=0.2, dim=2, res_out=10, IncludeBoundary=True)]
feild_IDs += [mesh.refine_entities(ent_ID=Out_face, res_in=0.2, dim=2, res_out=10, IncludeBoundary=True)]
feild_IDs += [mesh.refine_entities(ent_ID=volumes[1][1], res_in=0.2, dim=3, res_out=2, IncludeBoundary=True)]
feild_IDs += [mesh.refine_entities(ent_ID=volumes[3][1], res_in=0.2, dim=3, res_out=2, IncludeBoundary=True)]

print(feild_IDs)
mesh.refine_min(feild_IDs=feild_IDs)

mesh.save(mesh_file)
#print(mesh.get_obj())
# mesh.visualize()
# exit()
del mesh


## Sim parameters
param = nrv.SimParameters(D=3, mesh_file=mesh_file)
param.add_domain(mesh_domain=100,mat_file="material_2")
param.add_domain(mesh_domain=101,mat_file="material_1")
param.add_domain(mesh_domain=102,mat_file="silicone")

param.add_boundary(mesh_domain=11, btype='Dirichlet', value=0, variable=None)
param.add_boundary(mesh_domain=22, btype='Neuman', value=None, variable='jstim')

data = param.save_SimParameters()
sim1 = nrv.FEMSimulation(data=data)


jstim = 1
sim1.prepare_sim(jstim=jstim)
#sim1.assemble()
t1 = time.time()
print('start timer')
sim1.solve_and_save_sim(out_file)

t2 = time.time()
print('solved in '+str(t2 - t1)+' s')