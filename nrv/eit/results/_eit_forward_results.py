from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

from typing_extensions import Literal
from ..utils._misc import (
    gen_idx_arange,
    plot_array,
    adjust_axes,
    compute_v_rec_cap_idxs,
)

from ...backend import json_load, load_any
from ...backend._extlib_interface import set_idxs
from ...nmod.results import nerve_results
from ...utils import nrv_interp


class eit_forward_results(dict):
    """
    Stores and manages the results of an Electrical Impedance Tomography (EIT) forward simulation.

    This class combines outputs from both the nerve simulation and the finite element (FEM) EIT simulation,
    providing convenient access to time series, electrode measurements, protocol information, and post-processing tools.

    Parameters
    ----------
    nerve_res : nerve_results, str, dict, or None, optional
        Results from the nerve simulation, or a path/dictionary to load them.
    fem_res : dict or None, optional
        Results from the FEM EIT simulation.
    data : str or dict or None, optional
        Path or dictionary containing saved results to load.

    Notes
    -----
    - This class is designed for efficient post-processing and visualization of EIT simulation results.
    - It supports multi-frequency and multi-protocol EIT simulations.
    - Failed or invalid time steps are automatically detected and can be filtered out.
    - Provides tools for CAP detection and analysis.

    Examples
    --------
    >>> res = eit_forward_results(nerve_res=nerve_sim, fem_res=fem_sim) # create results
    >>> dv = res.dv_eit(i_e=0) # Access voltage shift of the first electrode
    >>> cap_mask = res.get_cap_mask(thr=0.1)
    >>> res.plot_recruited_fibers(ax)
    """

    # ...existing code...
    def __init__(
        self,
        nerve_res: nerve_results | str | dict | dict | None = None,
        fem_res: dict | None = None,
        data: str | dict | None = None,
    ):
        self.incorporate_nerve_res(nerve_res)
        self.filter_res = True

        self.interp_kind = "linear"
        self._v_eit_interp = None
        self._v_rec_interp = None
        if isinstance(data, (str, dict)):
            self.load(data)

        self._cap_ppt: None | pd.DataFrame = None
        self.rec_cap_ppt: None | pd.DataFrame = None

    def load(self, data: str | dict):
        if isinstance(data, str):
            key_dic = json_load(data)
        else:
            key_dic = data
        self.update(key_dic)
        np_keys = {
            "t_rec",
            "v_rec",
            "v_eit",
            "v_eit_phase",
            "failed_time_step",
            "t",
            "f",
            "p",
        }
        for key in np_keys:
            if key in self:
                self[key] = np.array(self[key])

    ## Property attributes

    @property
    def has_nerve_res(self) -> bool:
        return "t_rec" in self

    @property
    def has_fem_res(self) -> bool:
        return "v_eit" in self

    @property
    def has_failed_test(self) -> bool:
        if np.iterable(self.fail_results):
            return len(self.fail_results) > 0
        return False

    @property
    def is_multi_freqs(self) -> bool:
        """
        Returns True if the EIT simulation was run over multiple frequencies

        Returns
        -------
        bool
        """
        return self.n_f > 1

    @property
    def is_multi_patern(self) -> bool:
        """
        Returns True if the injections protocole contains more than one patern.

        Returns
        -------
        bool
        """
        return self.n_p > 1

    @property
    def n_t(self) -> int:
        """
        number of temporal point

        Returns
        -------
        int
        """
        if not self.has_fem_res:
            print("No FEM results in object times cannot be found")
            return 0
        return len(self["t"])

    @property
    def n_e(self) -> int:
        """
        number of electrodes

        Returns
        -------
        int
        """
        if not self.has_fem_res:
            print("No FEM results in object")
            return 0
        return self["v_eit"].shape[-1]

    @property
    def n_f(self) -> int:
        """
        number of frequency point

        Returns
        -------
        int
        """
        if not self.has_fem_res:
            print("No FEM results in object")
            return 0
        if not np.iterable(self["f"]):
            return 1
        return len(self["f"])

    @property
    def n_p(self) -> int:
        """
        number of frequency point

        Returns
        -------
        int
        """
        if not self.has_fem_res:
            print("No FEM results in object")
            return 0
        if "p" not in self:
            return 1
        return len(self["p"])

    # Shape properties
    @property
    def shape(self) -> tuple:
        """
        return the shape of `v_eit`

        Returns
        -------
        tuple
        """
        if not self.has_fem_res:
            print("No FEM results in object")
            return ()
        return self["v_eit"].shape

    @property
    def e_axis(self) -> int:
        return -1

    @property
    def t_axis(self) -> int:
        return -2

    @property
    def f_axis(self) -> int:
        if self.is_multi_freqs:
            return -3
        else:
            print("WARNING: No frequency axis in the result")

    @property
    def fail_results(self):
        if not self.has_fem_res:
            print("No FEM results in object")
            return np.array([])
        if "failed_time_step" not in self:
            __filter_res = False
            self.filter_res, __filter_res = __filter_res, self.filter_res
            self["failed_time_step"] = np.squeeze(
                np.where((self.v_eit(i_e=0) == 1e10) | (abs(self.dv_eit(i_e=0)) > 1e-3))
            )
            self.filter_res = __filter_res
        return self["failed_time_step"]

    @property
    def v_eit_interp(self):
        if self._v_eit_interp is None:
            X_ = self.t()
            Y_ = self.v_eit()
            if not self.is_multi_freqs:
                self._v_eit_interp = nrv_interp(
                    X_values=X_, Y_values=Y_, kind=self.interp_kind
                )

            else:
                Y_ = Y_.swapaxes(self.t_axis, self.f_axis)
                _interp = nrv_interp(X_values=X_, Y_values=Y_, kind=self.interp_kind)
                self._v_eit_interp = lambda X: _interp(X).swapaxes(
                    self.t_axis, self.f_axis
                )
        return self._v_eit_interp

    @property
    def v_rec_interp(self):
        if self._v_rec_interp is None:
            X_ = self["t_rec"]
            Y_ = self["v_rec"]
            self._v_rec_interp = nrv_interp(
                X_values=X_, Y_values=Y_, kind=self.interp_kind
            )
        return self._v_rec_interp

    def incorporate_nerve_res(
        self, nerve_res: nerve_results | str | dict | dict | None
    ):
        nerve_res = load_any(nerve_res, rec_context=True)
        if isinstance(nerve_res, nerve_results):
            if "recorder" in nerve_res:
                self["t_rec"] = np.array(nerve_res.recorder.t)
                self["v_rec"] = (len(self["t_rec"]),)
                n_elec = len(nerve_res.recorder.recording_points)
                self["v_rec"] = np.zeros((len(self["t_rec"]), n_elec))

                for i in range(n_elec):
                    self["v_rec"][:, i] = np.array(
                        nerve_res.recorder.recording_points[i].recording
                    )

    def update_failed_results(self, _v_eit, _v_eit_phase):
        i_t, i_f = None, None
        if self.is_multi_freqs:
            i_t, i_f = self.fail_results[0, :], self.fail_results[1, :]
        else:
            i_t = self.fail_results
        ix_update = self.ix_(i_f=i_f, i_t=i_t)
        if np.allclose(_v_eit.shape, self["v_eit"].shape):
            self["v_eit"][ix_update] = _v_eit[ix_update]
            self["v_eit_phase"][ix_update] = _v_eit_phase[ix_update]
        elif np.allclose(_v_eit.shape, self["v_eit"][ix_update].shape):
            self["v_eit"][ix_update] = _v_eit
            self["v_eit_phase"][ix_update] = _v_eit_phase
            if "failed_time_step" in self:
                del self["failed_time_step"]
        else:
            print("wrong dimensions cannot results be updated")

    def t(self, dt=None, i_f=None):
        if dt is None:
            _t = deepcopy(self["t"])
            if self.filter_res and self.has_failed_test:
                _t = np.delete(_t, self.fail_results, axis=0)
        else:
            t_sim = self["t"][-1]
            n_pts = int(t_sim / dt)
            _t = np.arange(n_pts) * dt
        return _t

    def get_idxs(
        self,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        n_t: int | None = None,
        include_freqs: bool = True,
        include_paterns: bool = True,
    ) -> tuple[np.ndarray]:
        """
        Return a tuple containing the

        Parameters
        ----------
        i_t : np.ndarray | int | None, optional
            _description_, by default None
        i_e : np.ndarray | int | None, optional
            _description_, by default None
        i_f : np.ndarray | int | None, optional
            _description_, by default None
        i_p : np.ndarray | int | None, optional
            _description_, by default None
        n_t : int | None, optional
            _description_, by default None
        include_freqs : bool, optional
            _description_, by default True
        include_paterns : bool, optional
            _description_, by default True

        Returns
        -------
        tuple[np.ndarray]
            _description_
        """
        i_all = (set_idxs(i_t, n_t or self.n_t), set_idxs(i_e, self.n_e))
        if self.is_multi_freqs and include_freqs:
            i_all = (set_idxs(i_f, self.n_f),) + i_all
        if self.is_multi_patern and include_paterns:
            i_all = (set_idxs(i_p, self.n_p),) + i_all
        return i_all

    def ix_(
        self,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        n_t: int | None = None,
        **kwgs,
    ) -> tuple[np.ndarray]:
        i_ = self.get_idxs(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, n_t=n_t, **kwgs)
        return np.ix_(*i_)

    def v_eit_idx(
        self,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        signed: bool = False,
        **kwgs,
    ):
        __filter_res = self.filter_res and i_t is None
        _v = self["v_eit"][
            self.ix_(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        ].squeeze()
        if signed:
            phi = self["v_eit_phase"][
                self.ix_(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
            ].squeeze()
            sign = 2 * (phi < np.pi) - 1
            _v = _v * np.cos(phi)
            # _v = _v * sign

        if __filter_res and self.has_failed_test:
            _v = np.delete(_v, self.fail_results, axis=0)
        return _v

    @property
    def _v_eit(self) -> np.ndarray:
        """
        Fast access to all v_eit values

        Returns
        -------
        np.ndarray
        """
        return self["v_eit"].copy()

    def v_eit(
        self,
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        if t is None:
            return self.v_eit_idx(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        else:
            _v = self.v_eit_interp(t)
            _v = _v[self.ix_(i_e=i_e, i_f=i_f, i_p=i_p, n_t=len(t), **kwgs)]
            return np.squeeze(_v)

    @property
    def _v_0(self) -> np.ndarray:
        """
        Fast access to all v_0 values

        Returns
        -------
        np.ndarray
        """
        return self._v_eit[..., 0, :]

    def v_0(
        self,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        kwgs.update(
            {
                "i_t": 0,
                "i_e": i_e,
                "i_f": i_f,
            }
        )
        _v_0 = self.v_eit(**kwgs)
        return _v_0.squeeze()

    @property
    def dv_eit(self) -> np.ndarray:
        """
        Fast access to all dv_eit values

        Returns
        -------
        np.ndarray
        """
        _v = self._v_eit
        return _v - _v[..., :1, :]

    def dv_eit(
        self,
        t: np.ndarray | float | None = None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        pc: bool = False,
        **kwgs,
    ) -> np.ndarray:
        _v = self.v_eit(t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        _v_0 = self.v_0(i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        _v, _v_0 = adjust_axes(arr1=_v, arr2=_v_0)
        _dv = _v - _v_0

        if pc:
            _dv *= 100 / _v_0
            _dv[np.isnan(_dv)] = 0
        return np.squeeze(_dv)

    @property
    def _dv_eit_pc(self) -> np.ndarray:
        """
        Fast access to all dv_eit_pc values

        Returns
        -------
        np.ndarray
        """
        _v = self._v_eit
        _v_0 = _v[..., :1, :]
        _dv = 100 * (_v - _v_0) / _v_0
        _dv[np.isnan(_dv)] = 0
        return _dv

    def dv_eit_pc(
        self,
        t: np.ndarray | float | None = None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        return self.dv_eit(t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, pc=True, **kwgs)

    def dv_eit_normalized(
        self,
        t: np.ndarray | float | None = None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        pc: bool = False,
        axis: np.ndarray | int | None = None,
        **kwgs,
    ):
        _dv = np.abs(
            self.dv_eit(t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, pc=pc, **kwgs)
        )
        if axis is None:
            axis = self.t_axis
        _dv_max = np.max(_dv, axis=axis)
        _dv_max = np.expand_dims(_dv_max, axis)
        _dv_nrm = _dv / _dv_max
        _dv_nrm[np.isnan(_dv_nrm)] = 0
        return _dv_nrm

    @property
    def _v_rec(self) -> np.ndarray:
        return self["v_rec"].copy()

    def v_rec(
        self,
        t: np.ndarray | float | None = None,
        i_e: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        if not self.has_nerve_res:
            print("No nerve results in object v_eit cannot be found")
            return None
        if t is None:
            _v = self["v_rec"]
            _v = _v[
                self.ix_(
                    i_e=i_e,
                    n_t=len(self["t_rec"]),
                    include_freqs=False,
                    include_paterns=False,
                    **kwgs,
                )
            ]
            return _v
        else:
            _v = self.v_rec_interp(t)
            _v = _v[self.ix_(i_e=i_e, n_t=len(t), include_freqs=False, **kwgs)]
            return np.squeeze(_v)

    ## Postprocessing method
    def i_t_duration(self, i_t_start, i_t_stop):
        return self["t"][i_t_stop] - self["t"][i_t_start]

    def get_cap_mask(self, thr: float = 0.05, **kwgs):
        # Computing normailzed dv
        dv_nrmlz = abs(self.dv_eit_pc(i_f=0, **kwgs))
        dv_nrmlz /= dv_nrmlz.max()
        # finding electrode whe cap is most pronounced
        i_e = np.argwhere(dv_nrmlz == 1.0)[-1, -1]
        dv_nrmlz = dv_nrmlz[..., i_e]
        _mask = dv_nrmlz > thr
        return _mask

    def get_cap_i_t(self, thr: float = 0.05, verbose: bool = False, **kwgs) -> list:
        _cap_mask = self.get_cap_mask(thr=thr, **kwgs)
        i_cap = np.arange(self.n_t)[_cap_mask]
        if verbose:
            print("i_cap", i_cap)
        # No CAP detected
        if len(i_cap) == 0:
            return [i_cap]
        # At least 1 CAP
        i_cut = np.argwhere(np.diff(i_cap) > 1).T[0] + 1
        if verbose:
            print("i_cut", i_cut)
            print("diff i_cap", np.diff(i_cap))
        # Only 1 CAP detected
        if len(i_cut) == 0:
            return [i_cap]
        # More than 1 CAP
        i_cap_split = np.array_split(i_cap, i_cut)
        if verbose:
            print(len(i_cap_split[0]), len(i_cap_split))
        return i_cap_split

    def get_acap_mask(
        self,
        thr: float = 0.05,
        t_new_cap: float | None = None,
        res_ax: Literal["default"] | None | tuple = "default",
        **kwgs,
    ):
        # Computing normailzed dv
        dv_nrmlz = abs(self._dv_eit_pc)  # - abs(self.dv_eit_pc(**kwgs))
        if res_ax == "default":
            res_ax = (-2, -1)
            if self.is_multi_freqs:
                res_ax = (-3,) + res_ax
        if t_new_cap is not None:
            i_t = np.argmin(np.abs(self["t"] - t_new_cap))
            _dv_nrmlz = dv_nrmlz[..., :i_t, :]
            _, dv_nrmlz_max_ = adjust_axes(_dv_nrmlz, _dv_nrmlz.max(axis=res_ax))
            dv_nrmlz[..., :i_t, :] = _dv_nrmlz / dv_nrmlz_max_

            _dv_nrmlz = dv_nrmlz[..., i_t:, :]
            _, dv_nrmlz_max_ = adjust_axes(_dv_nrmlz, _dv_nrmlz.max(axis=res_ax))

            dv_nrmlz[..., i_t:, :] = _dv_nrmlz / dv_nrmlz_max_
        else:
            _, dv_nrmlz_max = adjust_axes(dv_nrmlz, dv_nrmlz.max(axis=res_ax))
            dv_nrmlz /= dv_nrmlz_max
        _mask = dv_nrmlz > thr
        return _mask

    def _get_acap_i_e(self, i_l: int | np.ndarray):
        return i_l % self.n_e

    def _get_acap_i_f(self, i_l: int | np.ndarray):
        if self.is_multi_freqs:
            return (i_l // self.n_e) % self.n_f
        return np.zeros(i_l.shape)

    def _get_line_ppt(self, i_l: int | np.ndarray, with_f: bool = True):
        if with_f:
            return np.vstack(
                (
                    self._get_acap_i_f(i_l),
                    self._get_acap_i_e(i_l),
                )
            )
        else:
            return np.vstack((self._get_acap_i_e(i_l),))

    @property
    def _axes_labels(self):
        return ["freq", "elec"]

    @property
    def _column_labels(self):
        return ["i_f", "i_e"]

    def get_acap_t_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ) -> pd.DataFrame:

        if store == "default" and self._cap_ppt is not None:
            return self._cap_ppt

        _cap_mask = np.swapaxes(
            self.get_acap_mask(thr=thr, **kwgs), self.e_axis, self.t_axis
        )

        # No CAP detected
        if not _cap_mask.any():
            print(
                f"No CAP detected. Check the results or increase the detection treshold (thr={thr})"
            )
            return None

        shape_2axes = (np.prod(_cap_mask.shape[:-1]), _cap_mask.shape[-1])
        _cap_mask = _cap_mask.reshape(shape_2axes).astype(int)
        # i_cap = _i_t[_cap_mask]
        # Adding a first column of 0 for line starting with a 1
        padded = np.hstack((_cap_mask, np.zeros((shape_2axes[0], 1), dtype=int)))
        diffs = np.diff(padded, axis=1)

        # Start of a CAP (0 -> 1)
        starts = np.where(diffs == 1)
        # End of a CAP (1 -> 0)
        ends = np.where(diffs == -1)
        i_l = starts[0]  # also = ends[0]
        i_cap_num = gen_idx_arange(
            np.where(np.diff(i_l, prepend=-1) > 0)[0], i_l.shape[0]
        )

        i_t_start = starts[1]
        i_t_end = ends[1]
        d_acap = self["t"][i_t_end] - self["t"][i_t_start]

        if verbose:
            print(f"i_l {i_l.shape}:", i_l)
            print(f"i_cap_num {i_cap_num.shape}:", i_cap_num)
            print(f"i_t_start {i_t_start.shape}:", i_t_start)
            print(f"i_t_end {i_t_end.shape}:", i_t_end)
            print(f"d_acap {d_acap.shape}:", d_acap)
            print(f"_cap_mask {_cap_mask.shape}:", _cap_mask)

        l_ppt = self._get_line_ppt(i_l=i_l)
        labels = ["line"] + self._column_labels + ["i_cap", "i_t_min", "i_t_max"]
        if verbose:
            print(f"l_ppt {l_ppt.shape}:", l_ppt)

        _data = np.vstack(
            (
                i_l,
                l_ppt,
                i_cap_num,
                i_t_start,
                i_t_end,
            )
        ).T.astype(int)
        _cap_ppt = pd.DataFrame(data=_data, columns=labels)
        _cap_ppt["duration"] = d_acap
        if store in ["default", "overwrite"]:
            self._cap_ppt = _cap_ppt
        if verbose:
            print(f"cap_ppt {self._cap_ppt.shape}\n", self._cap_ppt)
        return _cap_ppt

    def get_acap_v_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ) -> pd.DataFrame:
        """

        Parameters
        ----------
        thr : float, optional
            _description_, by default 0.05
        verbose : bool, optional
            _description_, by default False
        i_res : _type_, optional
            _description_, by default None

        Returns
        -------
        _type_
            _description_
        """
        if (
            store == "default"
            and self._cap_ppt is not None
            and "dv_amp" in self._cap_ppt
        ):
            return self._cap_ppt

        _cap_ppt = self.get_acap_t_ppt(thr=thr, store=store, **kwgs)
        dv_masked, _v_0 = self.get_dv_from_df(
            _cap_ppt, verbose=verbose, masked_time=True, with_v_0=True
        )
        _mask_pos = dv_masked.mask & (dv_masked.data > 0)
        _mask_neg = dv_masked.mask & (dv_masked.data < 0)
        _dv_thr = np.ma.min(np.abs(dv_masked), axis=1)

        dv_masked.mask = _mask_neg
        _dv_min = np.ma.min(dv_masked, axis=1)
        dv_masked.mask = _mask_pos
        _dv_amp = np.ma.max(dv_masked, axis=1) - _dv_min
        _dv_pc_thr = 100 * _dv_thr / _v_0
        _dv_pc_min = 100 * _dv_min / _v_0
        _dv_pc_amp = 100 * _dv_amp / _v_0

        _cap_ppt["dv_min"] = _dv_min
        _cap_ppt["dv_amp"] = _dv_amp
        _cap_ppt["dv_thr"] = _dv_thr
        _cap_ppt["dv_pc_min"] = _dv_pc_min
        _cap_ppt["dv_pc_amp"] = _dv_pc_amp
        _cap_ppt["dv_pc_thr"] = _dv_pc_thr
        if (self._cap_ppt is None and store == "default") or store == "overwrite":
            self._cap_ppt.update(_cap_ppt)
        if verbose:
            print(f"cap_ppt {_cap_ppt.shape}\n", self._cap_ppt)
        return _cap_ppt

    def update_acap_inde_t_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ) -> pd.DataFrame:
        """

        Parameters
        ----------
        thr : float, optional
            _description_, by default 0.05
        verbose : bool, optional
            _description_, by default False
        i_res : _type_, optional
            _description_, by default None

        Returns
        -------
        _type_
            _description_
        """
        _cap_ppt = self.get_acap_v_ppt(thr=thr, store=store, **kwgs)

        dv_masked, _v_0 = self.get_dv_from_df(
            _cap_ppt, verbose=verbose, masked_time=True, with_v_0=True
        )
        _mask_pos = dv_masked.mask & (dv_masked.data > 0)
        _mask_neg = dv_masked.mask & (dv_masked.data < 0)
        _dv_thr = np.ma.min(np.abs(dv_masked), axis=1)

        dv_masked.mask = _mask_neg
        _dv_min = np.ma.min(dv_masked, axis=1)
        dv_masked.mask = _mask_pos
        _dv_amp = np.ma.max(dv_masked, axis=1) - _dv_min
        _dv_pc_thr = 100 * _dv_thr / _v_0
        _dv_pc_min = 100 * _dv_min / _v_0
        _dv_pc_amp = 100 * _dv_amp / _v_0

        _cap_ppt["dv_min"] = _dv_min
        _cap_ppt["dv_amp"] = _dv_amp
        _cap_ppt["dv_thr"] = _dv_thr
        _cap_ppt["dv_pc_min"] = _dv_pc_min
        _cap_ppt["dv_pc_amp"] = _dv_pc_amp
        _cap_ppt["dv_pc_thr"] = _dv_pc_thr
        if (self._cap_ppt is None and store == "default") or store == "overwrite":
            self._cap_ppt.update(_cap_ppt)
        if verbose:
            print(f"cap_ppt {_cap_ppt.shape}\n", self._cap_ppt)
        return _cap_ppt

    def get_dv_from_df(
        self,
        data: pd.DataFrame,
        verbose: bool = False,
        masked_time: bool = True,
        with_v_0: bool = False,
    ) -> np.ndarray | np.ma.MaskedArray:
        c_labs = self._column_labels
        if not self.is_multi_freqs:
            c_labs.remove("i_f")
        _i = tuple()
        for _lab in c_labs:
            _i += (data[_lab].to_numpy(),)

        if verbose:
            print(f"_i ({len(_i)}, {len(_i[0])})", _i)

        _v = self["v_eit"].copy()
        _v = _v.swapaxes(-1, -2)
        _v = _v[_i]
        _v_0 = _v[..., 0]
        _dv = _v - _v_0[:, np.newaxis]

        if verbose:
            print(f"_v {_v.shape}", _v.max())
            print(f"_v_0 {_v_0.shape}", _v_0.max())
            print(f"_dv {_dv.shape}", _dv.max())

        if masked_time:
            _i_t = np.multiply(
                np.ones(_v.shape, dtype=int), np.arange(self.n_t, dtype=int)[np.newaxis]
            )
            ##! numpy masked array are inverted (i.e. only False element are considerated)
            _mask = ~(
                (_i_t > data["i_t_min"].to_numpy()[:, np.newaxis])
                & (_i_t < data["i_t_max"].to_numpy()[:, np.newaxis])
            )
            _dv = np.ma.masked_array(_dv, _mask)

        if with_v_0:
            _dv = _dv, _v_0

        return _dv

    # Rec ppt
    def get_reccap_ppt(self, thr: float = 0.05, **kwgs):
        # Computing normailzed dv
        if not self.has_fem_res:
            print("WARNING no recording context in the result")
            return None
        _av_rec = self._v_rec.swapaxes(-1, -2)
        shape_2axes = (np.prod(_av_rec.shape[:-1]), _av_rec.shape[-1])
        _av_rec = _av_rec.reshape(shape_2axes)
        print(_av_rec.shape)
        dt = self["t_rec"][1] - self["t_rec"][0]
        i_l = np.linspace(
            0, shape_2axes[0], 2 * shape_2axes[0], endpoint=False, dtype=int
        )

        i_reccap = np.zeros((2 * shape_2axes[0], 4), dtype=int)
        for _i, _v in enumerate(_av_rec):
            i_reccap[2 * _i, :], i_reccap[2 * _i + 1, :] = compute_v_rec_cap_idxs(
                _v,
                dt,
            )

        _da = np.vstack(
            (
                i_l,
                self._get_line_ppt(i_l, with_f=False),
                (np.arange(2 * shape_2axes[0]) + 1) % 2,
                i_reccap.T,
            )
        ).T
        c_labs = [
            "i_l",
            *self._column_labels,
            "mye_cap",
            "i_start",
            "i_min",
            "i_max",
            "i_stop",
        ]
        c_labs.remove("i_f")
        self.rec_cap_ppt = pd.DataFrame(_da, columns=c_labs)

        self.rec_cap_ppt["durations"] = (
            self["t_rec"][self.rec_cap_ppt["i_stop"]]
            - self["t_rec"][self.rec_cap_ppt["i_start"]]
        )

        self.rec_cap_ppt["amplitudes"] = (
            _av_rec[i_l, self.rec_cap_ppt["i_max"]]
            - _av_rec[i_l, self.rec_cap_ppt["i_min"]]
        )
        return self.rec_cap_ppt

    # plot methods
    def plot(
        self,
        ax: plt.Axes,
        which: str = "v_eit",
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        pc=False,
        xtype="t",
        **kwgs,
    ):
        if t is None:
            i_t = set_idxs(i_t, self.n_t)
            _t = self["t"][i_t]
        else:
            _t = t

        if which == "dv_eit":
            _y = self.dv_eit(t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, pc=pc)
        elif which == "v_rec":
            _y = self.v_rec(t=t, i_e=i_e)
            if t is None:
                _t = self["t_rec"]
        else:
            _y = self.v_eit(t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p)

        if "f" in xtype:
            if not self.is_multi_freqs:
                print("WARNING: cannot plot quasistatic results over frequencies")
                return None
            elif i_f is not None:
                _x = self["f"]
            else:
                _x = self["f"][i_f]
            _x = np.squeeze(_x)
        else:
            _x = _t
            if self.is_multi_freqs and which != "v_rec":
                pass
                # _y = _y.swapaxes(self.t_axis,self.f_axis)
        plot_array(ax, _x, _y, **kwgs)


def load_res(res_dname: str, label: str) -> eit_forward_results:
    res = None
    if not os.path.isdir(res_dname):
        print(f"results directory not found: {res_dname}")
    else:
        fem_res_file = f"{res_dname}/{label}_fem.json"
        if os.path.isfile(fem_res_file):
            res = eit_forward_results(data=fem_res_file)
        else:
            print(f"results file not found: {fem_res_file}")
    return res


def synchronize_times(
    res1: eit_forward_results, res2: eit_forward_results, dt_min=0.001
) -> np.ndarray:
    t1 = res1["t"]
    t2 = res2["t"]
    t = np.sort(np.concatenate((t1, t2)))
    mask = np.where(np.diff(t, prepend=-1) > dt_min)
    return t[mask]
