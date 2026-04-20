from __future__ import annotations

import numpy as np
import pytest


def _build_fascicle_for_nerve(nrv_module, fascicle_id: int):
    fascicle = nrv_module.fascicle(diameter=90, ID=fascicle_id)
    fascicle.axons.create_population_from_data(
        (
            np.array([0, 1], dtype=int),
            np.array([1.2, 6.5]),
            np.array([0.0, 10.0]),
            np.array([0.0, -6.0]),
        )
    )
    return fascicle


@pytest.mark.neuron
@pytest.mark.slow
def test_nerve_simulation_runs_with_multiple_fascicles(nrv_module) -> None:
    nerve = nrv_module.nerve(length=2500, diameter=300, Outer_D=3)
    nerve.add_fascicle(_build_fascicle_for_nerve(nrv_module, 1), y=-60, z=0)
    nerve.add_fascicle(_build_fascicle_for_nerve(nrv_module, 2), y=60, z=0)
    nerve.set_axons_parameters(dt=0.01, Nrec=5, rec="nodes")
    nerve.insert_I_Clamp(position=0.5, t_start=0.4, duration=0.1, amplitude=2.0)

    results = nerve.simulate(t_sim=1.5, postproc_script="is_recruited")

    assert results.n_fasc == 2
    assert results.n_ax == 4
    assert set(results.fascicle_keys) == {"fascicle1", "fascicle2"}
