from typing import List, Tuple
import numpy as np

from ...backend._NRV_Class import NRV_class, abstractmethod

class CShape(NRV_class):
    """
    Abstract base class for closed-shaped geometries.
    """
    @abstractmethod
    def __init__(self, Ntheta:int=100):
        """
        Initializes the CShape with a specified number of points for angular resolution.

        :param Ntheta: Number of points to use for angular resolution.
        """
        super().__init__()
        self.Ntheta = Ntheta


    @property
    def theta(self):
        return np.linspace(0, 2 * np.pi, self.Ntheta, endpoint=True)


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

    def get_trace(self) -> tuple[list[float], list[float]]:
        """
        Get the trace of the ellipse.

        :return: A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        pass