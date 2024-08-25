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
from ._stimulus import (
    is_stim,
    set_common_time_series,
    get_equal_timing_copies,
    datfile_2_stim,
    stimulus,
)

submodules = [
    "FEM",
]

classes = [
    "electrode",
    "point_source_electrode",
    "FEM_electrode",
    "LIFE_electrode",
    "CUFF_electrode",
    "CUFF_MP_electrode",
    "extracellular_context",
    "stimulation",
    "FEM_stimulation",
    "material",
    "recording_point",
    "recorder",
    "stimulus"
]

functions = [
    "is_FEM_electrode",
    "is_CUFF_electrode",
    "is_LIFE_electrode",
    "is_analytical_electrode",
    "load_any_electrode",
    "check_electrodes_overlap",
    "is_extra_stim",
    "is_analytical_extra_stim",
    "is_FEM_extra_stim",
    "load_any_extracel_context",
    "is_mat",
    "get_mat_file_as_dict",
    "load_material",
    "compute_effective_conductivity",
    "is_recording_point",
    "is_recorder",
    "NodeD_interpol",
    "is_stim",
    "set_common_time_series",
    "get_equal_timing_copies",
    "datfile_2_stim",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
