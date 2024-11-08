import nrv
import os

if __name__ == "__main__":
    mesh_file = "./unitary_tests/results/mesh/102_mesh.msh"
    mesh = nrv.MshCreator(D=3)
    nrv.gmsh.logger.start()

    X0 = mesh.add_point(x=0, y=0, z=0)
    X1 = (10+5, 0, 0)
    mesh.add_line(X0, X1)

    mesh.add_cylinder(x=0, y=0, z=0, L=10, R=2)
    mesh.add_cylinder(x=5, y=0, z=0, L=10, R=2)
    mesh.add_cylinder(x=2.5, y=0, z=0, L=10, R=1)

    mesh.fragment()
    mesh.generate()


    mesh.save(mesh_file)

    #print(mesh.get_obj())
    #mesh.visualize()