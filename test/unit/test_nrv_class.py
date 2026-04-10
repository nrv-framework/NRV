from __future__ import annotations

import pytest


def test_nrv_class_save_serializes_nested_objects(nrv_module) -> None:
    class Child(nrv_module.NRV_class):
        def __init__(self) -> None:
            super().__init__()
            self.type = "child"
            self.value = 2

        def __hash__(self) -> int:
            return 0

    class Parent(nrv_module.NRV_class):
        def __init__(self) -> None:
            super().__init__()
            self.type = "parent"
            self.value = 1
            self.child = Child()

    payload = Parent().save()

    assert payload["type"] == "parent"
    assert payload["value"] == 1
    assert payload["child"]["type"] == "child"
    assert payload["child"]["value"] == 2


def test_base_nrv_class_cannot_be_instantiated(nrv_module) -> None:
    with pytest.raises(TypeError):
        nrv_module.NRV_class()
