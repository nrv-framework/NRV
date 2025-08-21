import nrv
import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
from copy import deepcopy

import pyeit.eit.jac as jac
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

# np.random.seed(102) # working

np.random.seed(444) # not working

if __name__ == "__main__":

    # nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    figdir = f"./figures/{test_id}_"


    if os.cpu_count() > 20:
        n_proc_global = 10
    else:
        n_proc_global = 3


    l_fem = 1000 # um
    l_elec = 300 # um
    x_rec = 3000 # um
    i_drive = 30 # uA
    #dt_fem = 1 # ms
    t_sim=10 # ms
    t_iclamp = 0 # ms
    n_fem_step = 10*n_proc_global
    # dt_fem = [
    #     (2.5, .5),
    #     (8,.1),
    #     (-1,.5),
    #         ]# ms

    dt_fem = [
        (2.5, .75),
        (8,.4),
        (-1,.75),
            ]

    n_elec = 16


    sigma_method = "avg_ind"
    inj_protocol_type = "simple"
    use_gnd_elec = True
    parameters = {"x_rec":x_rec,
    "dt_fem":dt_fem,
    "inj_protocol_type":inj_protocol_type,
    "n_proc_global":n_proc_global,
    "l_elec":l_elec,
    "l_fem":l_fem,
    "i_drive":i_drive,
    "sigma_method":sigma_method,
    "use_gnd_elec":use_gnd_elec,
    "n_elec":n_elec,
    }

    n_ax=10

    outer_d = 5     # mm
    nerve_d = 105  # um
    nerve_l = 5010  # um
    fasc1_d = 20   # um
    fasc1_y = 30     # um
    fasc1_z = 0     # um

    percent_unmyel = 1
    unmyelinated_nseg = 1000
    axons_data={
        "diameters":[10.001],
        "types":[1],
        "y":[0],
        "z":[0],
    }

    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d, postproc_label="sample_keys", record_g_mem=True)
    fascicle_1 = nrv.fascicle(diameter=fasc1_d, ID=1, unmyelinated_nseg=unmyelinated_nseg)
    fascicle_1.fill(n_ax=n_ax, percent_unmyel=percent_unmyel, M_stat="Ochoa_M", U_stat="Ochoa_U", fit_to_size=False,delta=1, delta_trace=3)
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

    nerve_data = nerve_1.save(save=False)


    fig, ax = plt.subplots(figsize=(6, 6))
    nerve_1.plot(ax)

    nerve_1.fascicles[1].axons.axon_pop


    del nerve_1

    eit_instance = eit.EIT2DProblem(nerve_data, res_dname=res_dir, label=test_id, **parameters)

    ## Nerve simulation
    sim_param = {"t_sim":t_sim}
    nrn_res = eit_instance.simulate_nerve(t_start=t_iclamp, sim_param=sim_param)
    fig.savefig(f"./unitary_tests/figures/{test_id}_A.png")

    fig, ax = plt.subplots(figsize=(6, 6))
    nrn_res.plot_recruited_fibers(ax)


    ## Impedance simulation
    eit_instance._setup_problem()
    # Build mesh
    eit_instance.build_mesh()
    fig.savefig(f"./unitary_tests/figures/{test_id}_B.png")

    # plt.show()