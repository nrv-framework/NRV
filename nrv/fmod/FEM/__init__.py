"""NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""

""" FEM-fmod librairy"""

from ._FEM import (
    FEM_model,
)
from ._COMSOL_model import (
    COMSOL_model,
)
from ._FENICS_model import (
    check_sim_dom,
    FENICS_model,
)

from . import fenics_utils, mesh_creator

submodules = [
    "fenics_utils",
    "mesh_creator",
]

classes = [
    "FEM_model",
    "COMSOL_model",
    "FENICS_model",
    "FENICS_lumped_impedance_model",
]

functions = [
    "check_sim_dom",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
