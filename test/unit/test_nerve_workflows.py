from __future__ import annotations

import numpy as np


def _small_fascicle(nrv_module, fascicle_id: int, shift: float):
    fascicle = nrv_module.fascicle(diameter=90, ID=fascicle_id)
    fascicle.axons.create_population_from_data(
        (
            np.array([0, 1], dtype=int),
            np.array([1.5, 7.5]),
            np.array([0.0 + shift, 8.0 + shift]),
            np.array([0.0, 5.0]),
        )
    )
    return fascicle


def test_nerve_can_group_multiple_fascicles(nrv_module) -> None:
    nerve = nrv_module.nerve(length=3000, diameter=300, Outer_D=3)
    fascicle_1 = _small_fascicle(nrv_module, fascicle_id=1, shift=0.0)
    fascicle_2 = _small_fascicle(nrv_module, fascicle_id=2, shift=0.0)

    nerve.add_fascicle(fascicle_1, y=-60, z=0)
    nerve.add_fascicle(fascicle_2, y=60, z=0)

    assert set(nerve.fascicles.keys()) == {1, 2}
    assert nerve.fascicles[1].L == nerve.L
    assert nerve.fascicles[2].L == nerve.L


def test_nerve_insert_iclamp_can_target_specific_fascicles(nrv_module) -> None:
    nerve = nrv_module.nerve(length=3000, diameter=300, Outer_D=3)
    nerve.add_fascicle(_small_fascicle(nrv_module, fascicle_id=1, shift=0.0), y=-60, z=0)
    nerve.add_fascicle(_small_fascicle(nrv_module, fascicle_id=2, shift=0.0), y=60, z=0)

    nerve.insert_I_Clamp(
        position=0.5,
        t_start=0.4,
        duration=0.1,
        amplitude=2.0,
        fasc_list=[1],
    )

    assert nerve.N_intra == 1
    assert nerve.fascicles[1].N_intra == 1
    assert nerve.fascicles[2].N_intra == 0


def test_nerve_save_keeps_fascicular_structure(nrv_module) -> None:
    nerve = nrv_module.nerve(length=3000, diameter=300, Outer_D=3)
    nerve.add_fascicle(_small_fascicle(nrv_module, fascicle_id=1, shift=0.0), y=-60, z=0)
    nerve.add_fascicle(_small_fascicle(nrv_module, fascicle_id=2, shift=0.0), y=60, z=0)

    payload = nerve.save(save=False, fascicles_context=True)

    assert "fascicles" in payload
    assert len(payload["fascicles"]) == 2
    assert set(payload["fascicles"].keys()) == {"1", "2"}
