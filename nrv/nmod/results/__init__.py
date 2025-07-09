"""nmod Results: standardized result gathering for nmod simulations.

nmod.results defines classes to gather results from nmod object simulations.
Result classes are defined for axons (myelinated and unlyelinated), fascicles
and nerves. All computed values, state variables and electrical quantities are
stored and exportable as dictionaries (json format).

"""

from ._axons_results import axon_results
from ._unmyelinated_results import unmyelinated_results
from ._myelinated_results import myelinated_results
from ._fascicles_results import fascicle_results
from ._nerve_results import nerve_results


submodules = []

classes = [
    "axon_results",
    "unmyelinated_results",
    "myelinated_results",
    "fascicle_results",
    "nerve_results",
]

functions = []

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
