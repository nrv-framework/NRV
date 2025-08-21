"""
EIT models - eit: Handles the simulation of Electrical Impedance Tomography (EIT) in peripheral nerve.

This subpackage provides tools and classes for simulating, analyzing, and reconstructing electrical impedance tomography (EIT) in neural tissues.

Main modules:
-------------
- _eit_forward.py: Forward EIT simulation routines for 2D and 3D domains.
- _eit_inverse.py: Inverse EIT algorithms for reconstructing conductivity maps.
- _eit2d.py, _eit3d.py: Specialized 2D and 3D EIT solvers and utilities.
- _pyeit_inverse.py: Integration with PyEIT for advanced inverse methods.
- results/: Classes for storing and managing EIT simulation and reconstruction results.
- utils/: Plotting, protocol management, and miscellaneous EIT utilities.

Features:
---------
- Forward and inverse EIT solvers for neural applications.
- Support for multiple geometries and protocols.
- Result management and visualization tools.
- Utilities for protocol definition and plotting.

.. SeeAlso::
   :doc:`EIT users guide </usersguide/eit>` --- For generic description.

    :doc:`Tutorial 6 </tutorials/6_play_with_eit>` --- For usage description.
"""

from ._eit_forward import eit_forward
from ._eit_inverse import eit_inverse
from ._eit3d import EIT3DProblem
from ._eit2d import EIT2DProblem
from ._eit_forward import static_env
from ._pyeit_inverse import pyeit_inverse

from . import results
from . import utils


# from . import

submodules = ["utils", "results"]

classes = [
    "eit_forward",
    "eit_inverse",
    "EIT3DProblem",
    "EIT2DProblem",
    "pyeit_inverse",
]

functions = [
    "static_env",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
