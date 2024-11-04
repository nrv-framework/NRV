import nrv
import time

## Results mesh_files
mesh_file = "./unitary_tests/results/mesh/117_mesh"
fig_file = "./unitary_tests/figures/117_A.png"
out_file = "./unitary_tests/results/outputs/117_res"

if __name__ == "__main__":
    ## Mesh creation
    if nrv.MCH.do_master_only_work():
        is_mesh = False
        if not is_mesh:
            print('Building mesh')
            t1 = time.time()

            L=5000          #um
            Outer_D = 10    #mm
            Nerve_D = 5000  #um

            size_elec = (1000, 500)
            #
            mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D)

            mesh.reshape_nerve(res=500)

            mesh.reshape_fascicle(d=2000, y_c=1000, z_c=0, ID=1, res=200)
            mesh.reshape_fascicle(d=1000, y_c=-1000, z_c=0, ID=2, res=200)

            #mesh.reshape_axon(d=10, y=1100, z=200, ID=1, res=3)

            #mesh.add_electrode(elec_type="CUFF MEA", N=3, x_c=L/2, y_c=0, z_c=0, size = size_elec, inactive=True, inactive_L=3000, inactive_th=500,res=50)
            mesh.add_electrode(elec_type="CUFF MP", N=3, x_c=L/2, contact_width = 1000, contact_length = 100,res=50)

            mesh.compute_mesh()

            mesh.save(mesh_file)
            # mesh.visualize()
            # exit()
            del mesh
            
            t2 = time.time()
            print('mesh generated in '+str(t2 - t1)+' s')

    nrv.synchronize_processes()

    # FEM Simulation
    param = nrv.FEMParameters(D=3, mesh_file=mesh_file)
    param.add_domain(mesh_domain=0,mat_file="saline")
    param.add_domain(mesh_domain=2,mat_file="epineurium")
    param.add_domain(mesh_domain=12,mat_file="endoneurium_ranck")
    param.add_domain(mesh_domain=14,mat_file="endoneurium_ranck")
    #param.add_domain(mesh_domain=1002,mat_file="endoneurium_ranck")

    param.add_domain(mesh_domain=100,mat_file="platinum")
    param.add_domain(mesh_domain=102,mat_file="platinum")
    param.add_domain(mesh_domain=104,mat_file="platinum")

    # Adding internal boundaries
    param.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=0.005, in_domains=[12])
    param.add_inboundary(mesh_domain=15,mat_file="perineurium", thickness=0.005, in_domains=[14])

    param.add_boundary(mesh_domain=0, btype='Dirichlet', value=0, variable=None)
    param.add_boundary(mesh_domain=101, btype='Neuman', value=None, variable='jstim')
    param.add_boundary(mesh_domain=103, btype='Neuman', value=None, variable='_jstim')



    data = param.save()

    mxd_dom = param.get_mixedspace_domain()
    mxd_mf = param.get_mixedspace_mat_pty()

    mxd_dom_0 = param.get_mixedspace_domain(0)
    mxd_dom_1 = param.get_mixedspace_domain(1)
    mxd_dom_02 = param.get_mixedspace_domain(0, 2)
    mxd_mf_02 = param.get_mixedspace_mat_pty(0, 2)
    mxd_mf_1 = param.get_mixedspace_mat_pty(1)

    sod_2 = param.get_space_of_domain(2)
    sod_14 = param.get_space_of_domain(14)

    sim1 = nrv.FEMSimulation(data=data, elem=('Lagrange', 2))
    jstim = 20
    sim1.setup_sim(jstim=jstim, _jstim=-jstim)



    sim1.solve_and_save_sim(out_file)

    if nrv.MCH.do_master_only_work():
        t3 = time.time()
        print('FEM solved in '+str(t3 - t2)+' s')


