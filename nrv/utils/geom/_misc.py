
import numpy as np

from ._cshape import CShape
from ._ellipse import Ellipse
from ._circle import Circle


def create_cshape(
    center: tuple[float, float] = (0, 0),
    radius: float | tuple[float, float] = 10,
    rot: None | float = None,
    diameter: None | float | tuple[float, float] = None,
)->CShape:
    """
    generate a CShape from parameters

    Parameters
    ----------
    center : tuple[float, float], optional
        _description_, by default (0, 0)
    radius : float | tuple[float, float], optional
        _description_, by default 10
    rot : None | float, optional
        _description_, by default None
    diameter : None | float | tuple[float, float], optional
        _description_, by default None

    Returns
    -------
    CShape
    """
    if isinstance(diameter, tuple):
        radius = tuple([_d/2 for _d in diameter])
    elif diameter is not None:
        radius = diameter / 2

    if isinstance(radius, tuple):
        geom = Ellipse(center=center, radius=radius, rot=rot)
    else:
        geom = Circle(center=center, radius=radius)
    return geom


def get_cshape_bbox(shape:CShape, looped_end:bool=False):
    y_bbox = (
        shape.center[0]-shape.bbox_size[0]/2,
        shape.center[0]+shape.bbox_size[0]/2,
    )
    z_bbox = (
        shape.center[1]-shape.bbox_size[1]/2,
        shape.center[1]+shape.bbox_size[1]/2,
    )

    bbox = np.array([
        (y_bbox[0], z_bbox[0]),
        (y_bbox[1], z_bbox[0]),
        (y_bbox[1], z_bbox[1]),
        (y_bbox[0], z_bbox[1]),
    ])
    if looped_end:
        bbox = np.vstack((
            bbox,
            (y_bbox[0], z_bbox[0]),
        ))
    return bbox


def overlap_checker(c:np.ndarray, r:float, c_comp:np.ndarray, r_comp:np.ndarray, delta:float=0)->np.ndarray[bool]:
    """
    Check if a cicle of center ``c`` and radius ``r`` overlap with a list of circles of center ``c_comp`` and radius ``r_comp``

    Parameters
    ----------
    c : np.ndarray
        2D position of the center of the circle.
    r : float
        radius of the circle.
    c_comp : np.ndarray
        Array, or shape listing the 2D position of the center of the circles to compare.
    r_comp : np.ndarrayn
        Array listing the radius of the circles to compare.
    delta : float, optional
        Additional extra space between circles perimeter, by default 0.

    Returns
    -------
    np.ndarray[bool]
    """
    d = np.sqrt(np.sum((c_comp - c)**2, axis=-1))
    return d < r_comp + r + delta