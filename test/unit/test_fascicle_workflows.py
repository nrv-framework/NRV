from __future__ import annotations

import numpy as np


def _build_small_fascicle(nrv_module, fascicle_id: int = 1):
    fascicle = nrv_module.fascicle(diameter=80, ID=fascicle_id)
    fascicle.axons.create_population_from_data(
        (
            np.array([0, 1, 0], dtype=int),
            np.array([1.0, 8.0, 2.0]),
            np.array([0.0, 10.0, -12.0]),
            np.array([0.0, 0.0, 8.0]),
        )
    )
    return fascicle


def test_fascicle_fill_builds_a_small_population(nrv_module) -> None:
    np.random.seed(1)
    fascicle = nrv_module.fascicle(diameter=90, ID=5)
    fascicle.fill(n_ax=6, percent_unmyel=0.5, delta=2.0, n_iter=40)

    assert nrv_module.is_fascicle(fascicle)
    assert fascicle.axons.n_ax == 6
    assert "is_placed" in fascicle.axons.axon_pop.columns
    assert fascicle.axons.axon_pop["is_placed"].any()


def test_fascicle_insert_iclamp_can_target_subpopulation_by_expression(nrv_module) -> None:
    fascicle = _build_small_fascicle(nrv_module)

    fascicle.insert_I_Clamp(
        position=0.5,
        t_start=0.5,
        duration=0.1,
        amplitude=2.0,
        expr="diameters > 5",
    )

    selected = fascicle.intra_stim_ON[0]

    assert fascicle.N_intra == 1
    assert len(selected) == 1
    assert fascicle.axons.axon_pop.iloc[selected[0]]["diameters"] > 5


def test_fascicle_insert_iclamp_can_use_named_masks(nrv_module) -> None:
    fascicle = _build_small_fascicle(nrv_module)
    fascicle.axons.add_mask(data="types == 0", label="unmyelinated")

    fascicle.insert_I_Clamp(
        position=0.25,
        t_start=0.2,
        duration=0.05,
        amplitude=1.0,
        mask_labels="unmyelinated",
    )

    selected = fascicle.intra_stim_ON[0]

    assert len(selected) == 2
    assert (fascicle.axons.axon_pop.iloc[selected]["types"] == 0).all()
