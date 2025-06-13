"""FIELD Models - fmod: handles extracellular field models.

fmod hosts the code to compute extracellular electrical fields and quantities.
Such quantity can result from both:


* electrical stimulation, handled by injecting stimulation current waveforms
  on electrodes. Associated computations can be performed using analitical
  approach (fast but relying on strong hypotheses), or using Finite Element
  models,
* the activity of the cells. In this second case, computations are for the
  moment only performed with an analitical approach.


Finite Elements solver can be chosen between COMSOL (requieres extra license,
this is not the recommended choice and is maintained only for comparison with
existing results in the litterature) and FenicsX. This last solution is fully open
source and should be preferred. In this case, geometries are meshed using GMSH. All FEM
computations are handled by a subpackage called ``FEM`` (seel below).

.. note::
  for scientific details of how nmod works and an overview of the general
  implementation, refer to the 'Scientific foundations' section of the
  documentation.

"""

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
