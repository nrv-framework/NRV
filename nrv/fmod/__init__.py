""" NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""
""" Fmod librairy for field models"""

from ._electrodes import (
    is_FEM_electrode,
    is_CUFF_electrode,
    is_LIFE_electrode,
    is_analytical_electrode,
    load_any_electrode,
    check_electrodes_overlap,
    electrode,
    point_source_electrode,
    FEM_electrode,
    LIFE_electrode,
    CUFF_electrode,
    CUFF_MP_electrode,
    
)
from ._extracellular import (
    is_extra_stim,
    is_analytical_extra_stim,
    is_FEM_extra_stim,
    load_any_extracel_context,
    extracellular_context,
    stimulation,
    FEM_stimulation,
)
from ._materials import (
    is_mat,
    get_mat_file_as_dict,
    load_material,
    compute_effective_conductivity,
    material,
)
from ._recording import (
    is_recording_point,
    is_recorder,
    NodeD_interpol,
    recording_point,
    recorder,
)

from . import FEM
submodules = [
    "FEM",
]

classes = [
    "material",
    "electrode",
    "point_source_electrode",
    "FEM_electrode",
    "LIFE_electrode",
    "CUFF_electrode",
    "CUFF_MP_electrode",
    "extracellular_context",
    "stimulation",
    "FEM_stimulation",
    "recording_point",
    "recorder",
]

functions = [
    "is_FEM_electrode",
    "is_CUFF_electrode",
    "is_LIFE_electrode",
    "is_analytical_electrode",
    "is_extra_stim",
    "is_analytical_extra_stim",
    "is_FEM_extra_stim",
    "is_mat",
    "is_recording_point",
    "is_recorder",
    "load_any_electrode",
    "load_any_extracel_context",
    "load_material",
    "check_electrodes_overlap",
    "get_mat_file_as_dict",
    "compute_effective_conductivity",
    "NodeD_interpol",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
