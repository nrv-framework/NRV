from __future__ import annotations

import numpy as np
import pytest


@pytest.mark.neuron
@pytest.mark.slow
def test_myelinated_axon_intracellular_simulation_runs_and_rasterizes(
    nrv_module,
) -> None:
    axon = nrv_module.myelinated(0, 0, 8, 4000, dt=0.01, rec="nodes")
    axon.insert_I_Clamp(0.5, 0.5, 0.1, 2.0)

    results = axon.simulate(t_sim=2.0)
    results.rasterize("V_mem")

    assert {"t", "V_mem", "x_rec", "node_index"}.issubset(results.keys())
    assert results["V_mem"].ndim == 2
    assert len(results["node_index"]) > 0
    assert isinstance(results.is_recruited("V_mem"), (bool, np.bool_))


@pytest.mark.neuron
@pytest.mark.slow
def test_myelinated_axon_extracellular_stimulation_and_recording_run(
    nrv_module,
) -> None:
    axon = nrv_module.myelinated(0, 0, 6, 5000, rec="all", dt=0.01)

    electrode = nrv_module.point_source_electrode(2500, 100, 0)
    stimulus = nrv_module.stimulus()
    stimulus.biphasic_pulse(0.5, 50, 0.05, 10, 0.02)
    extra_stim = nrv_module.stimulation(nrv_module.load_material("endoneurium_ranck"))
    extra_stim.add_electrode(electrode, stimulus)
    axon.attach_extracellular_stimulation(extra_stim)

    recorder = nrv_module.recorder("endoneurium_ranck")
    recorder.set_recording_point(2500, 150, 0)
    axon.attach_extracellular_recorder(recorder)

    results = axon.simulate(t_sim=2.0, record_I_mem=True)

    assert {"t", "V_mem", "x_rec", "recorder"}.issubset(results.keys())
    assert len(results["recorder"]["recording_points"]) >= 1
    assert len(results["recorder"]["recording_points"][0]["recording"]) == len(
        results["t"]
    )
