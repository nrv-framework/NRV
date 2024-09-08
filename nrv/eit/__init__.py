"""Electrical Impedance Tomography - eit: models for neural impedance imaging

eit provides high level models for imaging techniques based on electrical
impedance sensing for neural activity reconstruction. Tissue properties are
computed taking into account the temporal and frequencial evolution of neural
membranes conductivity. Models are based on both Finite Differences (NEURON)
computations and FEM models.


.. warning::
  The eit sb-package is currently under construction and scientific validation.
  The code can change fast, results not guaranteed, and developpers do not
  ensure backwards compatibility.

"""

from ._eit_forward import eit_forward
from ._eit_inverse import eit_inverse
from ._eit_utils import crop_fascicle, crop_nerve
from ._protocol import protocol, pyeit_protocol

submodules = []

classes = [
    "eit_forward",
    "eit_inverse",
    "protocol",
    "pyeit_protocol",
]

functions = [
    "crop_fascicle",
    "crop_nerve",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
