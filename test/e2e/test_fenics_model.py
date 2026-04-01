from __future__ import annotations

import pytest


@pytest.mark.fenics
@pytest.mark.slow
def test_fenics_model_can_build_a_default_mesh(nrv_module, fenics_available) -> None:
    model = nrv_module.FENICS_model()

    model.reshape_outerBox(5.5)
    model.build_and_mesh()

    assert model.is_meshed is True
    assert model.mesh is not None
    assert model.Perineurium_thickness == {0: 5}
