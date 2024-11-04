import nrv
import numpy as np
import os
if __name__ == "__main__":
    n_core = os.cpu_count()
    if n_core < 2:
        nrv.rise_warning("not enougth core to test multicore meshing")
    else:
        nrv.parameters.set_gmsh_ncore(n_core//2)

    mesh_file = "./unitary_tests/results/mesh/143_mesh"

    mesh = nrv.MshCreator(D=3)
    L=20
    mesh.add_cylinder(x=0, y=0, z=0, L=L, R=5)
    mesh.add_cylinder(x=0, y=2.5, z=0, L=L, R=2)
    mesh.add_cylinder(x=0, y=-2.5, z=0, L=L, R=2)
    mesh.fragment()
    volumes, Vcom = mesh.get_volumes(com=True)

    for i in range(len(volumes)):
        mesh.add_domains(volumes[i][1],100*i, dim=3, name=None)

    faces, Fcom = mesh.get_faces(com=True)

    In_mask = np.argwhere(np.array(Fcom)[:,0]==0).tolist()
    In_face = [faces[i[0]][1] for i in In_mask]
    Out_mask = np.argwhere(np.array(Fcom)[:,0]==L).tolist()
    Out_mask =[i for i in Out_mask]
    Out_face = [faces[i[0]][1] for i in Out_mask]


    mesh.add_domains(In_face, 11, dim=2, name=None)
    mesh.add_domains(Out_face,22, dim=2, name=None)

    feild_IDs = []
    feild_IDs += [mesh.refine_entities(ent_ID=In_face, res_in=2, dim=2, res_out=2, IncludeBoundary=True)]

    feild_IDs += [mesh.refine_entities(ent_ID=Out_face, res_in=0.2, dim=2, res_out=2, IncludeBoundary=True)]
    feild_IDs += [mesh.refine_threshold(ent_ID=In_face, dim=2 ,res_min=0.2, dist_min=L/4, dist_max=3*L/4, res_max=2)]
    mesh.refine_min(feild_IDs=feild_IDs)

    mesh.save(mesh_file)
    mesh.get_info(verbose=True)
    #mesh.visualize()
