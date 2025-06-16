from ._ellipse import Ellipse
import numpy as np

class Circle(Ellipse):
    """
    Circle class that inherits from Cshape.
    Represents a circle with a center and radius.
    """

    def __init__(self, center: tuple[float, float], radius: float, Ntheta: int=100):
        """
        Initialize the Circle with a center and radius.

        :param center: A tuple (x, y) representing the center of the circle.
        :param radius: The radius of the circle.
        """
        super().__init__(center=center, r1=radius, r2=radius, rot=0)
        self.radius = radius


    def get_point_inside(self, n_pts:int=1, delta:float=0)->np.ndarray:
        cr = (self.radius-delta) * np.sqrt(np.random.random(n_pts))
        cphi = 2*np.pi * np.random.random(n_pts)

        X = np.vstack((
            cr * np.cos(cphi),
            cr * np.sin(cphi)
            )).T
        X += self.c
        return X


    def overlap_with(self, cx, cy, r, delta):
        """Does the circle overlap with another of radius r at (cx, cy)?"""

        d = np.hypot(cx-self.cx, cy-self.cy)
        return d < r + self.r + delta


