import nrv
import time
import numpy as np

import matplotlib.pyplot as plt
from dolfinx import geometry

if __name__ == "__main__":
    ## Results mesh_files
    mesh_file = "./unitary_tests/results/mesh/115_mesh"
    fig_file = "./unitary_tests/figures/115_A.png"
    out_file = "./unitary_tests/results/outputs/115_res"


    ## Mesh creation
    mesh = nrv.MshCreator(D=3)
    L = 20
    R = 5

    mesh.add_cylinder(x=0, y=0, z=0, L=L/2, R=R)
    mesh.add_cylinder(x=L/2, y=0, z=0, L=L/2, R=R)
    mesh.add_box((L-R)/2, -R/2, -R/2, R, R, R)

    mesh.fragment()

    volumes, Vcom = mesh.get_volumes(com=True)

    mesh.add_domains(volumes[0][1],100, dim=3, name=None)
    mesh.add_domains(volumes[2][1],101, dim=3, name=None)
    mesh.add_domains([volumes[1][1], volumes[3][1]],102, dim=3, name=None)
    faces, Fcom = mesh.get_faces(com=True)

    In_mask = np.argwhere(np.array(Fcom)[:,0]==0).tolist()
    In_face = [faces[i[0]][1] for i in In_mask]
    Out_mask = np.argwhere(np.array(Fcom)[:,0]==L).tolist()
    Out_mask =[i for i in Out_mask]
    Out_face = [faces[i[0]][1] for i in Out_mask]

    mesh.add_domains(In_face, 11, dim=2, name=None)
    mesh.add_domains(Out_face,22, dim=2, name=None)

    feild_IDs = []
    feild_IDs += [mesh.refine_entities(ent_ID=In_face, res_in=0.2, dim=2, res_out=10, IncludeBoundary=True)]
    feild_IDs += [mesh.refine_entities(ent_ID=Out_face, res_in=0.2, dim=2, res_out=10, IncludeBoundary=True)]
    feild_IDs += [mesh.refine_entities(ent_ID=volumes[1][1], res_in=0.2, dim=3, res_out=2, IncludeBoundary=True)]
    feild_IDs += [mesh.refine_entities(ent_ID=volumes[3][1], res_in=0.2, dim=3, res_out=2, IncludeBoundary=True)]

    mesh.refine_min(feild_IDs=feild_IDs)
    mesh.save(mesh_file)

    #mesh.visualize()

    del mesh

    # FEM Simulation

    ## Sim parameters
    param = nrv.FEMParameters(D=3, mesh_file=mesh_file)
    param.add_domain(mesh_domain=100,mat_file="material_1")
    param.add_domain(mesh_domain=101,mat_file="material_2")
    param.add_domain(mesh_domain=102,mat_pty=100)

    param.add_boundary(mesh_domain=11, btype='Dirichlet', value=0, variable=None)
    param.add_boundary(mesh_domain=22, btype='Neuman', value=None, variable='jstim')

    data = param.save()
    sim1 = nrv.FEMSimulation(data=data)

    jstim = 1
    sim1.setup_sim(jstim=jstim)
    t1 = time.time()
    print('start timer')

    res1 = sim1.solve()

    t2 = time.time()
    print('solved in '+str(t2 - t1)+' s')
    res1.save(out_file)
    print('res1 saved')

    N = 100
    x = np.linspace(0, L, N)
    X = np.array([(k, 0, 0) for k in x])

    mesh = nrv.domain_from_meshfile(mesh_file)

    tree = geometry.bb_tree(mesh, mesh.geometry.dim)
    cells_candidates = geometry.compute_collisions_points(tree, X)

    cells_colliding = geometry.compute_colliding_cells(mesh, cells_candidates, X)
    cells = [cells_colliding.links(i)[0] for i in range(N)]

    u_x1 = res1.vout.eval(X, cells)[:,0]
    u_x = res1.eval(X)

    print(np.allclose(u_x, u_x1))

    plt.plot(x, u_x)
    plt.plot(x, u_x1, ":")
    plt.savefig(fig_file)
    # plt.show()
