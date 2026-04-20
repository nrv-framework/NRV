from __future__ import annotations

import numpy as np


def test_biphasic_stimulus_builds_expected_polarities(nrv_module) -> None:
    stim = nrv_module.stimulus()
    stim.biphasic_pulse(start=1.0, s_cathod=40.0, t_stim=0.1, s_anod=8.0, t_inter=0.05)

    assert np.isclose(np.min(stim.s), -40.0)
    assert np.isclose(np.max(stim.s), 8.0)
    assert np.isclose(stim.t[1], 1.0)
    assert len(stim.t) >= 5


def test_biphasic_context_modifier_updates_saved_axon_context(
    nrv_module, legacy_sources_dir
) -> None:
    context_path = legacy_sources_dir / "200_unmyelinated_axon.json"
    context_modifier = nrv_module.biphasic_stimulus_CM(
        start=1.0,
        s_cathod="0",
        t_cathod="1",
        s_anod=0,
    )

    local_context = context_modifier(np.array([80.0, 0.2]), str(context_path))
    stimulus = local_context.extra_stim.stimuli[0]

    assert np.isclose(np.min(stimulus.s), -80.0)
    assert np.isclose(stimulus.t[1], 1.0)
    assert np.isclose(stimulus.t[2], 1.2)
