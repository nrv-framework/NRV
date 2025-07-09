"""Utils: general purpose functions and classes

utils provides some classes and functions for runing and interconnecting code
from the scientific sub-packages.
"""

from ._misc import (
    distance_point2point,
    distance_point2line,
    nearest_idx,
    nearest_greater_idx,
    in_tol,
    get_perineurial_thickness,
    membrane_capacitance_from_model,
    compute_complex_admitance,
    get_MRG_parameters,
    get_length_from_nodes,
)
from ._nrv_function import (
    nrv_function,
    function_1D,
    gaussian,
    gate,
    function_2D,
    ackley,
    beale,
    goldstein_price,
    booth,
    bukin6,
    function_ND,
    Id,
    rosenbock,
    rastrigin,
    sphere,
    cost_evaluation,
    nrv_interp,
    MeshCallBack,
)

from ._units import (
    print_default_nrv_unit,
    from_nrv_unit,
    to_nrv_unit,
    convert,
    sci_round,
)

from ._stimulus import (
    is_stim,
    set_common_time_series,
    get_equal_timing_copies,
    datfile_2_stim,
    stimulus,
)

from . import geom


submodules = ["geom"]

classes = [
    "nrv_function",
    "function_1D",
    "gaussian",
    "gate",
    "function_2D",
    "ackley",
    "beale",
    "goldstein_price",
    "booth",
    "bukin6",
    "function_ND",
    "Id",
    "rosenbock",
    "rastrigin",
    "sphere",
    "cost_evaluation",
    "nrv_interp",
    "MeshCallBack",
    "stimulus",
]

functions = [
    "distance_point2point",
    "distance_point2line",
    "nearest_idx",
    "nearest_greater_idx",
    "in_tol",
    "get_perineurial_thickness",
    "membrane_capacitance_from_model",
    "compute_complex_admitance",
    "print_default_nrv_unit",
    "from_nrv_unit",
    "to_nrv_unit",
    "convert",
    "sci_round",
    "is_stim",
    "set_common_time_series",
    "get_equal_timing_copies",
    "datfile_2_stim",
    "get_MRG_parameters",
    "get_length_from_nodes",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
