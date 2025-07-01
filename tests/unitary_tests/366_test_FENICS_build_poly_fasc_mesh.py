import nrv
import time
import os
import numpy as np
import matplotlib.pyplot as plt



test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]


mesh_file = f"{test_dir}results/mesh/{test_num}_mesh"
figdir = "unitary_tests/figures/" + test_num + "_"

if __name__ == "__main__":
    ## Results filenames
    points = 4e2*np.array([[-3,0],[3,-3.5], [1,0],[3,3.5]])
    geom = nrv.create_cshape(vertices=points)
    fig, ax = plt.subplots(figsize=(6, 6))
    geom.plot(ax, label="Polygon Trace")
    geom.plot_bbox(ax, "-+",color=("k",.2),label='bbox')
    ## Mesh generation
    t1 = time.time()
    L=15000         #um
    Outer_D = 15    #mm
    Nerve_D = 5000 #um

    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

    mesh.reshape_fascicle(geometry=geom, ID=2)

    # mesh.reshape_axon(d=10, y=1100, z=200, ID=1, res=3)
    # #mesh.reshape_axon(d=6, y=-900, z=150, ID=2, res=2)
    # #mesh.reshape_axon(d=12, y=1300, z=-300, ID=3, res=3)

    mesh.add_electrode(elec_type="CUFF MP", N=10, x_c=L/2, contact_width = None, contact_length = 1000,res=50)
    mesh.add_electrode(elec_type="CUFF MP", N=6, x_c=L/4, contact_width = None, contact_length = 1000, is_volume=False, res=100)
    mesh.add_electrode(elec_type="CUFF MP", N=4, x_c=3*L/4, contact_width = None, contact_length = 1000, is_volume=False)
    #mesh.add_electrode(elec_type="CUFF MP", N=6, x_c=L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)
    #mesh.add_electrode(elec_type="CUFF MP", N=4, x_c=3*L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)

    mesh.compute_geo()
    mesh.save_geom(f"{test_num}_mesh_geom")
    # plt.show()
    # exit()
    mesh.compute_mesh()

    mesh.save(mesh_file)

    t2 = time.time()
    mesh.get_info(verbose=True)
    print('mesh generated in '+str(t2 - t1)+' s')


    #mesh.visualize()

