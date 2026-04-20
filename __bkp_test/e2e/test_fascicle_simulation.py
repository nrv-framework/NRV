from __future__ import annotations

import numpy as np
import pytest


def _build_simulated_fascicle(nrv_module):
    fascicle = nrv_module.fascicle(diameter=100, ID=1)
    fascicle.define_length(2500)
    fascicle.axons.create_population_from_data(
        (
            np.array([0, 1], dtype=int),
            np.array([1.0, 7.0]),
            np.array([0.0, 15.0]),
            np.array([0.0, -10.0]),
        )
    )
    fascicle.set_axons_parameters(dt=0.01, Nrec=7, rec="nodes")
    fascicle.insert_I_Clamp(position=0.5, t_start=0.4, duration=0.1, amplitude=2.0)
    return fascicle


@pytest.mark.neuron
@pytest.mark.slow
def test_fascicle_simulation_runs_and_returns_axon_results(nrv_module) -> None:
    fascicle = _build_simulated_fascicle(nrv_module)

    results = fascicle.simulate(t_sim=1.5, postproc_script="is_recruited")

    assert results.n_ax == 2
    assert len(results.get_axons_key()) >= 1
    assert isinstance(results.get_recruited_axons(), (int, np.integer))
