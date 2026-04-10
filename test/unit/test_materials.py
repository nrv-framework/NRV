from __future__ import annotations


def test_load_builtin_isotropic_material(nrv_module) -> None:
    material = nrv_module.load_material("material_1")

    assert material.is_isotropic() is True
    assert material.sigma == 1.0


def test_load_builtin_anisotropic_material(nrv_module) -> None:
    material = nrv_module.load_material("material_2")

    assert material.is_isotropic() is False
    assert material.sigma_xx == 1.0
    assert material.sigma_yy == 0.5
    assert material.sigma_zz == 0.5
