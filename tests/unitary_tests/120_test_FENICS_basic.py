import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":

    t0 = time.time()
    mesh_file = "./unitary_tests/results/mesh/120_mesh"
    output_file = "./unitary_tests/results/outputs/120_res_sim"

    my_model = nrv.FENICS_model()
    t = time.time()
    print("FEniCS model created in : "+str(t-t0))


    my_model.reshape_outerBox(5.5)
    my_model.build_and_mesh()
    #print(my_model.get_parameters())

    print(my_model.Perineurium_thickness == {0: 5})
    t = time.time()
    print("mesh built in : "+str(t-t0))
    my_model.mesh.save(mesh_file)
    #my_model.get_meshes()

    my_model.solve()
    #my_model.save(output_file)
    t = time.time()
    print("FEM solved in : "+str(t-t0))
    x = np.linspace(0, 5000, num=1000)
    y = 30
    y2 = 90
    z = 0
    V = my_model.get_potentials(x, y, z)
    V2 = my_model.get_potentials(x, y2, z)
    del my_model
    t = time.time()
    print("total time : "+str(t-t0))


    plt.figure()
    plt.plot(x, V)
    plt.plot(x, V2)
    plt.xlabel('position (um)')
    plt.ylabel('extracellular potential (mV)')
    plt.savefig('./unitary_tests/figures/120_A.png')


    #plt.show()
