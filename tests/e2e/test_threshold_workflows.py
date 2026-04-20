from __future__ import annotations

import pytest


def _kes_update(axon, amp, freq_kes, t_kes, start_kes=0.2, elec_id=0):
    stimulus = axon.extra_stim.stimuli[elec_id]
    new_stimulus = axon.extra_stim.stimuli[elec_id].__class__()
    new_stimulus.sinus(start_kes, t_kes, amp, freq_kes)
    axon.change_stimulus_from_electrode(elec_id, new_stimulus)


@pytest.mark.neuron
@pytest.mark.slow
def test_firing_threshold_search_from_saved_axon_runs(
    nrv_module, legacy_sources_dir
) -> None:
    axon = nrv_module.load_axon(
        str(legacy_sources_dir / "89_axon.json"),
        extracel_context=True,
    )

    threshold = nrv_module.firing_threshold_from_axon(
        axon,
        cath_time=0.1,
        amp_max=50,
        amp_tol=20,
        verbose=False,
        amp_tol_abs=10,
        t_sim=3,
    )

    assert isinstance(threshold, float)
    assert threshold >= 0


@pytest.mark.neuron
@pytest.mark.slow
def test_block_threshold_search_runs_on_small_myelinated_setup(nrv_module) -> None:
    axon = nrv_module.myelinated(0, 0, 8, 5000, model="MRG", rec="nodes", dt=0.01)

    electrode = nrv_module.point_source_electrode(2500, 100, 0)
    base_stimulus = nrv_module.stimulus()
    base_stimulus.sinus(0.2, 1.5, 5, 10)
    extra_stim = nrv_module.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(electrode, base_stimulus)
    axon.attach_extracellular_stimulation(extra_stim)
    axon.insert_I_Clamp(0.05, 1.0, 0.1, 2.0)

    threshold = nrv_module.axon_block_threshold(
        axon=axon,
        amp_max=20,
        update_func=_kes_update,
        args_update={"freq_kes": 10, "elec_id": 0, "start_kes": 0.2, "t_kes": 1.5},
        AP_start=1.0,
        freq=10,
        t_sim=2.0,
        tol=50,
        verbose=False,
        amp_tol_abs=10,
    )

    assert isinstance(threshold, float)
    assert threshold >= 0
