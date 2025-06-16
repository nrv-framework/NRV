"""Utils Geometrical general purpose functions and classes

utils.geom provides some classes and functions allowing to desig and handle various geomatrical shapes.
"""

from ._circle import Circle
from ._ellipse import Ellipse



submodules = []

classes = [
    "Circle",
    "Ellipse",
]

functions = []

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
