from __future__ import annotations

import pytest


@pytest.mark.fenics
@pytest.mark.slow
def test_fenics_backend_can_mesh_solve_and_sample_potentials(
    nrv_module, fenics_available
) -> None:
    model = nrv_module.FENICS_model()
    model.reshape_outerBox(5.5)
    model.build_and_mesh()
    model.solve()

    potentials = model.get_potentials([0, 250, 500], 30, 0)

    assert model.is_computed is True
    assert len(potentials) == 3


def test_saved_context_loaders_cover_axon_fascicle_and_nerve(
    nrv_module, legacy_sources_dir
) -> None:
    axon = nrv_module.load_axon(str(legacy_sources_dir / "200_unmyelinated_axon.json"))
    fascicle = nrv_module.load_fascicle(str(legacy_sources_dir / "56_fasc.json"))
    nerve = nrv_module.load_nerve(str(legacy_sources_dir / "400_1uax_nerve.json"))

    assert axon is not None
    assert fascicle is not None
    assert nerve is not None
