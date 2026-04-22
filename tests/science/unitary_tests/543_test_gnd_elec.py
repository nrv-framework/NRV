import numpy as np
import matplotlib.pyplot as plt

import nrv
from nrv.fmod.FEM.mesh_creator import get_mesh_domid


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir) + len(test_dir) :]
test_id = __fname__[: __fname__.find("_")]


def build_nerve():
    """
    Create a small single-fascicle nerve used to validate grounded electrodes.
    """
    nerve = nrv.nerve(length=5000, diameter=250, Outer_D=5, ID=int(test_id))
    nerve.verbose = False
    nerve.add_fascicle("./unitary_tests/sources/300_fascicle_1.json", ID=0)
    return nerve


def build_stimulation(nerve_length):
    """
    Create a stimulation context with one cuff ground and one active LIFE electrode.

    Parameters
    ----------
    nerve_length : float
        Length of the nerve, in um.

    Returns
    -------
    nrv.FEM_stimulation
        Stimulation context configured for the grounded-electrode regression test.
    """
    extra_stim = nrv.FEM_stimulation()

    cuff = nrv.CUFF_electrode(
        "CUFF_GND",
        contact_length=1000,
        contact_thickness=20,
        insulator_length=2000,
        insulator_thickness=200,
        x_center=nerve_length / 2,
    )
    stim_gnd = nrv.stimulus()
    extra_stim.add_electrode(cuff, stim_gnd)

    life = nrv.LIFE_electrode(
        "LIFE",
        D=25,
        length=800,
        x_shift=(nerve_length - 800) / 2,
        y_c=0,
        z_c=0,
    )
    stim_life = nrv.stimulus()
    stim_life.biphasic_pulse(start=0.5, s_cathod=20, t_stim=60e-3, s_anod=4, t_inter=40e-3)
    extra_stim.add_electrode(life, stim_life)

    return extra_stim


if __name__ == "__main__":
    gnd_elec_id = 0
    gnd_elec_domid = get_mesh_domid(objtype="e", objid=gnd_elec_id, is_surf=True)

    nerve = build_nerve()
    stimulation = build_stimulation(nerve.L)
    nerve.attach_extracellular_stimulation(stimulation)
    nerve.extra_stim.gnd_elec = gnd_elec_id
    results = nerve.simulate(t_sim=2)

    V_cuff_gnd = nerve.extra_stim.model.sim.get_domain_potential(gnd_elec_domid)

    assert results is not None
    assert nerve.extra_stim.gnd_elec == [gnd_elec_id]
    assert nerve.extra_stim.model.is_computed
    assert len(nerve.extra_stim.model.sim_res) == 2
    assert np.isclose(V_cuff_gnd, 0)

    del nerve, results, stimulation

    nerve = build_nerve()
    stimulation = build_stimulation(nerve.L)
    nerve.attach_extracellular_stimulation(stimulation)
    results = nerve.simulate(t_sim=2)
    V_cuff_no_gnd = nerve.extra_stim.model.sim.get_domain_potential(gnd_elec_domid)

    print(f"Cuff potential when connected to GND {V_cuff_gnd}\nCuff potential when GND connected to outerbox {V_cuff_no_gnd}")
    
