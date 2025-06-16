import numpy as np

from ._cshape import CShape


class Ellipse(CShape):
    """
    Ellipse class that inherits from Cshape.
    Represents an ellipse with a center, semi-major axis, and semi-minor axis.
    """

    def __init__(self, center: tuple[float, float], r1: float, r2: float, rot: float = 0, Ntheta: int = 100):
        """
        Initialize the Ellipse with a center and axes.

        :param center: A tuple (x, y) representing the center of the ellipse.
        :param semi_major_axis: The length of the semi-major axis.
        :param r2: The length of the semi-minor axis.
        """
        super().__init__(Ntheta)
        if r1 <= 0 or r2 <= 0:
            raise ValueError("Semi-major and semi-minor axes must be positive numbers.")

        self.center = center[:2]
        self.r1 = r1
        self.r2 = r2
        self.rot = rot

    @property
    def c(self):
        return np.array(self.center, dtype=float)


    @property
    def x(self):
        return 0
    
    @property
    def y(self):
        return self.center[0]

    @property
    def z(self):
        return self.center[1]

    @property
    def Rmatrix(self)->np.ndarray:
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
    def Rmatrix_inverse(self)->np.ndarray:
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
        X = np.array(point).astype(float).T
        # Translate back to the ellipse's coordinate system
        X -= self.c
        # Rotate back to the ellipse's coordinate system
        if self.is_rot:
            X @= self.Rmatrix_inverse

        # Normalize the coordinate
        X /= np.array((self.r1+delta, self.r2+delta))
        X_norm = np.sum(X**2, axis=-1)

        # Check if the normalized point is inside the unit circle
        return (X_norm <= 1).all()

    def get_trace(self) -> tuple[list[float], list[float]]:
        """
        Get the trace of the ellipse.

        :return: A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        y_trace = self.r1 * np.cos(self.theta)
        z_trace = self.r2 * np.sin(self.theta)

        X = np.vstack((
            y_trace,
            z_trace,
        )).T
        # Apply rotation if needed
        if self.is_rot:
            X = X @ self.Rmatrix
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
            X = X @ self.Rmatrix
        X += self.c
        return X



