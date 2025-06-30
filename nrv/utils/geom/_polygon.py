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

    def __init__(self, vertices: tuple[float, float]=(0,0)):
        """
        Initialize the Ellipse with a center and axes.

        :param center: A tuple (x, y) representing the center of the ellipse.
        :param semi_major_axis: The length of the semi-major axis.
        :param r2: The length of the semi-minor axis.
        """
        self.vertices:np.ndarray[float] = np.array(vertices)
        if self.vertices.shape[0]==2:
            pass_info("vertices of Polygon must be of dim (n_gon, 2) not (2, n_gon)")
            self.vertices = self.vertices.swapaxes(0,1)
            
        super().__init__(center=np.mean(self.vertices, axis=0))

    @property
    def n_gon(self)->int:
        return self.vertices.shape[0]

    @property
    def shp_poly(self)->shp.Polygon:
        return shp.Polygon(self.vertices)

    @property
    def center_c(self)->complex:
        return complex(self.center)

    @property
    def c(self)->np.ndarray:
        return np.array(self.center, dtype=float)

    @property
    def area(self)->float:
        # Shoelace formula
        _i = np.linspace(self.n_gon)
        return np.abs(np.sum(
            self.vertices[_i, 0]*self.vertices[_i-1, 1]
            - self.vertices[-1, 0]*self.vertices[_i, 1]
        ))
    
    @property
    def perimeter(self) -> float:
        return np.sum(np.hypot(self.vertices))

    @property
    def bbox_size(self)->tuple[float, float]:
        _bbox = self.bbox
        return (
            _bbox[2] - _bbox[0],
            _bbox[3] - _bbox[1],
        )
    
    @property
    def bbox(self)->np.ndarray:
        return np.array([
            np.min(self.vertices[:,0]), np.min(self.vertices[:,1]), np.max(self.vertices[:,0]), np.max(self.vertices[:,1])
        ])

    # Methods
    def is_inside(self, point: tuple[np.ndarray, np.ndarray], for_all:bool=True) -> bool:
        if not np.iterable(point[0]):
            return self.shp_poly.contains(shp.Point(*point))
        
        if for_all:
            return self.shp_poly.contains(shp.points(np.array(point).T)).all()

        return self.shp_poly.contains(shp.points(np.array(point).T))

    def rotate(self, angle:float, degree:bool=False):
        self.vertices = rotate_2D(point=self.vertices, angle=angle, degree=degree, as_array=True)


    def get_trace(self, n_theta=100) -> tuple[list[float], list[float]]:
        """
        Get the trace of the ellipse.

        :return: A tuple containing two lists: x-coordinates and y-coordinates of the ellipse.
        """
        p = np.linspace(0,self.n_gon, n_theta, endpoint=True)
        i_p = p.astype(int) % self.n_gon
        t_p = (p % 1).reshape(n_theta, 1)
        tr = (self.vertices[i_p-1] - self.vertices[i_p])*(1-t_p) + self.vertices[i_p]
        return tr[:, 0], tr[:, 1]
    
    def get_point_inside(self, n_pts:int=1, delta:float=0, max_iter=1e5)->np.ndarray:
        points = np.zeros((2,n_pts))
        _poly = self.shp_poly
        minx, miny, maxx, maxy = _poly.bounds
        i, _iter = 0, 0
        if delta == 0:
            gen_point = lambda X: shp.Point(*X)
        else:
            gen_point = lambda X: shp.Point(*X).buffer(delta)
        while i < n_pts:
            # pnt = np.random.uniform(minx, maxx, 2)
            pnt = (np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
            _iter +=1
            if _poly.contains(gen_point(pnt)):
                points[:,i] = pnt
                i += 1
            if _iter > max_iter:
                rise_warning(f"Max Iteration reach: only {i} points placed")
        return points
        