"""
Interface between NRV and multiprocessing tools handling.

.. note::
  In the future, will also be used to handle the compatibility with threading
"""

from ._machine_config import MachineConfig

from pathos.multiprocessing import ProcessingPool

# from pathos.pp import ParallelPythonPool
# from multiprocessing.dummy import Pool as ThreadPool
# from pathos.multiprocessing import ProcessingPool as Pool
from multiprocessing import current_process, active_children, get_context
from psutil import cpu_count
from typing import Literal

# Not great but remove the resource_tracker warning. Doesn't seem to be an issue
import warnings

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message="resource_tracker: There appear to be .* leaked semaphore",
)


_DEFAULT_BACKEND = "pathos"

this_machine = MachineConfig()


def get_pool(
    n_jobs, backend: None | Literal["spawn", "pathos", "pp"] = None
) -> ProcessingPool:
    """
    Return a worker pool based on the specified backend.

    Supported backends:
        - "spawn"  : Python's multiprocessing with spawn context (safe on macOS)
        - "pathos" : pathos.multiprocessing (more flexible but uses fork)
        - "pp"     : pathos.pp.ParallelPythonPool (no fork, safe for macOS)

    Parameters:
        n_jobs (int): Number of worker processes (defaults to os.cpu_count()).
        backend (str): One of 'spawn', 'pathos', or 'pp'.

    Returns:
        Pool-like object with .map() method.
    """
    backend = backend or _DEFAULT_BACKEND

    if backend == "spawn":
        # Safe multiprocessing using spawn context (safer on macOS)
        ctx = get_context("spawn")
        return ctx.Pool(n_jobs)

    elif backend == "pathos":
        # WARNING: pathos.multiprocessing uses fork, which can be unsafe on macOS
        return ProcessingPool(n_jobs)

    # elif backend == "pp":
    # pathos.pp uses Parallel Python backend (spawn-like, macOS friendly but not really tested)
    #    return ParallelPythonPool(n_jobs)

    # elif backend == "thread":
    #    # Not recommanded with GIL - Not tested and doesn't probably work anyway
    #  return ThreadPool(n_jobs)

    else:
        raise ValueError(f"Unsupported pool backend: {backend}")


_cpu_max_number = this_machine.CPU_ncores  # cpu_count(logical=True)

_proc_is_master = current_process().name == "MainProcess"
_proc_is_alone = _proc_is_master and len(active_children()) == 0
_proc_label = current_process().name
