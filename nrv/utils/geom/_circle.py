from ._ellipse import Ellipse
import numpy as np


class Circle(Ellipse):
    """
    Circle class that inherits from Cshape.
    Represents a circle with a center and radius.
    """

    def __init__(self, center: tuple[float, float] = (0, 0), radius: float = 10):
        """
        Initializes the `Circle`

        Parameters
        ----------
        center : tuple[float, float], optional
            Center of the shape, by default (0,0)
        radius : float , optional
            Radius of the shape, by default 10
        """
        super().__init__(center=center, radius=(radius, radius), rot=0)
        self.radius = radius

    @property
    def perimeter(self) -> float:
        """
        Perimeter of the shape in $\\mu m^2$
        """
        return 2 * np.pi * self.r

    @property
    def bbox_size(self) -> tuple[float, float]:
        """
        Size of the circle bounding box.

        Returns
        -------
        tuple[float, float]
            Bounding-box width and height.
        """
        return 2 * self.radius, 2 * self.radius

    def rotate(self, angle: float, degree: bool = False):
        """
        Rotate the circle.

        Parameters
        ----------
        angle : float
            Rotation angle.
        degree : bool, optional
            If ``True``, ``angle`` is expressed in degrees.
        """
        pass

    def get_point_inside(self, n_pts: int = 1, delta: float = 0) -> np.ndarray:
        """
        Draw random points inside the circle.

        Parameters
        ----------
        n_pts : int, optional
            Number of points to generate.
        delta : float, optional
            Minimum distance to keep from the boundary.

        Returns
        -------
        np.ndarray
            Array of shape ``(n_pts, 2)`` containing generated points.
        """
        cr = (self.radius - delta) * np.sqrt(np.random.random(n_pts))
        cphi = 2 * np.pi * np.random.random(n_pts)

        X = np.vstack((cr * np.cos(cphi), cr * np.sin(cphi))).T
        X += self.c
        return X
