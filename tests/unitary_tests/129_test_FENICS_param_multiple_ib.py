import nrv
import time
from dolfinx import fem

if __name__ == "__main__":
    filename = "./unitary_tests/sources/127_mesh"
    N_elec = 4
    N_ax = 3


    def get_electode_pot(E, sim):
        S= fem.assemble_scalar(fem.form(1*sim.ds(101+2*E)))
        return fem.assemble_scalar(fem.form(sim.vout*sim.ds(101+2*E)))/S




    param = nrv.FEMParameters(D=3, mesh_file=filename)
    param.add_domain(mesh_domain=0,mat_pty="saline")
    param.add_domain(mesh_domain=2,mat_pty="epineurium")
    param.add_domain(mesh_domain=12,mat_pty="endoneurium_ranck")
    param.add_domain(mesh_domain=14,mat_pty="endoneurium_ranck")


    for i_ax in range(N_ax):
        param.add_domain(mesh_domain=1000+(2*i_ax),mat_pty="endoneurium_ranck")

    for i_elec in range(N_elec):
        param.add_domain(mesh_domain=100+(2*i_elec),mat_pty=1e4)

    param.add_inboundary(mesh_domain=13,mat_file="perineurium", thickness=5, in_domains=[12, 1001, 1003])
    param.add_inboundary(mesh_domain=15,mat_file="perineurium", thickness=5, in_domains=[14, 1005])
    for i_ax in range(N_ax):
        param.add_inboundary(mesh_domain=1001+(2*i_ax),mat_file="gmem", thickness=0.005, in_domains=[1000+(2*i_ax)])

    doms = param.get_mixedspace_domain()
    mats = param.get_mixedspace_mat_pty()
    print('spaces:   ',[0, 1, 2, 3, 4, 5])
    for i, dom in enumerate(doms):
        print("domain "+str(i)+": ", dom)
    print('domains:   ',[k for k in range(11)])
    for i, mat in enumerate(mats):
        print("space "+str(i)+": ",mat)
    print(param.get_space_of_domain(1000))
    print(param.get_space_of_domain(14))
    print(param.get_space_of_domain(12))
    print(param.get_space_of_domain(0))

    print(param.get_spaces_of_ibound(13))
    print(param.get_spaces_of_ibound(15))
    print(param.get_spaces_of_ibound(1001))
    print(param.get_spaces_of_ibound(1003))
    print(param.get_spaces_of_ibound(1005))










