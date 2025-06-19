from typing import List, Tuple
import numpy as np

from ...backend._NRV_Class import NRV_class, abstractmethod

class CShape(NRV_class):
    """
    Abstract base class for closed-shaped geometries.
    """
    @abstractmethod
    def __init__(self, center:tuple[float, float], radius:float|tuple[float,float]):
        """
        Initializes the CShape with a specified number of points for angular resolution.

        :param Ntheta: Number of points to use for angular resolution.
        """
        super().__init__()
        self.center = center[:2]
        self.radius = radius

    
    @property
    def area(self)->float:
        """
        Area of the shape in \\(\\mu m^2\\)

        Returns
        -------
        float
        """
        pass

    def rotate(self, angle:float, degree:bool=False):
        """
        Rotate the shape

        Parameters
        ----------
        angle : float
            Rotation angle
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        pass

    def translate(self, y:float=0, z:float=0):
        """
        Translate the shape

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.center = self.center[0] + y, self.center[1] + z


    @abstractmethod
    def is_inside(self, point: tuple[np.ndarray|float, np.ndarray|float], delta:float=0) -> bool:
        """
        Checks if a given point is inside the C-shape.

        Parameters
        ----------
        point : tuple[np.ndarray|float, np.ndarray|float]
            A tuple representing the coordinates of the point (x, y).
        delat : float
            addtional space bewteen the point and the trace

        Returns
        -------
        bool
            True if the point is inside the C-shape, False otherwise.
        """
        pass


    def get_point_inside(self, n_pts:int=1, delta:float=0)->np.ndarray:
        """
        return n points coordinate randomly picked inside the shape

        Parameters
        ----------
        n_pts : int, optional
            number of points to generate, by default 0
        delta : float, optional
            distance with the shape perimeter, by default 0

        Returns
        -------
        np.ndarray
        """
        pass

    def get_trace(self, n_theta:int=100) -> tuple[list[float], list[float]]:
        """
        Get the trace of the shape.

        Parameters
        ----------
        n_theta : int, optional
            number of coordinate point returned, by default 100

        Returns
        -------
        tuple[list[float], list[float]]
            A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        pass