"""
EIT librairy for Electrical Impedance Tomography models
"""

from ._eit_forward import eit_forward
from ._eit_inverse import eit_inverse
from _eit_utils import crop_fascicle, crop_nerve
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
