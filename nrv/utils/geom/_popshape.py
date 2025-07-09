from typing import Iterable, Type
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from typing import Literal

from ._cshape import CShape
from ...backend._NRV_Class import NRV_class, abstractmethod
from ...backend._extlib_interface import df_to
from ...backend._log_interface import pass_info, rise_warning
from .._misc import rotate_2D


class PopShape(NRV_class):
    """
    Abstract base class for bumble-shaped geometries gathering sub-shapes.
    """

    @abstractmethod
    def __init__(self):
        """
        Initializes the CShape with a specified number of points for angular resolution.


        Parameters
        ----------
        """
        super().__init__()
        self.geom: None | Type[CShape] = None
        self._pop: DataFrame = DataFrame(columns=["types", "diameters"])
        self.mask_labels: list[str] = []

    @property
    def has_geom(self) -> bool:
        """
        Shape Status: True if the instance has a geometry

        Returns
        -------
        bool
        """
        return self.geom is not None

    @property
    def has_pop(self) -> bool:
        """
        Population Status: True if the instance has an population

        Returns
        -------
        bool
        """

        return not self._pop.empty

    @property
    def has_placed_pop(self) -> bool:
        """
        Placed Population Status: True if the instance has an population with fixed position for each member

        Returns
        -------
        bool
        """
        if not self.has_pop:
            return False
        keys_to_have = {"y", "z", "is_placed"} - set(self._pop.keys())
        if not len(keys_to_have):
            return self._pop["is_placed"].sum()
        return False

    def __len__(self) -> int:
        if not self.has_pop:
            return 0
        return len(self._pop)

    def set_geometry(self, **kwgs):
        """
        Generic creation of a population geomatry
        """
        pass

    def clear_geometry(self):
        self.geom = None

    def create_population(self, **kwgs):
        """
        Generic creation of a population
        """
        pass

    def clear_population(self):
        """
        Delete the current population
        """
        self._pop = DataFrame(columns=["types", "diameters"])
        self.mask_labels = []

    def place_population(self, **kwgs):
        """
        Generic method placing population member in the geometry
        """
        pass

    def clear_population_placement(self):
        """
        Reset the placement of the population
        """
        if self.has_placed_pop:
            self._pop["y"] = 0
            self._pop["z"] = 0
            self._pop["is_placed"] = False

    def placed_id(self):
        if self.has_placed_pop:
            self._pop["placed_id"] = np.zeros(len(self)) - 1
            _placed_id = np.sum(self._pop["is_placed"])
            self._pop.query("placed_id")["placed_id"] = np.arange(_placed_id)
            return

    @property
    def check_placement(self) -> np.ndarray:
        if not self.has_pop:
            return np.zeros(1, dtype=bool)
        if not ("y" in self._pop and "z" in self._pop):
            return np.zeros(len(self), dtype=bool)

        ok_trace = self.geom.is_inside((self._pop["y"], self._pop["z"]), for_all=False)
        if "is_placed" in self._pop:
            ok_trace &= self.axon_pop["is_placed"]
            n_discarded = np.sum(self.axon_pop["is_placed"]) - np.sum(ok_trace)
            if n_discarded > 0:
                _str = f"{n_discarded} axon"
                if n_discarded > 1:
                    _str += "s"
                pass_info(
                    _str
                    + " are not in the new geometry. Consider replacing population if needed"
                )
        self._pop["is_placed"] = ok_trace
        return self._pop["is_placed"].to_numpy(dtype=bool)

    def __getitem__(self, key) -> DataFrame:
        if self.has_pop:
            return self._pop[key]

    @property
    def iloc(self):
        if self.has_pop:
            return self._pop.loc

    # -------------------- #
    # Handeling population #
    # -------------------- #
    def rotate(
        self,
        angle: float,
        with_geom: bool = True,
        with_pop: bool = True,
        degree: bool = False,
        mask_on: list[str] = [],
    ):
        """
        Rotate the population and/or its geometry

        Parameters
        ----------
        angle : _type_
            _description_
        with_geom : bool, optional
            if True rotate the geometry, by default True
        with_pop : bool, optional
            if True rotate the population, by default True
        degree : bool, optional
            if True `angle` is in degree, if False in radian, by default False
        """
        if self.has_geom and with_geom:
            self.geom.rotate(angle, degree=degree)
        if self.has_placed_pop and with_pop:
            _y, _z = rotate_2D(
                center=self.geom.center,
                point=(self._pop["y"].to_numpy(), self._pop["z"].to_numpy()),
                angle=angle,
                degree=degree,
            )
            _m = self.get_mask(mask_labels=mask_on)
            self._pop["y"], self._pop["z"] = _y * _m, _z * _m
        self.check_placement

    def translate(
        self,
        y: float,
        z: float,
        with_geom: bool = True,
        with_pop: bool = True,
        mask_on: list[str] = [],
    ):
        """
        Translate the population and/or its geometry

        Parameters
        ----------
        y   : float
            y axis value for the translation in um
        z   : float
            z axis value for the translation in um
        with_geom : bool, optional
            if True rotate the geometry, by default True
        with_pop : bool, optional
            if True rotate the population, by default True
        """
        if self.has_geom and with_geom:
            self.geom.translate(y=y, z=z)
        if self.has_placed_pop and with_pop:
            _m = self.get_mask(mask_labels=mask_on, otype="numpy")
            self._pop["y"] += y * _m
            self._pop["z"] += z * _m
        self.check_placement

    # ----------------------- #
    # Mask and sub-population #
    # ----------------------- #
    @property
    def n_mask(self):
        """
        number of mask added to the population
        """
        return len(self.mask_labels)

    def add_mask(
        self,
        data: np.ndarray | str,
        label: None | str = None,
        overwrite: bool = True,
        mask_on: list[str] = [],
    ) -> tuple[int, np.ndarray]:
        """
        Add a mask on the population

        Parameters
        ----------
        data : np.ndarray | str
            Data to use for the mask, can be either:
             - str: compatible to :meth:`DataFrame.eval` from wich the mask will be generated.
             - 1D array-like: Mask that will be converted to booleen and added.
        label : None | str, optional
            Mask label, if None the label is set to `"mask_n"` where n in the smaller leading to an unused label, by default None.
        overwrite : bool, optional
            if True and `label` exists the method will do nothing, by default True
        """
        if not self.has_pop:
            rise_warning("Masks can be added only after population")
        if label is None:
            i_lab = 0
            label = f"mask_{i_lab}"
            while label in self.mask_labels:
                i_lab += 1
                label = f"mask_{i_lab}"
        if label in self.mask_labels and not overwrite:
            rise_warning(
                f"Mask {label} already exist, not added. Please set overwrite to True if overwrite is Needed"
            )
        else:
            if isinstance(data, str):
                mask = self._pop.eval(data)
            else:
                mask = np.array(data, dtype=bool)
                if len(mask) != len(self):
                    full_mask = np.zeros(len(self), dtype=bool)
                    i_mask = self.get_sub_population(
                        mask_labels=mask_on
                    ).index.to_numpy(dtype=int)
                    full_mask[i_mask] = mask
                    mask = full_mask
            self._pop[label] = mask
            self.mask_labels.append(label)
        return label, mask

    def valid_mask_labels(
        self, mask_labels: None | Iterable[str] | str = None
    ) -> list[str]:
        if mask_labels is None:
            _labels = self.mask_labels
        elif isinstance(mask_labels, str):
            if mask_labels in self.mask_labels:
                _labels = [mask_labels]
            else:
                rise_warning("label not found")
        else:

            _labels = [_lab for _lab in mask_labels if _lab in self.mask_labels]

        return _labels

    def clear_masks(self, mask_labels: None | Iterable[str] | str = None):
        """
        Delete one or several mask

        Parameters
        ----------
        mask_labels : None | Iterable[str] | str, optional
            Labels of the mask to delete, if None all are deleted, by default None
        """
        _mask_to_rmv = self.valid_mask_labels(mask_labels)
        self._pop.drop(_mask_to_rmv, axis="columns")
        self.mask_labels = [
            _mask for _mask in self.mask_labels if _mask not in _mask_to_rmv
        ]
        pass_info(f"the following mask were removed: {_mask_to_rmv}")

    def get_mask(
        self,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        placed_only: bool = True,
        otype: None | Literal["numpy", "list"] = None,
    ) -> DataFrame | np.ndarray | list:
        """
        Get a population mask from an expression or a list of labels.

        Note
        ----
        For supopulation from expression look at :meth:`pandas.DataFrame.eval` or :meth:`pandas.DataFrame.query` documentation.

        Tip
        ---
        To simplify, :meth:`self.get_mask` correspond to :meth:`pandas.DataFrame.eval` and :meth:`self.get_sub_population` correspond to :meth:`pandas.DataFrame.query`

        Parameters
        ----------
        expr : str | None, optional
            If not None mask is generated using :meth:`pandas.DataFrame.eval` of this expression, by default None
        mask_labels : None | Iterable[str] | str, optional
            Label or list of labels already added to the population, by default []
        placed_only : bool, optional
            if True add `"is_place"` column to the mask, by default True
        otype : None | Literal[&quot;numpy&quot;, &quot;list&quot;], optional
            type of the output see :func:`~nrv.backend._extlib_interface.df_to`, by default None

        Returns
        -------
        DataFrame | np.ndarray | list
            array like of booleen of the same size than the population corresponding to the mask
        """
        if self.has_pop:
            _mask = self._pop["diameters"] > 0
            if expr is None:
                _labels = self.valid_mask_labels(mask_labels)
                if placed_only and self.has_placed_pop:
                    _labels.append("is_placed")
                if len(_labels):
                    _mask = self._pop[list(_labels)].all(axis="columns")
            else:
                if placed_only and self.has_placed_pop:
                    expr += f" & is_placed"
                _mask = self._pop.eval(expr=expr)
            return df_to(_mask, otype)

    def get_sub_population(
        self,
        expr: str | None = None,
        mask_labels: None | Iterable[str] | str = [],
        placed_only: bool = True,
    ) -> DataFrame:
        """
        Get a sub population from an expression or a list of labels.

        Note
        ----
        For supopulation from expression look at :meth:`pandas.DataFrame.eval` or :meth:`pandas.DataFrame.query` documentation.

        Tip
        ---
        To simplify, :meth:`self.get_mask` correspond to :meth:`pandas.DataFrame.eval` and :meth:`self.get_sub_population` correspond to :meth:`pandas.DataFrame.query`

        Parameters
        ----------
        expr : str | None, optional
            If not None mask is generated using :meth:`pandas.DataFrame.eval` of this expression, by default None
        mask_labels : None | Iterable[str] | str, optional
            Label or list of labels already added to the population, by default []
        placed_only : bool, optional
            if True add `"is_place"` column to the mask, by default True
        otype : None | Literal[&quot;numpy&quot;, &quot;list&quot;], optional
            type of the output see :func:`~nrv.backend._extlib_interface.df_to`, by default None

        Returns
        -------
        DataFrame
            Containing the subpopulation parameters.
        """
        _mask = self.get_mask(
            expr=expr, mask_labels=mask_labels, placed_only=placed_only
        )
        return self._pop[_mask]

    # ----- ------------ #
    # Ploting population #
    # ----- ------------ #

    def plot(self, ax: plt.Axes, **kwgs):
        """
        Plot the population and its geometry :class:`matplotlib.pyplot.Axes`

        Parameters
        ----------
        ax : plt.Axes
            axes where population should be ploted
        """
        pass
