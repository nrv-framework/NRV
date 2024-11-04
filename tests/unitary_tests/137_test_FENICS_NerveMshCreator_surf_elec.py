import nrv
import time

if __name__ == "__main__":
    ## Results filenames
    mesh_file = "./unitary_tests/results/mesh/137_mesh"

    ## Mesh generation

    t1 = time.time()
    L=15000         #um
    Outer_D = 10    #mm
    Nerve_D = 5000 #um

    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
    mesh.add_electrode(elec_type="LIFE", x_c=L/4, y_c=1100, z_c=-300, length = 1000, d=25, res=5)
    mesh.add_electrode(elec_type="LIFE", x_c=3*L/4, y_c=1100, z_c=-300, length = 1000, d=25, res=5)
    mesh.add_electrode(elec_type="LIFE", x_c=L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)
    mesh.add_electrode(elec_type="LIFE", x_c=3*L/4, y_c=-800, z_c=-100, length = 1000, d=25, res=5)
    mesh.add_electrode(elec_type="CUFF MP", N=5,  x_c=L/8, contact_length=1000, is_volume=False)
    mesh.add_electrode(elec_type="CUFF MP", N=12, x_c=7*L/8, contact_length=1000, contact_width=1000, is_volume=False, insulator=True, insulator_thickness=500, insulator_length=3000,res=200)
    mesh.add_electrode(elec_type="CUFF", x_c=3*L/8, contact_length=1000, is_volume=False,insulator=True)#, insulator_length=2000, insulator_thickness=500, res=200)
    mesh.add_electrode(elec_type="CUFF", is_volume=False,x_c=5*L/8, contact_length=400, contact_thickness=100,\
        insulator=True, insulator_length=1500, insulator_thickness=600, res=30)

    mesh.compute_geo()

    mesh.compute_domains()
    print(mesh.electrodes)

    mesh.compute_res()
    mesh.generate()
    #mesh.compute_mesh()

    mesh.save(mesh_file)
    t2 = time.time()
    print('mesh generated in '+str(t2 - t1)+' s')
    print(mesh.electrodes)
    #mesh.visualize()

