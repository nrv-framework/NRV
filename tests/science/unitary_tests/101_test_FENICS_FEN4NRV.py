import nrv
import os
import numpy as np
import time

if __name__ == "__main__":

    mesh_file = "./unitary_tests/results/mesh/101_mesh.msh"
    out_file = './unitary_tests/results/outputs/101_simfile'
    mesh = nrv.MshCreator(D=3)
    nrv.gmsh.logger.start()

    X0 = mesh.add_point(x=0, y=0, z=0)
    X1 = (10+5, 0, 0)
    mesh.add_line(X0, X1)

    let_off = 4


    #F
    mesh.add_box(x=let_off, y=0, z=0, ax=1, ay=5, az=1)
    mesh.add_box(x=let_off, y=4, z=0, ax=3, ay=1, az=1)
    mesh.add_box(x=let_off, y=2, z=0, ax=2, ay=1, az=1)

    #E
    mesh.add_box(x=let_off*2, y=0, z=0, ax=1, ay=5, az=1)
    mesh.add_box(x=let_off*2, y=4, z=0, ax=3, ay=1, az=1)
    mesh.add_box(x=let_off*2, y=2, z=0, ax=2, ay=1, az=1)
    mesh.add_box(x=let_off*2, y=0, z=0, ax=3, ay=1, az=1)

    #M
    mesh.add_box(x=let_off*3, y=0, z=0, ax=1, ay=5, az=1)
    i = mesh.add_box(x=let_off*3+1, y=5, z=0, ax=3, ay=-1, az=1)
    mesh.rotate(volume=i, angle=-45, x=let_off*3+1, y=5,z=0, az=1,rad=False)
    mesh.add_box(x=let_off*3+4, y=0, z=0, ax=1, ay=5, az=1)
    i = mesh.add_box(x=let_off*3+4, y=5, z=0, ax=-4+1, ay=-1, az=1)
    mesh.rotate(volume=i, angle=45, x=let_off*3+4, y=5,z=0, az=1,rad=False)

    #4
    mesh.add_box(x=let_off*5+1, y=0, z=0, ax=1, ay=5, az=1)
    i = mesh.add_box(x=let_off*5+1, y=5, z=0, ax=-2.7, ay=-1.5, az=1)
    mesh.rotate(volume=i, angle=45, x=let_off*5+1, y=5,z=0, az=1,rad=False)
    mesh.add_box(x=let_off*5+1, y=2, z=0, ax=-2, ay=1, az=1)

    #N
    mesh.add_box(x=let_off*6, y=0, z=0, ax=1, ay=5, az=1)
    i = mesh.add_box(x=let_off*6+1, y=0, z=0, ax=1, ay=5, az=1)
    mesh.rotate(volume=i, angle=30, x=let_off*6+1.5, y=2.5,z=0, az=1,rad=False)
    mesh.add_box(x=let_off*6+2, y=0, z=0, ax=1, ay=5, az=1)

    #R
    mesh.add_box(x=let_off*7, y=0, z=0, ax=1, ay=5, az=1)
    mesh.add_box(x=let_off*7, y=2.5, z=0, ax=3, ay=2.5, az=1)
    i = mesh.add_box(x=let_off*7+1, y=3, z=0, ax=3, ay=-1, az=1)
    mesh.rotate(volume=i, angle=-45, x=let_off*7+0.9, y=3,z=0, az=1,rad=False)
    mesh.add_box(x=let_off*7+2, y=0, z=0, ax=1, ay=1, az=1)

    #V
    i = mesh.add_box(x=let_off*8.5, y=0.3, z=0, ax=1, ay=5, az=1)
    mesh.rotate(volume=i, angle=-20,x=let_off*8.5+0.5, y=0.3, z=0, az=1,rad=False)
    i = mesh.add_box(x=let_off*8.5, y=0.3, z=0, ax=1, ay=5, az=1)
    mesh.rotate(volume=i, angle=20,x=let_off*8.5+0.5, y=0.3, z=0, az=1,rad=False)
    mesh.add_box(x=let_off*8.5, y=0, z=0, ax=1, ay=1, az=1)

    #[]
    mesh.add_box(x=1, y=-1, z=0, ax=let_off*10, ay=7, az=1)
    mesh.fragment()


    volumes, Vcom, Bd = mesh.get_volumes(com=True, bd=True)

    #print(volumes, Vcom, Bd)
    outer = []
    letters = []
    for i in range(len(volumes)):
        if -1 in Bd[i]:
            outer += [volumes[i][1]]
        else:
            letters += [volumes[i][1]]

    mesh.add_domains(outer,1, dim=3, name=None)
    mesh.add_domains(letters,2, dim=3, name=None)


    faces, Fcom, Bd = mesh.get_faces(com=True, bd=True)

    left = []
    rigth = []
    for i in range(len(faces)):
        if np.isclose(-1,Fcom[i][1]):
            left += [faces[i][1]]
        elif np.isclose(6,Fcom[i][1]):
            rigth += [faces[i][1]]

    mesh.add_domains(left,0, dim=2, name=None)
    mesh.add_domains(rigth,3, dim=2, name=None)

    #print(mesh.get_obj())
    mesh.generate()
    mesh.save(mesh_file)



    sim1 = nrv.FEMSimulation(D=3, mesh=mesh, elem=('Lagrange', 2))


    sim1.add_domain(mesh_domain=1,mat_file=10000)
    sim1.add_domain(mesh_domain=2,mat_file=0.0001)

    sim1.add_boundary(mesh_domain=3, btype='Dirichlet', value=0)
    sim1.add_boundary(mesh_domain=0, btype='Neuman', value=10)

    sim1.setup_sim()
    t1 = time.time()
    sim1.solve_and_save_sim(out_file)

    t2 = time.time()
    print('solved in '+str(t2 - t1)+' s')


    #mesh.visualize()