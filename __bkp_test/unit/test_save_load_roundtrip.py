from __future__ import annotations

import numpy as np


def test_axon_save_load_roundtrip_preserves_basic_identity(
    nrv_module, tmp_path
) -> None:
    axon = nrv_module.unmyelinated(0, 0, 1, 1000, model="HH", dt=0.01, Nrec=5)
    save_path = tmp_path / "axon.json"
    axon.save(save=True, fname=str(save_path))

    loaded = nrv_module.load_axon(str(save_path))

    assert loaded is not None
    assert loaded.myelinated is False
    assert loaded.d == axon.d
    assert loaded.L == axon.L


def test_fascicle_save_load_roundtrip_preserves_population(
    nrv_module, tmp_path
) -> None:
    fascicle = nrv_module.fascicle(diameter=100, ID=3)
    fascicle.define_length(2000)
    fascicle.axons.create_population_from_data(
        (
            np.array([0, 1], dtype=int),
            np.array([1.0, 6.0]),
            np.array([0.0, 10.0]),
            np.array([0.0, -5.0]),
        )
    )
    save_path = tmp_path / "fascicle.json"
    fascicle.save(save=True, fname=str(save_path))

    loaded = nrv_module.load_fascicle(str(save_path))

    assert loaded is not None
    assert loaded.ID == fascicle.ID
    assert loaded.axons.n_ax == fascicle.axons.n_ax


def test_nerve_save_load_roundtrip_preserves_fascicle_count(
    nrv_module, tmp_path
) -> None:
    nerve = nrv_module.nerve(length=3000, diameter=300, Outer_D=3, ID=7)
    for fascicle_id, y_pos in ((1, -60), (2, 60)):
        fascicle = nrv_module.fascicle(diameter=90, ID=fascicle_id)
        fascicle.axons.create_population_from_data(
            (
                np.array([0, 1], dtype=int),
                np.array([1.5, 7.5]),
                np.array([0.0, 8.0]),
                np.array([0.0, 5.0]),
            )
        )
        nerve.add_fascicle(fascicle, y=y_pos, z=0)

    save_path = tmp_path / "nerve.json"
    nerve.save(fname=str(save_path), save=True)

    loaded = nrv_module.load_nerve(str(save_path))

    assert loaded is not None
    assert loaded.ID == nerve.ID
    assert len(loaded.fascicles) == 2
