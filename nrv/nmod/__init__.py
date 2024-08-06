"""
Nmod librairy for neural models
"""

from ._axon_pop_generator import load_stat, create_axon_population, fill_area_with_axons, axon_packer, expand_pop, remove_collision, remove_outlier_axons, get_circular_contour, plot_population, save_axon_population, load_axon_population
from ._axons import axon
from ._unmyelinated import unmyelinated
from ._myelinated import myelinated
from ._fascicles import fascicle
from ._nerve import nerve
from . import results

submodules = ["results"]

classes = ["axon", "unmyelinated", "myelinated", "fascicle", "nerve"]

functions = [
    "load_stat",
    "create_axon_population",
    "fill_area_with_axons",
    "axon_packer",
    "expand_pop",
    "remove_collision",
    "remove_outlier_axons",
    "get_circular_contour",
    "plot_population",
    "save_axon_population",
    "load_axon_population",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions