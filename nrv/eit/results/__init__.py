"""
eit Results: standardized result gathering for eit simulations.

eit.results defines classes to gather results or list of results from eit forward simulations.

"""

from ._eit_forward_results import eit_forward_results, synchronize_times, load_res
from ._eit_results_list import eit_results_list, res_list_from_labels

# from . import

submodules = []

classes = [
    "eit_forward_results",
    "eit_results_list",
]

functions = [
    "synchronize_times",
    "load_res",
    "res_list_from_labels",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
