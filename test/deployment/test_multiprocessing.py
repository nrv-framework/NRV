from __future__ import annotations

import pytest


def _dispatch_square(x: float, offset: float = 0.0) -> float:
    return x * x + offset


@pytest.mark.slow
def test_search_threshold_dispatcher_runs_with_spawned_workers(nrv_module) -> None:
    values = [0.0, 1.0, 2.0]
    results = nrv_module.search_threshold_dispatcher(
        _dispatch_square,
        values,
        ncore=2,
        offset=1.0,
    )

    assert results == [1.0, 2.0, 5.0]
