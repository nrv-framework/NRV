import numpy as np

from ._cshape import CShape
from ._ellipse import Ellipse
from ._circle import Circle
from ._polygon import Polygon


def create_cshape(
    center: tuple[float, float] = (0, 0),
    radius: float | tuple[float, float] = 10,
    rot: None | float = None,
    degree: bool = False,
    diameter: None | float | tuple[float, float] = None,
    vertices: None | np.ndarray = None,
) -> CShape:
    """
    generate a CShape from parameters

    Parameters
    ----------
    center : tuple[float, float], optional
        Center of the shape, by default (0, 0)
    radius : float | tuple[float, float], optional
        Radius of the shape, by default 10
    rot : None | float, optional
        Rotation of the shape, by default None
    diameter : None | float | tuple[float, float], optional
        Diameter of the shape. If None, radius value is used to define the shape, by default None
    vertices: None|np.ndarray, optional
        If not none create a polygon with these vertices coordinate, by default None

    Returns
    -------
    CShape
    """
    if vertices is not None:
        return Polygon(vertices=vertices)
    if isinstance(diameter, tuple):
        radius = tuple([_d / 2 for _d in diameter])
    elif diameter is not None:
        radius = diameter / 2

    if isinstance(radius, tuple):
        return Ellipse(center=center, radius=radius, rot=rot, degree=degree)
    else:
        return Circle(center=center, radius=radius)


def get_cshape_bbox(shape: CShape, looped_end: bool = False):
    y_bbox = (
        shape.center[0] - shape.bbox_size[0] / 2,
        shape.center[0] + shape.bbox_size[0] / 2,
    )
    z_bbox = (
        shape.center[1] - shape.bbox_size[1] / 2,
        shape.center[1] + shape.bbox_size[1] / 2,
    )

    bbox = np.array(
        [
            (y_bbox[0], z_bbox[0]),
            (y_bbox[1], z_bbox[0]),
            (y_bbox[1], z_bbox[1]),
            (y_bbox[0], z_bbox[1]),
        ]
    )
    if looped_end:
        bbox = np.vstack(
            (
                bbox,
                (y_bbox[0], z_bbox[0]),
            )
        )
    return bbox


def circle_overlap_checker(
    c: np.ndarray, r: float, c_comp: np.ndarray, r_comp: np.ndarray, delta: float = 0
) -> np.ndarray[bool]:
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
    d = np.sqrt(np.sum((c_comp - c) ** 2, axis=-1))
    return d < r_comp + r + delta


def cshape_overlap_checker(
    s: CShape,
    s_comp: CShape | list[CShape],
    n_trace: int = 1000,
    on_trace: bool = False,
) -> bool | list[bool]:
    """
    Check if a `CShape` overlape with another or a list of them.

    Warning
    -------
    This version is not ideal and will be improved in the future

    Parameters
    ----------
    s : CShape
        _description_
    s_comp : CShape | list[CShape]
        _description_
    n_trace : int, optional
        _description_, by default 1000
    on_trace : bool, optional
        _description_, by default False

    Returns
    -------
    bool|list[bool]
        _description_
    """
    if isinstance(s_comp, CShape):
        _isin = s.is_inside(s_comp.get_trace(n_trace), for_all=False)
        if not on_trace:
            return True in _isin

        return True in _isin and False in _isin
    else:
        comp = []
        for s_c in s_comp:
            comp += [cshape_overlap_checker(s, s_c, n_trace=n_trace, on_trace=on_trace)]

        return comp
