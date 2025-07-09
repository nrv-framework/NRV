from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt

from ...backend._NRV_Class import NRV_class, abstractmethod


class CShape(NRV_class):
    """
    Abstract base class for closed-shaped geometries.
    """

    @abstractmethod
    def __init__(
        self,
        center: tuple[float, float] = (0, 0),
        radius: float | tuple[float, float] = 0,
        rot: float = None,
        degree: bool = False,
    ):
        """
        Initializes the CShape

        Parameters
        ----------
        center : tuple[float, float], optional
            Center of the shape, by default (0,0)
        radius : float | tuple[float,float], optional
            Radius of the shape, for none elliptic shape set as an average distance between trace points and center, by default 0
        rot : float, optional
            rotation of the shape, by default None
        degree : bool, optional
            if True `rot` is in degree, if False in radian, by default False
        """
        super().__init__()
        self.center = center
        self.radius = radius
        self.rot = 0

        if rot is not None:
            self.rotate(rot, degree)

    # ---------- #
    # Properties #
    # ---------- #

    @property
    def x(self) -> float:
        return 0

    @property
    def y(self) -> float:
        return self.center[0]

    @property
    def z(self) -> float:
        return self.center[1]

    @property
    def area(self) -> float:
        """
        Area of the shape in $\\mu m^2$

        Returns
        -------
        float
        """
        pass

    @property
    def perimeter(self) -> float:
        """
        Perimeter of the shape in $\\mu m^2$

        Returns
        -------
        float
        """
        pass

    @property
    def bbox_size(self) -> tuple[float, float]:
        """
        Size of the bounding bounding box of the shape. (usefull for meshing)

        Returns
        -------
        tuple[float, float]
        """
        pass

    @property
    def bbox(self) -> tuple[float, float]:
        """
        Coordinate of the bounding box as a :class:`numpy.ndarray`in the following format :math:`y_{min}, z_{min}, y_{max}, z_{max}`.

        Returns
        -------
        tuple[float, float]
        """
        pass

    def rotate(self, angle: float, degree: bool = False):
        """
        Rotate the shape.

        Parameters
        ----------
        angle : float
            Rotation angle
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        pass

    def translate(self, y: float = 0, z: float = 0):
        """
        Translate the shape.

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        """
        self.center = self.center[0] + y, self.center[1] + z

    @abstractmethod
    def is_inside(
        self,
        point: tuple[np.ndarray | float, np.ndarray | float],
        delta: float = 0,
        for_all: bool = True,
    ) -> bool | np.ndarray[bool]:
        """
        Checks if a given point is inside the C-shape.

        Parameters
        ----------
        point : tuple[np.ndarray|float, np.ndarray|float]
            A tuple representing the coordinates of the point (x, y).
        delat : float
            addtional space bewteen the point and the trace
        for_all : bool
            If False return a array of bool for each point else return only one bool using ``all``, by default True
        Returns
        -------
        bool | np.ndarray[bool]
            True if the point is inside the C-shape, False otherwise.
        """
        pass

    def get_point_inside(self, n_pts: int = 1, delta: float = 0) -> np.ndarray:
        """
        Returns n points coordinate randomly picked inside the shape

        Parameters
        ----------
        n_pts : int, optional
            number of points to generate, by default 0
        delta : float, optional
            distance with the shape perimeter, by default 0

        Returns
        -------
        np.ndarray
            array, of dimension (n_pts, 2), containing the coordinate of y, z-coorinates of the generated point
        """
        pass

    def get_trace(
        self, n_theta: int = 100
    ) -> tuple[np.ndarray[float], np.ndarray[float]]:
        """
        Returns the trace of the geometry as a list of points.

        Parameters
        ----------
        n_theta : int, optional
            number of coordinate point returned, by default 100

        Returns
        -------
        tuple[np.ndarray[float], np.ndarray[float]]
            A tuple containing two lists: y-coordinates and z-coordinates of points in the shape boundaries.
        """
        pass

    # ------------ #
    # Plot methods #
    # ------------ #

    def plot(
        self,
        axes: plt.Axes,
        n_tetha: int = 100,
        add_center: bool = False,
        *args,
        **kwgs
    ):
        """
        plot the border of the shape

        Parameters
        ----------
        axes : plt.Axes
            Matplolib axes where to plot
        n_tetha : int, optional
            number of resultion points used for the plot, by default 100
        """
        axes.plot(*self.get_trace(n_theta=n_tetha), *args, **kwgs)

    def plot_bbox(self, axes: plt.Axes, *args, **kwgs):
        """
                plot the border of the shape

        Parameters
        ----------
        axes : plt.Axes
            Matplolib axes where to plot
        """
        axes.plot(
            self.bbox[np.array([0, 0, 2, 2, 0])],
            self.bbox[np.array([1, 3, 3, 1, 1])],
            *args,
            **kwgs
        )
