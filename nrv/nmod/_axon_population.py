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
    save_axon_population,
    get_stat_expected,
)

from .utils._packers import (
    Placer,
    axon_packer,
    get_circular_contour,
    expand_pop,
    remove_collision,
    get_ppop_info,
)

from ..backend._inouts import check_function_kwargs
from ..backend._log_interface import pass_info, rise_warning, rise_error
from ..utils.geom import (
    create_cshape,
    Ellipse,  # typing
    Circle,  # typing
)
from ..utils.geom._cshape import CShape  # typing
from ..utils.geom._popshape import PopShape
from ..utils._misc import get_MRG_parameters


class axon_population(PopShape):
    """
    Instance of an axon population.

    """

    def __init__(self, **kwgs):
        super().__init__()

        gen_kwg = check_function_kwargs(self.generate, kwgs)

        if len(gen_kwg):
            self.generate(**gen_kwg)

    @property
    def axon_pop(self):
        return self._pop

    @property
    def n_ax(self):
        if not self.has_pop:
            return 0
        return len(self._pop)

    # --------------- #
    # Overall methods #
    # --------------- #
    def generate(
        self,
        geometry: None | Type[CShape] = None,
        center: tuple[float, float] = None,
        radius: None | float | tuple[float, float] = None,
        rot: float = 0,
        diameter: None | float | tuple[float, float] = None,
        discard_placement: bool = False,
        data: tuple[np.ndarray] | np.ndarray | str = None,
        n_ax: int = None,
        FVF: None | float = None,
        percent_unmyel: float = 0.7,
        M_stat: str = "Schellens_1",
        U_stat: str = "Ochoa_U",
        pos: None | tuple[np.ndarray] | np.ndarray | str = None,
        method: Literal["default", "packing"] = "default",
        delta: float = 0.01,
        delta_trace: float | None = None,
        delta_in: float | None = None,
        n_iter: int = None,
        fit_to_size: bool = False,
        with_node_shift: bool = True,
        overwrite=False,
    ):
        """
        Generate the complete geometry and/or axon population and placement.

        Parameters
        ----------
        geometry : None | Type[CShape]
            if not None, geometry used for the population
        center : tuple[float, float], optional
            _description_, by default None
        r1 : float, optional
            _description_, by default 0
        r2 : float, optional
            _description_, by default 0
        rot : float, optional
            _description_, by default 0
        data : tuple[np.ndarray] | np.ndarray | str
            data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax) or (4, n_ax), arange in the following order: `types`, `diameters`, `y` (optional), `z` (optional).
        n_ax               : int, optional
            Number of axon to generate for the population (Unmyelinated and myelinated), default 100
        FVF             : float
            Fiber Volume Fraction estimated for the area. If None, the value n_ax is used. By default set to None
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition
        method : Literal[&quot;default&quot;, &quot;packing&quot;], optional
            method to use for the , by default "default"
        overwrite : bool, optional
            If True placement is skipped if the population is already paced, by default False
        delta               : float
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        with_node_shift            : bool
            if True also compute the Node of Ranviers shifts
        fname      : str
            optional, if specified, name file to store the population generated

        Note
        ----
        When `FVF` is set, an approximated value of `n_ax` is calculated from:

        .. math::

            FVF = \\frac{n_{axons}*E_{d}}{A_{tot}}

        where $E_{d}$ is the espected diameters from the myelinated and unmyelinated fibers stats and $A_{tot}$ is geometry total area.

        Tip
        ---
        It goes for the previous definition that `FVF` will only be accurate for large axon population. This might be improved in future version but for now it is adviced to define small population using `n_ax` instead of `FVF`
        """
        self.set_geometry(
            geometry=geometry,
            center=center,
            radius=radius,
            rot=rot,
            diameter=diameter,
            discard_placement=discard_placement,
        )

        if n_ax is not None or FVF is not None:
            self.fill_geometry(
                data=data,
                n_ax=n_ax,
                FVF=FVF,
                percent_unmyel=percent_unmyel,
                M_stat=M_stat,
                U_stat=U_stat,
                pos=pos,
                method=method,
                delta=delta,
                delta_trace=delta_trace,
                delta_in=delta_in,
                n_iter=n_iter,
                fit_to_size=fit_to_size,
                with_node_shift=with_node_shift,
                overwrite=overwrite,
            )

    def fill_geometry(
        self,
        data: tuple[np.ndarray] | np.ndarray | str = None,
        n_ax: int = 100,
        FVF: None | float = None,
        percent_unmyel: float = 0.7,
        M_stat: str = "Schellens_1",
        U_stat: str = "Ochoa_U",
        pos: None | tuple[np.ndarray] | np.ndarray | str = None,
        method: Literal["default", "packing"] = "default",
        delta: float = 0.01,
        delta_trace: float | None = None,
        delta_in: float | None = None,
        n_iter: int = None,
        fit_to_size: bool = False,
        with_node_shift: bool = True,
        overwrite: bool = False,
        fname: str = None,
    ):
        """
        Fill a geometricaly defined contour with axons

        Parameters
        ----------
        data : tuple[np.ndarray] | np.ndarray | str
            data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax) or (4, n_ax), arange in the following order: `types`, `diameters`, `y` (optional), `z` (optional).
        n_ax               : int, optional
            Number of axon to generate for the population (Unmyelinated and myelinated), default 100
        FVF             : float
            Fiber Volume Fraction estimated for the area. If None, the value n_ax is used. By default set to None
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition
        method : Literal[&quot;default&quot;, &quot;packing&quot;], optional
            method to use for the , by default "default"
        overwrite : bool, optional
            If True placement is skipped if the population is already paced, by default False
        delta               : float
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        with_node_shift            : bool
            if True also compute the Node of Ranviers shifts
        fname      : str
            optional, if specified, name file to store the population generated

        Note
        ----
        When `FVF` is set, an approximated value of `n_ax` is calculated from:

        .. math::

            FVF = \\frac{n_{axons}*E_{d}}{A_{tot}}

        where $E_{d}$ is the espected diameters from the myelinated and unmyelinated fibers stats and $A_{tot}$ is geometry total area.

        Tip
        ---
        It goes for the previous definition that `FVF` will only be accurate for large axon population. This might be improved in future version but for now it is adviced to define small population using `n_ax` instead of `FVF`
        """
        if not self.has_geom:
            rise_warning(
                "set the geometry before filling the fascicle, nothing was set"
            )
        else:
            self.create_population(
                data=data,
                percent_unmyel=percent_unmyel,
                n_ax=n_ax,
                FVF=FVF,
                M_stat=M_stat,
                U_stat=U_stat,
                overwrite=overwrite,
            )

            # Need for the case of data.shape is (4,n)
            # to avoid calling place twice
            if not self.has_placed_pop or overwrite:
                self.place_population(
                    pos=pos,
                    method=method,
                    delta=delta,
                    delta_trace=delta_trace,
                    delta_in=delta_in,
                    n_iter=n_iter,
                    fit_to_size=fit_to_size,
                    with_node_shift=with_node_shift,
                    overwrite=overwrite,
                )
            if fname is not None:
                save_axon_population(fname, *self._pop.to_numpy())

    def generate_from_deprected_fascicle(self, key_dic: dict):
        """
        Generate the population from the data saved in a deprecated fascicle file.

        Warning
        -------
            This function is mostly for internal use for retrocompatibility. If deprecated save file are found, it is adviced to uptated them using :func:`update_fascicle_file`.

        Parameters
        ----------
        key_dic : dict
            Dictionary containing the loaded fascicle
        """
        if len({"y_grav_center", "z_grav_center", "D"} - key_dic.keys()) == 0:
            self.set_geometry(
                center=(key_dic["y_grav_center"], key_dic["z_grav_center"]),
                diameter=key_dic["D"],
            )
        if (
            len(
                {
                    "axons_type",
                    "axons_diameter",
                    "axons_y",
                    "axons_z",
                    "NoR_relative_position",
                }
                - key_dic.keys()
            )
            == 0
        ):
            if len(key_dic["axons_diameter"]) > 0:
                self.create_population(
                    data=(key_dic["axons_type"], key_dic["axons_diameter"])
                )
            if len(key_dic["axons_y"]) > 0:
                self.place_population(pos=(key_dic["axons_y"], key_dic["axons_z"]))
            if len(key_dic["NoR_relative_position"]) == len(self):
                self.generate_NoR_position_from_data(key_dic["NoR_relative_position"])
            elif self.has_pop:
                rise_warning(
                    "Number of NoR positions in the file does not match with the population, regenerating"
                )
                self.generate_random_NoR_position()

    # ---------------- #
    # Geometry methods #
    # ---------------- #
    def set_geometry(
        self,
        geometry: None | Type[CShape] = None,
        center: tuple[float, float] = None,
        radius: None | float | tuple[float, float] = None,
        rot: float = 0,
        degree: bool = False,
        diameter: None | float | tuple[float, float] = None,
        discard_placement: bool = False,
    ):
        """
        Set the geometry of the population

        Parameters
        ----------
        center : tuple[float, float], optional
            Center of the shape, by default (0, 0)
        radius : float | tuple[float, float], optional
            Radius of the shape, by default 10
        rot : None | float, optional
            Rotation of the shape, by default None
        diameter : None | float | tuple[float, float], optional
            Diameter of the shape. If None, radius value is used to define the shape, by default None
        discard_placement : bool
            If true and a unplace an potential population already placed. Else, only discard the axon not fiting in the geometry, by default False
        """
        if geometry is not None:
            self.geom = geometry
        else:
            if self.has_geom:
                center = center or self.geom.center
                radius = radius or self.geom.radius
                if isinstance(self.geom, Ellipse):
                    rot = rot or self.geom.rot
            if center is not None and radius is not None or diameter is not None:
                self.geom = create_cshape(
                    center=center,
                    radius=radius,
                    rot=rot,
                    degree=degree,
                    diameter=diameter,
                )
            else:
                raise ValueError(
                    "Either the geometry or its property must be use in argument"
                )

        # Find points outside the new geometry
        if self.has_placed_pop:
            if discard_placement:
                self.clear_population_placement()
            else:
                self.check_placement

    def reshape_geometry(
        self,
        geometry: None | Type[CShape] = None,
        center: tuple[float, float] = None,
        radius: float | tuple[float, float] = None,
        rot: float = None,
        discard_placement: bool = False,
    ):
        if geometry is None and self.has_geom:
            # Reload previous geometry properties if unchange
            # ! Not ideal method see how to generalize
            if center is None:
                center = self.geom.center
            if radius:
                radius = self.geom.radius
            rot = self.geom.rot
        self.set_geometry(
            geometry=geometry,
            center=center,
            radius=radius,
            rot=rot,
            discard_placement=discard_placement,
        )

    # -------------------- #
    # Population genrators #
    # -------------------- #
    def create_population(
        self,
        data: tuple[np.ndarray] | np.ndarray | str = None,
        n_ax: int = 100,
        FVF: None | float = None,
        percent_unmyel: float = 0.7,
        M_stat: str = "Schellens_1",
        U_stat: str = "Ochoa_U",
        overwrite=False,
    ):
        """
        Creat an placed axon population

        Parameters
        ----------
        data : tuple[np.ndarray] | np.ndarray | str
            data to used to create the population. Supported data:

                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax) or (4, n_ax), arange in the following order: `types`, `diameters`, `y` (optional), `z` (optional).
        n_ax               : int, optional
            Number of axon to generate for the population (Unmyelinated and myelinated), default 100
        FVF             : float
            Fiber Volume Fraction estimated for the area. If None, the value n_ax is used. By default set to None
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition

        Note
        ----
        When `FVF` is set, an approximated value of `n_ax` is calculated from:

        .. math::

            FVF = \\frac{n_{axons}*E_{d}}{A_{tot}}

        where $E_{d}$ is the espected diameters from the myelinated and unmyelinated fibers stats and $A_{tot}$ is geometry total area.

        Tip
        ---
        It goes for the previous definition that `FVF` will only be accurate for large axon population. This might be improved in future version but for now it is adviced to define small population using `n_ax` instead of `FVF`
        """
        if not self.has_pop or overwrite:
            if data is not None:
                self.create_population_from_data(data=data)
            else:
                self.create_population_from_stat(
                    n_ax=n_ax,
                    FVF=FVF,
                    percent_unmyel=percent_unmyel,
                    M_stat=M_stat,
                    U_stat=U_stat,
                )

    def create_population_from_stat(
        self,
        n_ax: int,
        FVF: None | float = None,
        percent_unmyel: float = 0.7,
        M_stat: str = "Schellens_1",
        U_stat: str = "Ochoa_U",
    ):
        """
        Create a virtual population of axons (no Neuron implementation, axon class not called) of a controled number, with controlled statistics.

        Parameters
        ----------
        n_ax               : int
            Number of axon to generate for the population (Unmyelinated and myelinated).
        FVF             : float
            Fiber Volume Fraction estimated for the area. If None, the value n_ax is used. By default set to None.
        percent_unmyel  : float
            ratio of unmyelinated axons in the population. Should be between 0 and 1.
        M_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition.
        U_stat          : str
            name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition.

        Note
        ----
        When `FVF` is set, an approximated value of `n_ax` is calculated from:

        .. math::

            FVF = \\frac{n_{axons}*E_{d}}{A_{tot}}

        where $E_{d}$ is the espected diameters from the myelinated and unmyelinated fibers stats and $A_{tot}$ is geometry total area.

        Tip
        ---
        It goes for the previous definition that `FVF` will only be accurate for large axon population. This might be improved in future version but for now it is adviced to define small population using `n_ax` instead of `FVF`
        """
        if FVF is not None:
            e_d = percent_unmyel * get_stat_expected(U_stat) + (
                1 - percent_unmyel
            ) * get_stat_expected(M_stat)
            e_A = np.pi * (0.5 * e_d) ** 2
            n_ax = round(FVF * self.geom.area / (2 * e_A))
            #!BUG in stats `2*` not supposed to be their
            pass_info(f"A {n_ax} axons population will be generated")

        axons_diameters, axons_type, _, _ = create_axon_population(
            n_ax, percent_unmyel=percent_unmyel, M_stat=M_stat, U_stat=U_stat
        )
        _data = {
            "types": axons_type,
            "diameters": axons_diameters,
        }
        self._pop = DataFrame(data=_data)

    def create_population_from_data(self, data: tuple[np.ndarray] | np.ndarray | str):
        """
        create the population directely from the values

        Note
        ----
        If column are not precised, the order for the data must be:
            +-------+-----------+------------+------------+------------+
            | Types | Diameters | y-position | z-position | node shift |
            +       +           +            +            +            +
            |       |           | `optional` | `optional` | `optional` |
            +-------+-----------+------------+------------+------------+

        For `str` indexed objects (:class:`dict` or :class:`pandas.DataFrame`) the respective indexes of the column above must be: `"types"`, `"diameters"`, `"y"` (optional), `"z"` (optional), `"node_shift"` (optional).


        Parameters
        ----------
        data : tuple[np.ndarray] | np.ndarray | str
            data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax) or (4, n_ax), arange in the following order: `types`, `diameters`, `y` (optional), `z` (optional), `node_shift` (optional).
        """
        if isinstance(data, str):
            axons_diameters, axons_type, _, _, y_axons, z_axons = load_axon_population(
                data
            )
            data = axons_diameters, axons_type
            if np.isnan(y_axons).all() or np.isnan(z_axons).all():
                data += (y_axons, z_axons)
        if isinstance(data, dict) or isinstance(data, DataFrame):
            _keys = ["types", "diameters", "y", "z", "node_shift"]
            if isinstance(data, dict):
                _dkeys = data.keys()
            else:
                _dkeys = set(data.columns)
            if len(set(_keys) - _dkeys) > 0:
                _keys = _keys[:4]
            if len(set(_keys) - _dkeys) > 0:
                _keys = _keys[:2]
            if len(set(_keys) - _dkeys) > 0:
                rise_warning(
                    f"Wrong data format to create_population.",
                    f"If data is dict or DataFrames it must at least contains the keys: {_keys}",
                )
            else:
                data = [data[k] for k in _keys]
        if np.iterable(data):
            n_col = len(data)
            self._pop = DataFrame(data=zip(*data[:2]), columns=["types", "diameters"])
            if n_col == 4:
                self._pop = DataFrame(
                    data=zip(*data), columns=["types", "diameters", "y", "z"]
                )
                self.check_placement
                pass_info("Axon placed population generated from data")
            elif n_col == 5:
                self._pop = DataFrame(
                    data=zip(*data),
                    columns=["types", "diameters", "y", "z", "node_shift"],
                )
                self.check_placement
                pass_info("Axon placed population generated from data")
            else:
                pass_info("Axon population generated from data")

    # ----------------------- #
    # Place population method #
    # ----------------------- #
    def place_population(
        self,
        pos: None | tuple[np.ndarray] | np.ndarray | str = None,
        method: Literal["default", "packing"] = "default",
        overwrite=False,
        delta: float = 0.01,
        delta_trace: float | None = None,
        delta_in: float | None = None,
        n_iter: int = None,
        fit_to_size: bool = False,
        with_node_shift: bool = True,
    ):
        """
        Place the population.

        Parameters
        ----------
        pos : None | tuple[np.ndarray] | np.ndarray
            if not None data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax)
        method : Literal[&quot;default&quot;, &quot;packing&quot;], optional
            method to use for the , by default "default"
        overwrite : bool, optional
            If True placement is skipped if the population is already paced, by default False
        delta               : float
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            _description_, by default None
        delta_in : float | None, optional
            _description_, by default None
        fit_to_size         : bool
            if true, the axon population is extended to fit within fascicle size, if not the population is kept as is
        n_iter              : int
            number of interation for the packing algorithm if the y-x axon coordinates are not specified
        with_node_shift            : bool
            if True also compute the Node of Ranviers shifts
        """
        if not self.has_pop or not self.has_geom:
            pass_info("Need to contain population and geometry to allow packing")
            return None
        if not overwrite and self.has_placed_pop:
            pass_info(
                "Population already placed, please precise if you want to overwrite"
            )
            return None
        if pos is not None:
            self.place_population_from_data(pos=pos)

        if method == "packing":
            if n_iter is None:
                n_iter = 20_000
            self._use_packer(delta=delta, n_iter=n_iter, fit_to_size=fit_to_size)
        else:
            if n_iter is None:
                n_iter = 500
            self._use_placer(
                delta=delta, delta_trace=delta_trace, delta_in=delta_in, n_iter=n_iter
            )
        if with_node_shift:
            self.generate_random_NoR_position()

    def place_population_from_data(self, pos: tuple[np.ndarray] | np.ndarray | str):
        """_summary_

        Parameters
        ----------
        pos : tuple[np.ndarray] | np.ndarray
            data to used to create the population. Supported data:
                - `str`: of the file path and name where to load the population properties.
                - `tuple[np.ndarray]` containing the population properties.
                - `np.ndarray`: of dimention (2, n_ax)
        """
        if not np.iterable(pos) or not len(pos) > 1:
            raise ValueError("pos must be iterable and of lenght at least equel to 2")

        self._pop["y"], self._pop["z"] = pos[0], pos[1]

    def _use_placer(
        self,
        delta: float = 0.01,
        delta_trace: float | None = None,
        delta_in: float | None = None,
        n_iter: int = 500,
    ):
        """
        Place population using :class:`Placer-class<.utils._packers.Placer>`.

        Parameters
        ----------
        delta : float, optional
            axon-to-axon and axon to border minimal distance, by default .01
        delta_trace : float | None, optional
            axon to border minimal distance, if None set to `delta, by default None
        delta_in : float | None, optional
            axon-to-axon minimal distance, if None set to `delta`, by default None
        n_iter : int, optional
            number of interation for the packing algorithm if the y-x axon coordinates are not specified, by default 500
        """
        _p = Placer(
            geom=self.geom,
            delta=delta,
            delta_trace=delta_trace,
            delta_in=delta_in,
            n_iter=n_iter,
        )
        _, self.axon_pop["y"], self.axon_pop["z"], self.axon_pop["is_placed"] = (
            _p.place_all(self.axon_pop["diameters"].to_numpy() / 2)
        )

    def _use_packer(
        self,
        delta: float = 1,
        fit_to_size: bool = False,
        n_iter: int = 20_000,
    ) -> None:
        """
        Place population using :class:`Placer-class<.utils._packers.Placer>`.

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
                if d_pop < 2 * self.geom.radius:
                    exp_factor = 0.99 * (2 * self.geom.radius / d_pop)
                    y_axons, z_axons = expand_pop(y_axons, z_axons, exp_factor)
            else:
                rise_warning(
                    "Can't fit population to size, fascicle diameter is not defined."
                )
        self._pop["y"], self._pop["z"] = y_axons + self.geom.y, z_axons + self.geom.z

        _ok_in = remove_collision(axons_diameter, y_axons, z_axons, return_mask=True)

        _ok_trace = self.geom.is_inside((self._pop["y"], self._pop["z"]))
        self._pop["is_placed"] = _ok_in & _ok_trace

    def get_ppop_info(self, verbose=False):
        y, z, r = (
            self.axon_pop["y"].to_numpy(),
            self.axon_pop["z"].to_numpy(),
            (self.axon_pop["diameters"] / 2).to_numpy(),
        )
        get_ppop_info(y, z, r, verbose=verbose)

    # ---------------- #
    # NoR displacement #
    # ---------------- #
    @property
    def has_node_shift(self):
        if not self.has_pop:
            return False
        return "node_shift" in self._pop.columns

    def generate_random_NoR_position(self):
        """
        Generates radom Node of Ranvier shifts to prevent from axons with the same diamters to be aligned.
        """
        # also generated for unmyelinated but the meaningless value won't be used
        self._pop["node_shift"] = np.random.uniform(low=0.0, high=1.0, size=self.n_ax)
        self._pop["node_shift"] *= self._pop["types"]

    def generate_ligned_NoR_position(self, x=0):
        """
        Generates Node of Ranvier shifts to aligned a node of each axon to x postition.

        Parameters
        ----------
        x    : float
            x axsis value (um) on which node are lined, by default 0
        """
        # also generated for unmyelinated but the meaningless value won't be used
        node_lengths = get_MRG_parameters(self._pop["diameters"].to_numpy)[5]
        self._pop["node_shift"] = (x - 0.5) % node_lengths / node_lengths

        self._pop["node_shift"] *= self._pop["types"]

    def generate_NoR_position_from_data(self, node_shift: np.ndarray):
        """
        Generates Node of Ranvier shifts to aligned a node of each axon to x postition.

        Parameters
        ----------
        x    : float
            x axsis value (um) on which node are lined, by default 0
        """
        self._pop["node_shift"] = node_shift
        self._pop["node_shift"] *= self._pop["types"]

    # ------- #
    # Plotter #
    # ------- #
    def plot(
        self,
        axes: plt.Axes,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        contour_color: str = "k",
        myel_color: str = "b",
        unmyel_color: str = "r",
        num: bool = False,
        **kwgs,
    ):
        if self.has_geom:
            kwgs["color"] = contour_color
            axes.plot(*self.geom.get_trace(), **kwgs)
        if self.has_placed_pop:
            sub_pop = self.get_sub_population(expr=expr, mask_labels=mask_labels)
            for i_ax in sub_pop.index:
                c = ptc.Circle(
                    (self._pop["y"][i_ax], self.axon_pop["z"][i_ax]),
                    self._pop["diameters"][i_ax] / 2,
                )

                if sub_pop["types"][i_ax]:
                    c.set_color(myel_color)
                else:
                    c.set_color(unmyel_color)
                axes.add_artist(c)
                if num:
                    axes.text(self._pop["y"][i_ax], self._pop["z"][i_ax], str(i_ax))
        axes.set_aspect("equal", adjustable="box")

    def hist(
        self,
        axes: plt.Axes,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        myel_color: str = "b",
        unmyel_color: str = "r",
        **kwgs,
    ):
        """
        Plot an histogram of axon diamters in the population

        Parameters
        ----------
        axes    : matplotlib.Axes
            axes of the figure to display the histogram.
        expr : str | None, optional
            Subpopulation to plot, by default None.
        mask_labels : None | Iterable[str] | str, optional
            Subpopulation to plot, by default [].
        myel_color : str, optional
            Color of myelinated axons bins, by default "b".
        unmyel_color : str, optional
            Color of unmyelinated axons bins, by default "r".
        """
        if self.has_pop:
            sub_pop = self.get_sub_population(expr=expr, mask_labels=mask_labels)
            u_diam = sub_pop.query("types==0")["diameters"]
            kwgs["color"] = unmyel_color
            axes.hist(u_diam, **kwgs)
            m_diam = sub_pop.query("types==1")["diameters"]
            kwgs["color"] = myel_color
            axes.hist(m_diam, **kwgs)
