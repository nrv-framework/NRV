"""
NRV-:class:`.axon_population` handling.
"""


from typing import Type, Iterable, Literal
import numpy as np
from pandas import DataFrame
from matplotlib import pyplot as plt, patches as ptc


from .utils._axon_pop_generator import (
    create_axon_population, 
    load_axon_population,
)

from .utils._packers import (
    Placer, 
    axon_packer,
    get_circular_contour,
    expand_pop,
    remove_collision,
    remove_outlier_axons,
    get_ppop_info,
)

from ..backend._log_interface import pass_info, rise_warning
from ..utils.geom._ellipse import Ellipse
from ..utils.geom._circle import Circle
from ..utils.geom._cshape import CShape
from ..utils.geom._bshape import BShape


class axon_population(BShape):
    """
    Instance of an axon population.

    """
    def __init__(self):
        super().__init__()


    @property
    def axon_pop(self):
        return self._pop


    @property
    def n_ax(self):
        if not self.has_pop:
            return 0
        return len(self._pop)

    # ---------------- #
    # Geometry methods #
    # ---------------- #
    def set_geometry(self, geometry:None|Type[CShape]=None, center:tuple[float, float]=None, r1:float=0, r2:float=0, rot:float=0, discard_placement:bool=False):
        """
        Set the geometry of the population

        Parameters
        ----------
        geometry : None | Type[CShape]
            _description_
        center : tuple[float, float], optional
            _description_, by default None
        r1 : float, optional
            _description_, by default 0
        r2 : float, optional
            _description_, by default 0
        rot : float, optional
            _description_, by default 0

        Raises
        ------
        ValueError
            _description_
        """
        if geometry is not None:
            self.geom = geometry
        elif center is not None and r1>0:
            self.create_geometry(center=center, r1=r1, r2=r2, rot=rot)
        else:
            raise ValueError("Either the geometry or its property must be use in argument")
        
        # Find points outside the new geometry
        if self.has_placed_pop:
            if discard_placement:
                self.unplace
            else:
                ok_trace = self.geom.is_inside((self._pop["y"], self._pop["z"])) or self.axon_pop["is_placed"]
                n_discarded = np.sum(self.axon_pop["is_placed"]) - np.sum(ok_trace)
                if n_discarded > 0:
                    _str = f"{n_discarded} axon"
                    if n_discarded>1:
                        _str += "s"
                    pass_info(_str+" are not in the new geometry. Please")



    def create_geometry(self, center:tuple[float, float], r1:float, r2:float=0, rot:float=0):
        if r2 in [0, r1]:
            self.geom = Circle(center=center, radius=r1)
        else:
            self.geom = Ellipse(center=center, r1=r1, r2=r2, rot=rot)




    # -------------------- #
    # Population genrators #
    # -------------------- #
    def create_population():
        pass

    def create_population_from_stat(self, n_ax, percent_unmyel=0.7, M_stat="Schellens_1", U_stat="Ochoa_U"):
        axons_diameters, axons_type, _, _ = create_axon_population(
            n_ax, 
            percent_unmyel=percent_unmyel, 
            M_stat=M_stat,
            U_stat=U_stat
        )
        _data = {
            "types":axons_type, 
            "diameters":axons_diameters,
        }
        self._pop = DataFrame(data=_data)


    def create_population_from_data(self, data:Iterable[np.ndarray]|str):
        """
        create the population directely from the values

        Note
        ----
        If column are not precised, the order for the data must be:
            |-------|----------|------------|------------|
            | Axons |  Axons   | y-position | z-position |
            | Type  | Diameter | `optional` | `optional` |
            |-------|----------|------------|------------|


        Parameters
        ----------
        data : Iterable[np.ndarray]
            data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_axons) or (4, n_axons).
        """
        if isinstance(data,str):
            axons_diameters, axons_type, _, _, y_axons, z_axons = load_axon_population(data)
            data = axons_diameters, axons_type
            if np.isnan(y_axons).all() or np.isnan(z_axons).all():
                data += (y_axons, z_axons)

        if np.iterable(data):
            n_col = len(data)
            if n_col==2:
                pass_info("Generating Axon population from data")
                self._pop = DataFrame(data=zip(*data), columns=["types", "diameters"])
            elif n_col==4:
                pass_info("Generating Axon placed population from data")
                self._pop = DataFrame(data=zip(*data), columns=["types", "diameters", "y", "z"])


    # ----------------------- #
    # Place population method #
    # ----------------------- #
    def place_population(self, method:Literal["default", "packing"]="default", overwrite=False, **kwgs):
        if not self.has_pop or not self.has_geom:
            pass_info("Need to contain population and geometry to allow packing")
            return None
        if not overwrite and self.has_placed_pop:
            pass_info("Population already placed, please precise if you want to overwrite")
            return None
        if method=="default":
            self._use_placer(**kwgs)
        else:
            self._use_packer(**kwgs)


    def _use_placer(self, delta:float=.01, delta_trace:float|None=None, delta_in:float|None=None, n_iter:int=500):
        """
        place population using ``placer``

        Parameters
        ----------
        delta : float, optional
            _description_, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        n_iter : int, optional
            _description_, by default 500
        """
        _p = Placer(geom=self.geom, delta=delta, delta_trace=delta_trace, delta_in=delta_in, n_iter=n_iter)
        _, self.axon_pop["y"], self.axon_pop["z"], self.axon_pop["is_placed"] = _p.place_all(self.axon_pop["diameters"].to_numpy()/2)

    def _use_packer(
        self,
        delta: float = 1,
        fit_to_size: bool = False,
        n_iter: int = 20_000,
    ) -> None:
        """
        Fill the fascicle with an axon population

        Parameters
        ----------
        delta               : float
            axon-to-axon and axon to border minimal distance
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        """
        axons_diameter = self.axon_pop["diameters"].to_numpy()
        N = len(axons_diameter)
        if not isinstance(self.geom, Circle):
            pass_info(NotImplemented)
            return self._use_placer(delta=delta, n_iter=n_iter)
        
        y_axons, z_axons = axon_packer(axons_diameter, delta=delta, n_iter=n_iter)
        if fit_to_size:
            if self.geom.radius is not None:
                d_pop = get_circular_contour(axons_diameter, y_axons, z_axons, delta)
                if d_pop < 2*self.geom.radius:
                    exp_factor = 0.99 * (2*self.geom.radius / d_pop)
                    y_axons, z_axons = expand_pop(y_axons, z_axons, exp_factor)
            else:
                rise_warning(
                    "Can't fit population to size, fascicle diameter is not defined."
                )
        self._pop["y"], self._pop["z"] = y_axons+self.geom.y, z_axons+self.geom.z

        _ok_in = remove_collision(
            axons_diameter, y_axons, z_axons, return_mask=True
        )

        _ok_trace = self.geom.is_inside((self._pop["y"], self._pop["z"]))

        self._pop["is_placed"] = _ok_in & _ok_trace


    def plot(self, ax, contour_color="k", myel_color="b", unmyel_color="r",**kwgs):
        if self.has_geom:
            kwgs["color"] = contour_color
            ax.plot(*self.geom.get_trace(), **kwgs)
        if self.has_placed_pop:
            for i in range(self.n_ax):
                if self.axon_pop["is_placed"][i]:
                    c = ptc.Circle((self.axon_pop["y"][i], self.axon_pop["z"][i]), self.axon_pop["diameters"][i]/2)
                    if self.axon_pop["types"][i]:
                        c.set_color(myel_color)
                    else:
                        c.set_color(unmyel_color)
                    ax.add_artist(c)
        return super().plot(ax, **kwgs)

    def get_ppop_info(self, verbose=False):
        y, z, r = self.axon_pop["y"].to_numpy(), self.axon_pop["z"].to_numpy(), (self.axon_pop["diameters"]/2).to_numpy()
        get_ppop_info(y, z, r, verbose=verbose)

