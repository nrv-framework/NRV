import numpy as np
from copy import deepcopy

from ._cshape import CShape
from .._units import to_nrv_unit


class Ellipse(CShape):
    """
    Ellipse class that inherits from Cshape.
    Represents an ellipse with a center, semi-major axis, and semi-minor axis.
    """

    def __init__(self, center: tuple[float, float], radius:tuple[float, float], rot:float=None, degree:bool=False):
        """
        Initialize the Ellipse with a center and axes.

        :param center: A tuple (x, y) representing the center of the ellipse.
        :param semi_major_axis: The length of the semi-major axis.
        :param r2: The length of the semi-minor axis.
        """
        super().__init__(center, radius)
        assert np.iterable(radius), "Ellipse radius must be iterable (of lenght at least equal to 2)"
        self.rot = 0
        self.r1 = self.radius[0]
        self.r2 = self.radius[1]

        if rot is not None:
            self.rotate(rot, degree)


    @property
    def c(self)->np.ndarray:
        return np.array(self.center, dtype=float)

    def r(self)->np.ndarray:
        return np.array(self.radius, dtype=float)

    @property
    def x(self)->float:
        return 0
    
    @property
    def y(self)->float:
        return self.center[0]

    @property
    def z(self)->float:
        return self.center[1]
    
    @property
    def area(self)->float:
        return np.pi * self.r1 * self.r2

    @property
    def rot_mat(self)->np.ndarray:
        """
        rotation matrix

        Returns
        -------
        np.ndarray
        """
        return np.array(
            [[np.cos(self.rot), -np.sin(self.rot)],
            [np.sin(self.rot), np.cos(self.rot)]]
            )

    @property
    def rot_mat_inverse(self)->np.ndarray:
        """
        Inverse rotation matrix

        Returns
        -------
        np.ndarray
        """
        return np.array([
            [np.cos(-self.rot), -np.sin(-self.rot)],
            [np.sin(-self.rot), np.cos(-self.rot)],
            ])

    @property
    def is_rot(self)->bool:
        return bool(self.rot)

    def is_inside(self, point: tuple[np.ndarray, np.ndarray], delta:float=0) -> bool:
        if isinstance(point, np.ndarray):
            X = deepcopy(point)
        else:
            X = np.array(point).astype(float).T
        # Translate back to the ellipse's coordinate system
        X -= self.c
        # Rotate back to the ellipse's coordinate system
        if self.is_rot:
            X @= self.rot_mat_inverse

        # Normalize the coordinate
        X /= np.array((self.r1+delta, self.r2+delta))
        X_norm = np.sum(X**2, axis=-1)

        # Check if the normalized point is inside the unit circle
        return (X_norm <= 1).all()
    
    def rotate(self, angle:float, degree:bool=False):
        if degree:
            angle = to_nrv_unit(angle, "deg")
        self.rot += angle


    def get_trace(self, n_theta=100) -> tuple[list[float], list[float]]:
        """
        Get the trace of the ellipse.

        :return: A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        _theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=True)

        y_trace = self.r1 * np.cos(_theta)
        z_trace = self.r2 * np.sin(_theta)

        X = np.vstack((
            y_trace,
            z_trace,
        )).T
        # Apply rotation if needed
        if self.is_rot:
            X = X @ self.rot_mat
        # Apply translation
        X += self.c
        return X[:,0], X[:,1]
    
    def get_point_inside(self, n_pts:int=1, delta:float=0)->np.ndarray:

        _theta = np.random.random(n_pts) * 2 * np.pi
        _rf = np.sqrt(np.random.random(n_pts))

        #Get a random point inside an unit circle
        X = np.vstack((
            _rf * np.cos(_theta),
            _rf * np.sin(_theta),
        )).T

        # Scale to ellipse dimension
        X *= np.array((self.r1-delta, self.r2-delta))

        # Rotate and translate
        if self.is_rot:
            X = X @ self.rot_mat
        X += self.c
        return X



