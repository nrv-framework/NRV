import numpy as np
from copy import deepcopy
import shapely as shp

from ._cshape import CShape
from .._units import to_nrv_unit
from .._misc import rotate_2D
from ...backend._log_interface import rise_warning, pass_info


class Polygon(CShape):
    """
    Polygon class that inherits from Cshape.
    Represents an polygon eiher from its vertices positions.
    """

    def __init__(self, vertices: tuple[float, float] = [[0, 0], [0, 1], [1, 0]]):
        """

        Parameters
        ----------
        vertices : tuple[float, float], optional
            Vertices of the polygone, by default [[0,0], [0,1], [1,0]]
        """
        self.vertices: np.ndarray[float] = np.array(vertices, dtype=float)
        if self.vertices.shape[0] == 2:
            pass_info("vertices of Polygon must be of dim (n_gon, 2) not (2, n_gon)")
            self.vertices = self.vertices.swapaxes(0, 1)

        super().__init__(center=np.mean(self.vertices, axis=0))
        # Mostely to have an idea of default mesh res
        self.radius = np.mean(np.hypot(self.c, self.vertices))

    @property
    def n_gon(self) -> int:
        """
        Number of polygon vertices.

        Returns
        -------
        int
            Vertex count.
        """
        return self.vertices.shape[0]

    @property
    def shp_poly(self) -> shp.Polygon:
        """
        Polygon representation as a :mod:`shapely` object.

        Returns
        -------
        shapely.Polygon
            Shapely polygon built from ``vertices``.
        """
        return shp.Polygon(self.vertices)

    @property
    def c(self) -> np.ndarray:
        """
        Center of the polygon as an array.

        Returns
        -------
        np.ndarray
            Polygon center coordinates.
        """
        return np.array(self.center, dtype=float)

    @property
    def area(self) -> float:
        """
        Area of the polygon.

        Returns
        -------
        float
            Polygon area.
        """
        # Shoelace formula
        _i = np.arange(self.n_gon)
        return np.abs(
            np.sum(
                self.vertices[_i, 0] * self.vertices[_i - 1, 1]
                - self.vertices[-1, 0] * self.vertices[_i, 1]
            )
        )

    @property
    def perimeter(self) -> float:
        """
        Perimeter of the polygon.

        Returns
        -------
        float
            Polygon perimeter.
        """
        return np.sum(np.hypot(*self.vertices.T))

    @property
    def bbox_size(self) -> tuple[float, float]:
        """
        Size of the polygon bounding box.

        Returns
        -------
        tuple[float, float]
            Bounding-box width and height.
        """
        _bbox = self.bbox
        return (
            _bbox[2] - _bbox[0],
            _bbox[3] - _bbox[1],
        )

    @property
    def bbox(self) -> np.ndarray:
        """
        Coordinates of the polygon bounding box.

        Returns
        -------
        np.ndarray
            Bounding box as ``[ymin, zmin, ymax, zmax]``.
        """
        return np.array(
            [
                np.min(self.vertices[:, 0]),
                np.min(self.vertices[:, 1]),
                np.max(self.vertices[:, 0]),
                np.max(self.vertices[:, 1]),
            ]
        )

    # Methods
    def is_inside(
        self, point: tuple[np.ndarray, np.ndarray], for_all: bool = True
    ) -> bool:
        """
        Check whether one or several points lie inside the polygon.

        Parameters
        ----------
        point : tuple[np.ndarray, np.ndarray]
            Point or set of points to test.
        for_all : bool, optional
            If ``True``, return a single boolean for all points.

        Returns
        -------
        bool | np.ndarray
            Inclusion test result.
        """
        if not np.iterable(point[0]):
            return self.shp_poly.contains(shp.Point(*point))

        if for_all:
            return self.shp_poly.contains(shp.points(np.array(point).T)).all()

        return self.shp_poly.contains(shp.points(np.array(point).T))

    def rotate(self, angle: float, degree: bool = False):
        """
        Rotate the polygon around its center.

        Parameters
        ----------
        angle : float
            Rotation angle.
        degree : bool, optional
            If ``True``, ``angle`` is provided in degrees.
        """
        self.vertices = rotate_2D(
            point=self.vertices,
            center=self.center,
            angle=angle,
            degree=degree,
            as_array=True,
        ).T

    def translate(self, y: float = 0, z: float = 0):
        """
        Translate the polygon.

        Parameters
        ----------
        y : float, optional
            Translation along the y axis.
        z : float, optional
            Translation along the z axis.
        """
        self.vertices += np.array([y, z])
        self.center = np.mean(self.vertices, axis=0)

    def get_trace(self, n_theta=100) -> tuple[list[float], list[float]]:
        """
        Get the trace of the ellipse.

        :return: A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        # return self.vertices[:, 0], self.vertices[:, 1]
        p = np.linspace(0, self.n_gon, n_theta, endpoint=True)
        i_p = p.astype(int) % self.n_gon
        t_p = (p % 1).reshape(n_theta, 1)
        tr = (self.vertices[i_p - 1] - self.vertices[i_p]) * (1 - t_p) + self.vertices[
            i_p
        ]
        return tr[:, 0], tr[:, 1]

    def get_point_inside(
        self, n_pts: int = 1, delta: float = 0, max_iter=1e5
    ) -> np.ndarray:
        """
        Draw random points inside the polygon by rejection sampling.

        Parameters
        ----------
        n_pts : int, optional
            Number of points to generate.
        delta : float, optional
            Minimum distance kept from the boundary.
        max_iter : int, optional
            Maximum number of rejection-sampling iterations.

        Returns
        -------
        np.ndarray
            Generated points of shape ``(n_pts, 2)``.
        """
        points = np.zeros((n_pts, 2))
        _poly = self.shp_poly
        minx, miny, maxx, maxy = _poly.bounds
        i, _iter = 0, 0
        if delta == 0:
            gen_point = lambda X: shp.Point(*X)
        else:
            gen_point = lambda X: shp.Point(*X).buffer(delta)
        while i < n_pts and _iter < max_iter:
            # pnt = np.random.uniform(minx, maxx, 2)
            pnt = (np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            _iter += 1
            if _poly.contains(gen_point(pnt)):
                points[i, :] = pnt
                i += 1
            if _iter > max_iter:
                rise_warning(f"Max Iteration reach: only {i} points placed")
                break
        return points
