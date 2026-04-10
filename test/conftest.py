from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TEST_ROOT = Path(__file__).resolve().parent


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: fast API-level tests")
    config.addinivalue_line("markers", "e2e: strategic end-to-end workflow tests")
    config.addinivalue_line(
        "markers", "deployment: environment and runtime sanity checks"
    )
    config.addinivalue_line(
        "markers", "neuron: tests that exercise NEURON-backed simulation workflows"
    )
    config.addinivalue_line(
        "markers", "fenics: tests that require the FEniCS/dolfinx stack"
    )
    config.addinivalue_line("markers", "slow: tests that are expected to take longer")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    family_markers = {
        "unit": pytest.mark.unit,
        "e2e": pytest.mark.e2e,
        "deployment": pytest.mark.deployment,
    }

    for item in items:
        path = Path(str(item.fspath)).resolve()
        relative_parts = path.relative_to(TEST_ROOT).parts
        if relative_parts:
            family = relative_parts[0]
            marker = family_markers.get(family)
            if marker is not None:
                item.add_marker(marker)


@pytest.fixture(scope="session")
def nrv_module():
    return pytest.importorskip(
        "nrv",
        reason="NRV and its scientific runtime dependencies must be available",
    )


@pytest.fixture(scope="session")
def fenics_available():
    return pytest.importorskip(
        "dolfinx",
        reason="FEniCS/dolfinx is required for this test",
    )


@pytest.fixture(scope="session")
def project_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def legacy_sources_dir(project_root: Path) -> Path:
    return project_root / "tests" / "unitary_tests" / "sources"
