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
    r"""
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

    Note
    ----
    - This class is designed for efficient post-processing and visualization of EIT simulation results.
    - It supports multi-frequency and multi-protocol EIT simulations.
    - Failed or invalid time steps are automatically detected and can be filtered out.
    - Provides tools for CAP detection and analysis.

    Note
    ----
    In this class the eit_forward simulation results are stored in multidimensionnal tensor. This tensor contain between 2 and 5 dimensions as shown in the following table:

    .. list-table::
        :widths: 10 10 10 10 10
        :header-rows: 1

        * 
            - Dimensions
            - Paterns
            - Frequency
            - Time
            - Electrode
        * 
            - Status
            - Optional
            - Optional
            - Always
            - Always
        * 
            - Size
            - n_p
            - n_f
            - n_t
            - n_e
        * 
            - Corresponding key
            - ``"p"``
            - ``"f"``
            - ``"t"``
            - ``"e"``

    Example
    -------
    >>> res = eit_forward_results(nerve_res=nerve_sim, fem_res=fem_sim) # create results
    >>> dv = res.dv_eit(i_e=0) # Access voltage shift of the first electrode
    >>> cap_mask = res.get_cap_mask(thr=0.1)
    """

    # ...existing code...
    def __init__(
        self,
        nerve_res: nerve_results | str | dict | dict | None = None,
        fem_res: dict | None = None,
        data: str | dict | None = None,
    ):
        """
        Build an EIT forward-results container.

        Parameters
        ----------
        nerve_res : nerve_results | str | dict | None, optional
            Nerve simulation result object, or serialized data that can be loaded
            with :func:`load_any`.
        fem_res : dict | None, optional
            Reserved input for FEM results. The current implementation expects FEM
            data to be provided through ``data``.
        data : str | dict | None, optional
            Path to a JSON result file or an already loaded result dictionary.
        """
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
        """
        Load serialized EIT results into the current object.

        Parameters
        ----------
        data : str | dict
            Path to a JSON file or a dictionary containing serialized result
            entries. Known array-like entries are converted to ``numpy.ndarray``.
        """
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
        """
        Whether recording data coming from the nerve simulation is available.

        Returns
        -------
        bool
            ``True`` when ``t_rec`` is present in the container.
        """
        return "t_rec" in self

    @property
    def has_fem_res(self) -> bool:
        """
        Whether forward EIT FEM data is available.

        Returns
        -------
        bool
            ``True`` when ``v_eit`` is present in the container.
        """
        return "v_eit" in self

    @property
    def has_failed_test(self) -> bool:
        """
        Whether failed EIT samples have been identified.

        Returns
        -------
        bool
            ``True`` when :attr:`fail_results` contains at least one failed index.
        """
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
        number of drive partern point

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
        """
        Index of the electrode axis in EIT arrays.

        Returns
        -------
        int
            The last axis, equal to ``-1``.
        """
        return -1

    @property
    def t_axis(self) -> int:
        """
        Index of the time axis in EIT arrays.

        Returns
        -------
        int
            The penultimate axis, equal to ``-2``.
        """
        return -2

    @property
    def f_axis(self) -> int:
        """
        Index of the frequency axis in EIT arrays when it exists.

        Returns
        -------
        int
            ``-3`` for multi-frequency datasets.
        """
        if self.is_multi_freqs:
            return -3
        else:
            print("WARNING: No frequency axis in the result")

    @property
    def fail_results(self):
        """
        Indices of failed FEM time samples.

        Failed samples are computed lazily from the first electrode by flagging
        points equal to ``1e10`` or points whose differential response exceeds
        ``1e-3``.

        Returns
        -------
        np.ndarray
            Failed time indices for quasi-static data, or failed frequency/time
            indices for multi-frequency data.
        """
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
        """
        Interpolator for the EIT electrode potentials.

        Returns
        -------
        callable
            Callable returning interpolated ``v_eit`` values at arbitrary times.
        """
        if self._v_eit_interp is None:
            X_ = self.t()
            Y_ = self.v_eit()
            if not (self.is_multi_freqs or self.is_multi_patern):
                self._v_eit_interp = nrv_interp(
                    X_values=X_, Y_values=Y_, kind=self.interp_kind
                )

            else:
                # Interpolated dimention (time) must be in np.axe = 0
                Y_ = Y_.swapaxes(self.t_axis, 0)
                _interp = nrv_interp(X_values=X_, Y_values=Y_, kind=self.interp_kind)
                self._v_eit_interp = lambda X: _interp(X).swapaxes(
                    self.t_axis, 0
                )
        return self._v_eit_interp

    @property
    def v_rec_interp(self):
        """
        Interpolator for recorder voltages from the nerve simulation.

        Returns
        -------
        callable
            Callable returning interpolated recorder signals at arbitrary times.
        """
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
        """
        Import recorder traces from a nerve simulation result.

        Parameters
        ----------
        nerve_res : nerve_results | str | dict | None
            Nerve result object, or serialized data loadable with
            :func:`load_any`. When a recorder is present, its time vector and all
            recording-point traces are copied into ``t_rec`` and ``v_rec``.
        """
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
        """
        Replace entries previously marked as failed.

        Parameters
        ----------
        _v_eit : np.ndarray
            Replacement magnitude array, either with the full ``v_eit`` shape or
            restricted to the failed entries.
        _v_eit_phase : np.ndarray
            Replacement phase array with the same layout as ``_v_eit``.
        """
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
        """
        Return the FEM time vector, optionally resampled.

        Parameters
        ----------
        dt : float | None, optional
            If provided, generate a regular time vector from ``0`` to the end of
            the simulation using this time step. Otherwise return the stored time
            vector.
        i_f : int | None, optional
            Unused placeholder kept for API compatibility.

        Returns
        -------
        np.ndarray
            Time vector, optionally filtered to remove failed samples.
        """
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
        Build index arrays for advanced slicing of EIT results.

        Parameters
        ----------
        i_t : np.ndarray | int | None, optional
            Time indices to keep. ``None`` selects all times.
        i_e : np.ndarray | int | None, optional
            Electrode indices to keep. ``None`` selects all electrodes.
        i_f : np.ndarray | int | None, optional
            Frequency indices to keep. Ignored for quasi-static results.
        i_p : np.ndarray | int | None, optional
            Pattern indices to keep. Ignored when a single pattern is stored.
        n_t : int | None, optional
            Number of time samples to use when ``i_t`` is converted by
            :func:`set_idxs`. Defaults to :attr:`n_t`.
        include_freqs : bool, optional
            If ``True``, include the frequency axis in the returned tuple when the
            dataset is multi-frequency.
        include_paterns : bool, optional
            If ``True``, include the pattern axis in the returned tuple when the
            dataset is multi-pattern.

        Returns
        -------
        tuple[np.ndarray]
            Tuple of index arrays ordered to match the internal ``v_eit`` layout.
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
        """
        Return broadcasting indices ready for ``numpy`` advanced indexing.

        Parameters
        ----------
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices forwarded to :meth:`get_idxs`.
        n_t : int | None, optional
            Number of time samples used when expanding ``i_t``.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_idxs`.

        Returns
        -------
        tuple[np.ndarray]
            Output of :func:`numpy.ix_` built from :meth:`get_idxs`.
        """
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
        """
        Extract raw stored EIT voltages using index-based selection.

        Parameters
        ----------
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices used to select times, electrodes, frequencies, and patterns.
        signed : bool, optional
            If ``True``, convert amplitude and phase into signed voltages through
            ``v*cos(phi)``.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`ix_`.

        Returns
        -------
        np.ndarray
            Selected EIT voltage values.
        """
        __filter_res = self.filter_res and i_t is None
        _v = self["v_eit"][
            self.ix_(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
        ].squeeze()
        if signed:
            phi = self["v_eit_phase"][
                self.ix_(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)
            ].squeeze()
            _v = _v * np.cos(phi)

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
        """
        Return EIT voltages, either at stored or interpolated times.

        Parameters
        ----------
        t : np.ndarray | float | None, optional
            Evaluation times. If ``None``, values are extracted from stored
            samples; otherwise interpolation is used.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting times, electrodes, frequencies, and patterns.
            ``i_t`` is ignored when ``t`` is provided.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`v_eit_idx` or
            :meth:`ix_`.

        Returns
        -------
        np.ndarray
            EIT voltages with singleton dimensions removed.
        """
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
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        """
        Return the baseline EIT voltage at the first time sample.

        Parameters
        ----------
        i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting electrodes, frequencies, and patterns.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`v_eit`.

        Returns
        -------
        np.ndarray
            Baseline voltage values at ``i_t = 0``.
        """
        kwgs.update(
            {
                "i_t": 0,
                "i_e": i_e,
                "i_f": i_f,
                "i_p": i_p,
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
        """
        Return the voltage variation relative to the baseline sample.

        Parameters
        ----------
        t : np.ndarray | float | None, optional
            Evaluation times. If provided, the differential signal is computed on
            interpolated voltages.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting times, electrodes, frequencies, and patterns.
        pc : bool, optional
            If ``True``, express the variation as a percentage of the baseline.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`v_eit`.

        Returns
        -------
        np.ndarray
            Differential EIT signal.
        """
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
        """
        Return the percentage differential EIT signal.

        Parameters
        ----------
        t : np.ndarray | float | None, optional
            Evaluation times.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting times, electrodes, frequencies, and patterns.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`dv_eit`.

        Returns
        -------
        np.ndarray
            ``dv/v0`` expressed in percent.
        """
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
        """
        Return the absolute differential EIT signal normalized by its maximum.

        Parameters
        ----------
        t : np.ndarray | float | None, optional
            Evaluation times.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting times, electrodes, frequencies, and patterns.
        pc : bool, optional
            If ``True``, normalize the percentage variation instead of the raw
            variation.
        axis : np.ndarray | int | None, optional
            Axis along which the maximum is computed. Defaults to the time axis.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`dv_eit`.

        Returns
        -------
        np.ndarray
            Normalized absolute differential signal.
        """
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
        """
        Fast access to all recorder voltages.

        Returns
        -------
        np.ndarray
            Copy of the stored ``v_rec`` array.
        """
        return self["v_rec"].copy()

    def v_rec(
        self,
        t: np.ndarray | float | None = None,
        i_e: np.ndarray | int | None = None,
        **kwgs,
    ) -> np.ndarray:
        """
        Return recorder voltages from the nerve simulation.

        Parameters
        ----------
        t : np.ndarray | float | None, optional
            Evaluation times. If provided, recorder signals are interpolated.
        i_e : np.ndarray | int | None, optional
            Recording electrode indices to extract.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`ix_`.

        Returns
        -------
        np.ndarray
            Selected or interpolated recorder voltages.
        """
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
        """
        Convert a pair of time indices into a duration.

        Parameters
        ----------
        i_t_start : int
            Start time index.
        i_t_stop : int
            Stop time index.

        Returns
        -------
        float
            Duration between the two FEM samples.
        """
        return self["t"][i_t_stop] - self["t"][i_t_start]

    def get_cap_mask(self, thr: float = 0.05, **kwgs):
        """
        Detect the global CAP window on the most responsive electrode.

        Parameters
        ----------
        thr : float, optional
            Threshold applied to the normalized percentage differential signal.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`dv_eit_pc`.

        Returns
        -------
        np.ndarray
            Boolean mask over time identifying samples attributed to the CAP.
        """
        # Computing normailzed dv
        dv_nrmlz = abs(self.dv_eit_pc(i_f=0, **kwgs))
        dv_nrmlz /= dv_nrmlz.max()
        # finding electrode whe cap is most pronounced
        i_e = np.argwhere(dv_nrmlz == 1.0)[-1, -1]
        dv_nrmlz = dv_nrmlz[..., i_e]
        _mask = dv_nrmlz > thr
        return _mask

    def get_cap_i_t(self, thr: float = 0.05, verbose: bool = False, **kwgs) -> list:
        """
        Split CAP detections into contiguous time-index groups.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`get_cap_mask`.
        verbose : bool, optional
            If ``True``, print intermediate detection arrays.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_cap_mask`.

        Returns
        -------
        list
            List of arrays, one per detected CAP interval.
        """
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
        """
        Detect activity masks independently for each acquisition line.

        Parameters
        ----------
        thr : float, optional
            Threshold applied after line-wise normalization.
        t_new_cap : float | None, optional
            Optional time separating two normalization windows, useful when two
            CAPs should be normalized independently.
        res_ax : Literal["default"] | None | tuple, optional
            Axes used to compute normalization maxima. ``"default"`` adapts to the
            internal EIT layout.
        **kwgs : dict
            Unused placeholder kept for API symmetry.

        Returns
        -------
        np.ndarray
            Boolean mask with the same shape as ``_dv_eit_pc``.
        """
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
        """
        Convert flattened acquisition-line indices into electrode indices.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.

        Returns
        -------
        int | np.ndarray
            Electrode indices associated with each line.
        """
        return i_l % self.n_e

    def _get_acap_i_f(self, i_l: int | np.ndarray):
        """
        Convert flattened acquisition-line indices into frequency indices.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.

        Returns
        -------
        np.ndarray
            Frequency indices associated with each line.
        """
        if self.is_multi_freqs:
            return (i_l // self.n_e) % self.n_f
        return np.zeros(i_l.shape)

    def _get_acap_i_p(self, i_l: int | np.ndarray):
        """
        Convert flattened acquisition-line indices into drive paterns indices.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.

        Returns
        -------
        np.ndarray
            Frequency indices associated with each line.
        """
        if self.is_multi_patern:
            n_product = self.n_e
            if self.is_multi_freqs:
                n_product *= self.n_f
            return (i_l // n_product) % self.n_p
        return np.zeros(i_l.shape)

    def _get_line_ppt(self, i_l: int | np.ndarray, with_f: bool = True):
        """
        Build line descriptors for CAP summary tables.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.
        with_f : bool, optional
            If ``True``, include frequency indices together with electrode
            indices.

        Returns
        -------
        np.ndarray
            Stacked index rows describing each acquisition line.
        """
        if with_f:
            _line_ppt = np.vstack(
                (
                    self._get_acap_i_f(i_l),
                    self._get_acap_i_e(i_l),
                )
            )
            if self.is_multi_patern:
                _line_ppt = np.vstack(
                    (
                        self._get_acap_i_p(i_l),
                        _line_ppt
                    )
                )
            return _line_ppt
        else:
            return np.vstack((self._get_acap_i_e(i_l),))

    @property
    def _axes_labels(self):
        """
        Labels associated with flattened acquisition dimensions.

        Returns
        -------
        list[str]
            Human-readable names for the frequency and electrode axes.
        """
        _a_lab = ["freq", "elec"]
        if self.is_multi_patern:
            _a_lab = ["drive patern"] + _a_lab
        return _a_lab

    @property
    def _column_labels(self):
        """
        Column names used in CAP summary tables.

        Returns
        -------
        list[str]
            Column labels corresponding to frequency and electrode indices.
        """
        _c_lab = ["i_f", "i_e"]
        if self.is_multi_patern:
            _c_lab = ["i_p"] + _c_lab
        return _c_lab

    def get_acap_t_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ) -> pd.DataFrame:
        r"""
        Build a dataframe describing CAP time windows for each acquisition line.

        Note
        ----
        This methods adds the following columns to the CAP Dataframe:
        

        .. list-table::
           :widths: 10  10 50
           :header-rows: 1

           * - Dimensions
             - type
             - Description
           * - line
             - ``int``
             - Acquisition line index
           * - i_res (Optional)
             - ``int``
             - Results index in a ``eit_results_list``
           * - i_p (Optional)
             - ``int``
             - Injection patern index for multipatern simulation
           * - i_f
             - ``int``
             - Frequency index
           * - i_e
             - ``int``
             - Electrode index
           * - i_cap
             - ``int``
             - CAP index
           * - i_t_min
             - ``int``
             - Min index in time vector
           * - i_t_max
             - ``int``
             - Max index in time vector
           * - duration
             - ``float``
             - CAP duration in ms

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`get_acap_mask`.
        verbose : bool, optional
            If ``True``, print intermediate arrays used to build the table.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy for the resulting dataframe. ``"default"`` caches the
            first result, ``"overwrite"`` refreshes the cache, and ``"external"``
            returns the dataframe without caching it.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_acap_mask`.

        Returns
        -------
        pd.DataFrame
            One row per detected CAP segment and acquisition line.
        """
        if store == "default" and self._cap_ppt is not None:
            return self._cap_ppt

        # A mask tensor is built with one where activity can be mesured
        # e_axis and t_axis are swapped to ease the next step
        _cap_mask = np.swapaxes(
            self.get_acap_mask(thr=thr, **kwgs), self.e_axis, self.t_axis
        )

        # No CAP detected
        if not _cap_mask.any():
            print(
                f"No CAP detected. Check the results or increase the detection treshold (thr={thr})"
            )
            return None

        # Cap detected in the results
        # The multidimensionnal mask tensor (sized n_res, n_p, n_f, n_e, n_t) is flattened by acquisition-line into a 2 dimensionnal tensor (sized n_res.n_p.n_f.n_e, n_t)
        shape_2axes = (np.prod(_cap_mask.shape[:-1]), _cap_mask.shape[-1])
        _cap_mask = _cap_mask.reshape(shape_2axes).astype(int)
        # i_cap = _i_t[_cap_mask]

        # Detecting all CAPs for each acquisition-line
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

        # Building the data frame computed data
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
        Build a CAP summary table augmented with voltage metrics.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`get_acap_t_ppt`.
        verbose : bool, optional
            If ``True``, print intermediate arrays and the final dataframe.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy shared with :meth:`get_acap_t_ppt`.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_acap_t_ppt`.

        Returns
        -------
        pd.DataFrame
            CAP dataframe enriched with amplitude and percentage-based metrics.
        """
        if (
            store == "default"
            and self._cap_ppt is not None
            and "dv_amp" in self._cap_ppt
        ):
            return self._cap_ppt

        # 
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
        Refresh the cached CAP dataframe with voltage-derived metrics.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`get_acap_v_ppt`.
        verbose : bool, optional
            If ``True``, print intermediate arrays and the final dataframe.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy shared with :meth:`get_acap_v_ppt`.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_acap_v_ppt`.

        Returns
        -------
        pd.DataFrame
            Updated CAP dataframe.
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
        """
        Extract differential EIT traces described by a CAP dataframe.

        Parameters
        ----------
        data : pd.DataFrame
            Table containing at least the line descriptors and CAP time bounds.
        verbose : bool, optional
            If ``True``, print extracted indices and array shapes.
        masked_time : bool, optional
            If ``True``, mask samples outside the ``(i_t_min, i_t_max)`` interval
            stored in ``data``.
        with_v_0 : bool, optional
            If ``True``, also return the baseline voltage used for normalization.

        Returns
        -------
        np.ndarray | np.ma.MaskedArray | tuple
            Differential EIT traces, optionally masked in time and optionally
            paired with the baseline voltage.
        """
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
        """
        Build a dataframe summarizing CAPs detected on recorder traces.

        Parameters
        ----------
        thr : float, optional
            Unused placeholder kept for API compatibility.
        **kwgs : dict
            Unused placeholder for future extensions.

        Returns
        -------
        pd.DataFrame | None
            Recorder CAP summary table, or ``None`` when recording data is
            unavailable.
        """
        # Computing normailzed dv
        if not self.has_fem_res:
            print("WARNING no recording context in the result")
            return None
        _av_rec = self._v_rec.swapaxes(-1, -2)
        shape_2axes = (np.prod(_av_rec.shape[:-1]), _av_rec.shape[-1])
        _av_rec = _av_rec.reshape(shape_2axes)
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
        """
        Plot stored or interpolated EIT-related signals.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Target axes.
        which : str, optional
            Signal to plot. Supported values are ``"v_eit"``, ``"dv_eit"``, and
            ``"v_rec"``.
        t : np.ndarray | None, optional
            Optional time vector used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Indices selecting times, electrodes, frequencies, and patterns.
        pc : bool, optional
            For ``which="dv_eit"``, plot the percentage differential signal.
        xtype : str, optional
            Use ``"t"`` for time on the x-axis or include ``"f"`` to plot against
            frequency.
        **kwgs : dict
            Additional plotting arguments forwarded to :func:`plot_array`.
        """
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
            elif i_f is None:
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
    """
    Load an EIT result set from a result directory.

    Parameters
    ----------
    res_dname : str
        Directory containing serialized EIT result files.
    label : str
        Common file prefix used to locate ``"{label}_fem.json"``.

    Returns
    -------
    eit_forward_results | None
        Loaded result object, or ``None`` when the directory or file is missing.
    """
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
    """
    Merge two time vectors while removing nearly duplicated samples.

    Parameters
    ----------
    res1 : eit_forward_results
        First result object.
    res2 : eit_forward_results
        Second result object.
    dt_min : float, optional
        Minimum separation required between consecutive retained samples.

    Returns
    -------
    np.ndarray
        Sorted union of the two time vectors with close duplicates removed.
    """
    t1 = res1["t"]
    t2 = res2["t"]
    t = np.sort(np.concatenate((t1, t2)))
    mask = np.where(np.diff(t, prepend=-1) > dt_min)
    return t[mask]
