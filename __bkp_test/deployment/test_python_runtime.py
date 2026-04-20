from __future__ import annotations

import sys


def test_python_runtime_reports_supported_gil_status_api() -> None:
    py_version = float(".".join(sys.version.split()[0].split(".")[0:2]))

    if py_version >= 3.13:
        status = sys._is_gil_enabled()
        assert status in (0, 1)
    else:
        assert not hasattr(sys, "_is_gil_enabled") or callable(sys._is_gil_enabled)
