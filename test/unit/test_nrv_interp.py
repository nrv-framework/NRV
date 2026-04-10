from __future__ import annotations

import numpy as np


def test_linear_interpolator_matches_reference_points(nrv_module) -> None:
    x_values = np.array([0.0, 1.0, 2.0, 4.0])
    y_values = np.array([0.0, 1.0, 0.0, 2.0])

    interpolator = nrv_module.nrv_interp(x_values, y_values, kind="linear")
    y_interp = interpolator(np.array([0.0, 1.0, 2.0, 4.0]))

    assert np.allclose(y_interp, y_values)


def test_interpolator_operations_preserve_expected_arithmetic(nrv_module) -> None:
    x_values = np.array([0.0, 1.0, 2.0, 4.0])
    y_values = np.array([1.0, 2.0, 3.0, 4.0])
    sample = np.linspace(0.0, 4.0, 17)

    interpolator = nrv_module.nrv_interp(x_values, y_values, kind="cardinal", scale=0)

    doubled = interpolator + interpolator
    scaled = 2 * interpolator
    shifted = 10 + (interpolator / interpolator)

    assert np.allclose(doubled(sample), scaled(sample))
    assert np.allclose(shifted(sample), np.full_like(sample, 11.0))
