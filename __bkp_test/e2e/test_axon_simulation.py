from __future__ import annotations

import numpy as np
import pytest


@pytest.mark.neuron
@pytest.mark.slow
def test_unmyelinated_axon_simulation_generates_membrane_voltage(nrv_module) -> None:
    axon = nrv_module.unmyelinated(
        0,
        0,
        1,
        2000,
        model="HH",
        dt=0.01,
        Nrec=9,
        Nsec=1,
    )
    axon.insert_I_Clamp(0.5, 0.5, 0.1, 5.0)

    results = axon(t_sim=2.0)

    assert {"t", "V_mem", "x_rec"}.issubset(results.keys())
    assert results["V_mem"].ndim == 2
    assert results["V_mem"].shape[0] == len(results["x_rec"])
    assert results["V_mem"].shape[1] == len(results["t"])
    assert np.max(results["V_mem"]) > np.min(results["V_mem"])
