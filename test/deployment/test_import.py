from __future__ import annotations


def test_nrv_import_exposes_project_metadata(nrv_module) -> None:
    assert nrv_module.__title__ == "NeuRon Virtualizer"
    assert nrv_module.__project__ == "NeuRon Virtualizer (NRV)"
    assert isinstance(nrv_module.__version__, str)
    assert nrv_module.__version__


def test_nrv_configuration_is_initialized(nrv_module) -> None:
    assert hasattr(nrv_module, "CONFIG")
    assert nrv_module.CONFIG is not None
