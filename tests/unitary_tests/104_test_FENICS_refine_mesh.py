import nrv
import numpy as np

mesh_file = "./unitary_tests/results/mesh/104_mesh"

mesh = nrv.MshCreator(D=3)
L=20
mesh.add_cylinder(x=0, y=0, z=0, L=L, R=5)
mesh.add_cylinder(x=0, y=2.5, z=0, L=L, R=2)
mesh.add_cylinder(x=0, y=-2.5, z=0, L=L, R=2)
mesh.fragment()

volumes, Vcom = mesh.get_volumes(com=True)

print(volumes, Vcom)
for i in range(len(volumes)):
    mesh.add_domains(volumes[i][1],100*i, dim=3, name=None)

faces, Fcom = mesh.get_faces(com=True)

print(faces, Fcom)
In_mask = np.argwhere(np.array(Fcom)[:,0]==0).tolist()
In_face = [faces[i[0]][1] for i in In_mask]
Out_mask = np.argwhere(np.array(Fcom)[:,0]==L).tolist()
Out_mask =[i for i in Out_mask]
Out_face = [faces[i[0]][1] for i in Out_mask]
print(In_mask, Out_mask)

mesh.add_domains(In_face, 11, dim=2, name=None)
mesh.add_domains(Out_face,22, dim=2, name=None)
print(In_face, Out_face)

feild_IDs = []
feild_IDs += [mesh.refine_entities(ent_ID=In_face, res_in=0.2, dim=2, res_out=2, IncludeBoundary=True)]
feild_IDs += [mesh.refine_entities(ent_ID=Out_face, res_in=0.2, dim=2, res_out=2, IncludeBoundary=True)]
feild_IDs += [mesh.refine_threshold(ent_ID=In_face, dim=2 ,res_min=0.2, dist_min=L/4, dist_max=3*L/4, res_max=2)]

print(feild_IDs)
mesh.refine_min(feild_IDs=feild_IDs)

mesh.save(mesh_file)
mesh.save("./unitary_tests/sources/3cylinder")

print(mesh.get_obj())
#mesh.visualize()