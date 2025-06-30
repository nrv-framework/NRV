import nrv
import numpy as np
import matplotlib.pyplot as plt


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

mesh_file_u = f"./unitary_tests/results/mesh/{test_num}_umesh.msh"
mesh_file_m = f"./unitary_tests/results/mesh/{test_num}_mmesh.msh"


if __name__ == "__main__":
    fascicle = nrv.fascicle(ID=test_num, diameter=50)
    fascicle.fill(data={
        "diameters": [10 ,3, 4],
        "types": [1, 1, 1],
        "y": [0, 0, 10],
        "z": [0, 10, 0],
        "node_shift":[.2,.3,.1]
    })
    print(fascicle.axons)
    fig, ax = plt.subplots(figsize=(5,5))
    fig.savefig(figdir+"B.png")

    mesh = nrv.mesh_from_fascicle(fascicle, Length=300,Outer_D=None, Nerve_D=400)
    print(mesh.n_core)
    mesh.compute_mesh()
    mesh.save(mesh_file_m)
    mesh.get_info(verbose=True)
    del mesh

    fascicle = nrv.fascicle(ID=test_num, diameter=50)
    fascicle.fill(data={
        "diameters": [1, 1, 2],
        "types": [0, 0, 0],
        "y": [0, 0, 5],
        "z": [0, 2, 0],
    })


    fig, ax = plt.subplots(figsize=(5,5))
    fascicle.plot(ax)
    fig.savefig(figdir+"B.png")
    # plt.show()

    mesh = nrv.mesh_from_fascicle(fascicle, Length=100,Outer_D=None, Nerve_D=400)
    print(mesh.n_core)
    mesh.compute_mesh()
    mesh.save(mesh_file_u)
    mesh.get_info(verbose=True)
    del mesh

# plt.show()


