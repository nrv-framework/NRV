"""Utils Geometrical general purpose functions and classes

utils.geom provides some classes and functions allowing to desig and handle various geomatrical shapes.
"""

from ._circle import Circle
from ._ellipse import Ellipse
from ._misc import (
    create_cshape,
    get_cshape_bbox,
    overlap_checker,
)



submodules = []

classes = [
    "Circle",
    "Ellipse",
]

functions = [
    "create_cshape",
    "get_cshape_bbox",
    "overlap_checker",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
