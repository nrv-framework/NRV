import nrv
from time import perf_counter
import os
import matplotlib.pyplot as plt
import numpy as np
from dolfinx import fem
## Results filenames
test_num = "166"
mesh_file = f"./unitary_tests/results/mesh/{test_num}_mesh"
sim_file = f"./unitary_tests/results/outputs/{test_num}_simres"
fig_file = f"./unitary_tests/figures/{test_num}_"


def get_electode_pot(E, sim):
    S= fem.assemble_scalar(fem.form(1*sim.ds(101+2*E)))
    return fem.assemble_scalar(fem.form(sim.vout*sim.ds(101+2*E)))/S


def get_sig_ap(sig_in, sig_lay, R, th):
    _sig1 = sig_in * (R/(R-th))
    _sig2 = sig_lay * (R/th)
    return (_sig1 * _sig2)/(_sig1 + _sig2)

if __name__ == "__main__":
    ## Mesh generation
    t1 = perf_counter()
    L=200


    nrv.parameters.set_gmsh_ncore(3)
    Outer_D = None    #mm
    Nerve_D = 500 #um
    Fasc_D = 10 #um
    per_th = nrv.get_perineurial_thickness(fasc_d=Fasc_D)

    mesh = nrv.NerveMshCreator(Length=L,Outer_D=Outer_D,Nerve_D=Nerve_D, ver_level=2)
    mesh.reshape_fascicle(d=Fasc_D, y_c=0, z_c=0, ID=0)
    mesh.add_electrode(elec_type="CUFF MP", N=4,  x_c=L/2, contact_length=L/3, is_volume=False)
    mesh.compute_mesh()
    mesh.save(mesh_file)

    t2 = perf_counter()
    mesh.get_info(verbose=True)


    print('mesh generated in '+str(t2 - t1)+' s')

    sig_end = nrv.load_f_material("endoneurium_bhadra").sigma
    sig_per = nrv.load_f_material("perineurium").sigma

    mat_ap = nrv.f_material()
    aplha_lay = Fasc_D/(per_th*2)
    aplha_in = Fasc_D/((Fasc_D/2-per_th)*2)


    print(aplha_lay)
    mat_ap.set_isotropic_conductivity(get_sig_ap(sig_end, sig_per, Fasc_D/2, per_th))
    print(mat_ap.sigma)

    mat_lay = nrv.layered_material(mat_in=sig_end, mat_lay=sig_per, alpha_lay=(per_th*2)/Fasc_D)
    print(mat_lay.sigma)

    # first simulation with layered mat
    ts0 = perf_counter()
    sim0 = nrv.FEMSimulation(D=3, mesh_file=mesh_file, elem=('Lagrange', 2))
    sim0.add_domain(mesh_domain=2,mat_pty="endoneurium_bhadra")
    sim0.add_domain(mesh_domain=10,mat_pty=mat_lay)
    sim0.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim0.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)
    #sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim_', ID=1)

    # simulating
    sim0.setup_sim(jstim=1e-6)
    res0 = sim0.solve()
    pot0 = np.array([get_electode_pot(1, sim0),
                    get_electode_pot(2, sim0),
                    get_electode_pot(3, sim0),
                    get_electode_pot(0, sim0),
                    ]
    )
    del sim0

    # second simulation with mat
    sim1 = nrv.FEMSimulation(D=3, mesh_file=mesh_file, elem=('Lagrange', 2))
    sim1.add_domain(mesh_domain=2,mat_pty="endoneurium_bhadra")
    sim1.add_domain(mesh_domain=10,mat_pty=mat_ap)
    sim1.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)
    #sim1.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim_', ID=1)

    # simulating
    sim1.setup_sim(jstim=1e-6)
    res1 = sim1.solve()
    pot1 = np.array([get_electode_pot(1, sim1),
                    get_electode_pot(2, sim1),
                    get_electode_pot(3, sim1),
                    get_electode_pot(0, sim1),
                    ]
    )
    del sim1

    # third simulation with thin layer
    sim2 = nrv.FEMSimulation(D=3, mesh_file=mesh_file, elem=('Lagrange', 2))
    sim2.add_domain(mesh_domain=2,mat_pty="endoneurium_bhadra")
    sim2.add_domain(mesh_domain=10,mat_pty=sig_end)
    sim2.add_inboundary(mesh_domain=11,mat_pty=sig_per, thickness=per_th, in_domains=[10])

    sim2.add_boundary(mesh_domain=101, btype='Dirichlet', value=0, variable=None, ID=0)
    sim2.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim', ID=1)
    #sim2.add_boundary(mesh_domain=105, btype='Neuman', value=None, variable='jstim_', ID=1)

    # simulating
    sim2.setup_sim(jstim=1e-6)
    res2 = sim2.solve()
    pot2 = np.array([get_electode_pot(1, sim2),
                    get_electode_pot(2, sim2),
                    get_electode_pot(3, sim2),
                    get_electode_pot(0, sim2),
                    ]
    )
    diff_pot = abs(pot2 - pot0)
    diff_pot1 = abs(pot2 - pot1)

    print(f"pot0 = {pot0[1]}, pot1 = {pot1[1]}, pot2 = {pot2[1]}")
    print(f"diff = {diff_pot[1]}, diffpc = {round(100*diff_pot[1]/pot1[1], 4)}%")
    del sim2

    plt.figure()
    plt.plot(100*diff_pot/max(abs(pot2)), "x", markersize=10,markeredgewidth=2)
    plt.plot(100*diff_pot/max(abs(pot2)), "+", markersize=10,markeredgewidth=2)

    plt.ylabel("diff (%)")
    plt.xticks([0, 1, 2, 3], labels=["EW", "ES", "EE", "EN"])
    plt.xlim(-0.1, 3.1)
    plt.savefig(fig_file+"A.png")

    res1.save(sim_file+"1")
    res2.save(sim_file+"2")
    npts = 300
    Y = np.array([[L/2, Nerve_D*(x/npts-0.5), 0] for x in range(1,npts)])


    plt.figure()
    plt.plot(Y[:, 1], res0.eval(Y))
    plt.plot(Y[:, 1], res1.eval(Y))
    plt.plot(Y[:, 1], res2.eval(Y))
    plt.savefig(fig_file+"B.png")
    Z = np.array([[L/2, 0, Nerve_D*(x/npts-0.5)] for x in range(1,npts)])

    plt.figure()
    plt.plot(Z[:, 2], res0.eval(Z))
    plt.plot(Z[:, 2], res1.eval(Z))
    plt.plot(Z[:, 2], res2.eval(Z))
    plt.savefig(fig_file+"C.png")

    # plt.show()
