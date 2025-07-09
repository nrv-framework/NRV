"""nmod util: utils function and class specific to nmod sub-package.

nmod utils mostly gather tools to build axon populations.

"""

from ._packers import (
    Placer,
    dist_matrix,
    get_ppop_info,
    axon_packer,
    get_circular_contour,
    expand_pop,
    remove_collision,
    remove_outlier_axons,
)

from ._axon_pop_generator import (
    load_stat,
    create_axon_population,
    fill_area_with_axons,
    plot_population,
    save_axon_population,
    load_axon_population,
)


submodules = []

classes = [
    "Placer",
]

functions = [
    "dist_matrix",
    "get_ppop_info",
    "axon_packer",
    "get_circular_contour",
    "expand_pop",
    "remove_collision",
    "remove_outlier_axons",
    "load_stat",
    "create_axon_population",
    "fill_area_with_axons",
    "plot_population",
    "save_axon_population",
    "load_axon_population",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
