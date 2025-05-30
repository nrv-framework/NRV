import nrv
import time
import os
if __name__ == "__main__":
    ## Results filenames
    mesh_file = "./unitary_tests/results/mesh/108_mesh"

    ## Mesh generation
    t1 = time.time()
    L=15000         #um
    Outer_D = 15    #mm
    Nerve_D = 5000 #um

    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)

    mesh.reshape_fascicle(d=700, y_c=700, z_c=0, ID=1)
    mesh.reshape_fascicle(d=1000, y_c=-1000, z_c=0, ID=2)

    mesh.reshape_axon(d=10, y=1100, z=200, ID=1, res=3)
    #mesh.reshape_axon(d=6, y=-900, z=150, ID=2, res=2)
    #mesh.reshape_axon(d=12, y=1300, z=-300, ID=3, res=3)

    mesh.add_electrode(elec_type="CUFF MP", N=10, x_c=L/2, contact_width = None, contact_length = 100,res=50)
    mesh.add_electrode(elec_type="CUFF MP", N=6, x_c=L/4, contact_width = None, contact_length = 100)
    mesh.add_electrode(elec_type="CUFF MP", N=4, x_c=3*L/4, contact_width = None, contact_length = 100)
    #mesh.add_electrode(elec_type="CUFF MP", N=6, x_c=L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)
    #mesh.add_electrode(elec_type="CUFF MP", N=4, x_c=3*L/4, y_c=0, z_c=0, size = (1000, 500),inactive=True)

    mesh.compute_mesh()

    mesh.save(mesh_file)

    t2 = time.time()
    mesh.get_info(verbose=True)
    print('mesh generated in '+str(t2 - t1)+' s')


    #mesh.visualize()

