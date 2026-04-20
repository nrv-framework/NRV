import nrv

if __name__ == "__main__":
    mesh_file = "./unitary_tests/results/mesh/103_mesh"
    mesh = nrv.MshCreator(D=3)

    mesh.add_cylinder(x=0, y=0, z=0, L=20, R=5)
    mesh.add_cylinder(x=0, y=2.5, z=0, L=20, R=2)
    mesh.add_cylinder(x=0, y=-2.5, z=0, L=20, R=2)

    mesh.fragment()

    volumes, Vcom = mesh.get_volumes(com=True)

    print(volumes, Vcom)
    for i in range(len(volumes)):
        mesh.add_domains(volumes[i][1],10**(i+1), dim=3, name=None)

    faces, Fcom = mesh.get_faces(com=True)

    print(faces, Fcom)
    for i in range(len(faces)):
        mesh.add_domains(faces[i][1],1+10*(i+1), dim=2, name=None)


    mesh.save(mesh_file)

    print(mesh.get_obj())
    #mesh.visualize()

