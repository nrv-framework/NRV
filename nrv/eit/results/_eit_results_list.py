import numpy as np
import os


from ._eit_forward_results import eit_forward_results, Literal
from ...backend._extlib_interface import set_idxs, get_query


class eit_results_list(eit_forward_results):
    """
    Container for multiple EIT forward simulation results, enabling batch analysis, comparison, and post-processing.

    This class extends `eit_forward_results` to handle a list of EIT results, providing unified access to temporal, electrode, frequency, and protocol axes across all simulations.
    It supports adding results from files, objects, or lists, and offers methods for filtering, slicing, and statistical analysis.

    Parameters
    ----------
    dt : float, optional
        Time step for resampling all results (default: 0.001).
    t_sim : float or None, optional
        Total simulation time. If None, inferred from first result.
    results : list of eit_forward_results, eit_forward_results, or str, optional
        Initial results to add (can be a list, single object, or filename).
    include_rec : bool, optional
        If True, include analytical nerve recordings in the container.

    Note
    ----
    - Results can be added from files, objects, or lists, and are automatically resampled to a common time axis.
    - Provides batch post-processing and statistical analysis tools for EIT simulations.
    - CAP detection and analysis methods are extended to handle multiple results.
    - Useful for comparing different simulation conditions, protocols, or geometries.

    Example
    -------
    >>> res_list = eit_results_list(dt=0.001)
    >>> res_list.add_results([res1, res2, res3])
    >>> mean_v = res_list.mean(which="v_eit")
    >>> cap_times = res_list.get_cap_i_t(thr=0.1)
    >>> error = res_list.error(which="v_eit", i_res_ref=0)
    """

    def __init__(
        self,
        dt: float | None = 0.001,
        t_sim: float | None = None,
        results: list[eit_forward_results] | eit_forward_results | str = None,
        include_rec: bool = False,
    ):
        """
        Build a container aggregating several forward EIT simulations.

        Parameters
        ----------
        dt : float | None, optional
            Common time step used to resample all added results.
        t_sim : float | None, optional
            Common simulation duration. If omitted, it is inferred from the first
            added result.
        results : list[eit_forward_results] | eit_forward_results | str, optional
            Initial result or results to add. Strings are interpreted as result
            file paths.
        include_rec : bool, optional
            If ``True``, also aggregate recorder traces from the nerve context.
        """
        super().__init__()
        self.dt: float = dt
        self.t_sim: float | None = t_sim
        self.n_res = 0
        self.res_info = {}
        self.add_results(results, include_rec=include_rec)

    @property
    def r_axis(self) -> int:
        """
        Index of the result axis in stacked arrays.

        Returns
        -------
        int
            The leading axis, equal to ``0``.
        """
        return 0

    @property
    def _axes_labels(self):
        """
        Labels associated with stacked acquisition dimensions.

        Returns
        -------
        list[str]
            Axis labels including the result dimension.
        """
        return ["res"] + super()._axes_labels

    @property
    def _column_labels(self):
        """
        Column labels used in CAP summary tables.

        Returns
        -------
        list[str]
            Column names including the result index.
        """
        return ["i_res"] + super()._column_labels

    ## add and access results methods
    def add_results(
        self,
        results: list[eit_forward_results] | eit_forward_results | str,
        include_rec: bool = False,
    ):
        """
        Add one or several EIT results to the list.

        Parameters
        ----------
        results : list[eit_forward_results] | eit_forward_results | str
            Result object, path to a serialized result, or list mixing both.
        include_rec : bool, optional
            If ``True``, resample and store recorder traces together with EIT
            voltages.
        """
        if isinstance(results, eit_forward_results):
            # first results
            if self.t_sim is None:
                self.t_sim = results["t"][-1]
                self["t"] = np.arange(int(self.t_sim / self.dt), dtype=float) * self.dt
                self["f"] = results["f"]
                if results.is_multi_patern:
                    self["p"] = results["p"]
                self["v_eit"] = np.expand_dims(results.v_eit(t=self["t"]), self.r_axis)
                if include_rec:
                    self["v_rec"] = np.expand_dims(
                        results.v_rec(t=self["t"]), self.r_axis
                    )
                    self["t_rec"] = self["t"]
            else:
                if self.t_sim < results["t"][-1]:
                    print(
                        f"Warning: {results["label"]} t_sim longer than list t_sim. Some results migth no be taken in acount"
                    )
                if self.t_sim > results["t"][-1]:
                    ## Out of Bound handeling (keep last value)
                    i_t_last = np.argwhere(self["t"] > results["t"][-1])[0, 0]
                    v_eit_ = results.v_eit(t=self["t"][:i_t_last])
                    v_eit_oob = results.v_eit(
                        t=self["t"][i_t_last:]
                    ) * 0 + results.v_eit(i_t=[-1])
                    v_eit_ = np.concatenate([v_eit_, v_eit_oob])

                    v_eit_ = np.expand_dims(v_eit_, self.r_axis)
                else:
                    v_eit_ = np.expand_dims(results.v_eit(t=self["t"]), self.r_axis)
                self["v_eit"] = np.append(self["v_eit"], v_eit_, axis=self.r_axis)
                if include_rec:
                    v_rec_ = np.expand_dims(results.v_rec(t=self["t"]), self.r_axis)
                    self["v_rec"] = np.append(self["v_rec"], v_rec_, axis=self.r_axis)

            self.res_info[f"{self.n_res}"] = {
                "computation_time": results["computation_time"],
                "res_dir": results["res_dir"],
                "label": results["label"],
                "mesh_info": results["mesh_info"],
            }
            if "parameters" in results:
                # print(results["parameters"])
                self.res_info[f"{self.n_res}"].update(results["parameters"])
            else:
                print(DeprecationWarning("eit_forward_results not up to date"))
            self.n_res += 1
        elif isinstance(results, str):
            self.add_results(eit_forward_results(data=results), include_rec=include_rec)
        elif isinstance(results, list):
            rl = sort_list_res(results)
            for res in rl:
                self.add_results(res, include_rec=include_rec)
        elif results is None:
            pass
        else:
            print("warning: results type cannot be added")

    def res_where(self, to_check: str | list | dict):
        """
        Select results whose metadata matches a query.

        Parameters
        ----------
        to_check : str | list | dict
            Search token, list of tokens, or dictionary of exact metadata pairs.

        Returns
        -------
        np.ndarray
            Boolean mask over the stored results.
        """
        if isinstance(to_check, str):
            to_check = [to_check]
        ok_res = np.zeros(self.n_res, dtype=bool)
        if isinstance(to_check, dict):
            for i in range(self.n_res):
                ok_res[i] = to_check.items() <= self.res_info[str(i)].items()
        for _t in to_check:
            for i in range(self.n_res):
                if not ok_res[i]:
                    ok_res[i] = (
                        _t in self.res_info[str(i)]["label"]
                        or _t in self.res_info[str(i)]["res_dir"]
                    )
        return ok_res

    def res_argwhere(self, to_check: str | list):
        """
        Return indices of results matching a query.

        Parameters
        ----------
        to_check : str | list | np.ndarray
            Query forwarded to :meth:`res_where`, or an already computed boolean
            mask.

        Returns
        -------
        np.ndarray
            Integer indices of matching results.
        """
        list_res = np.arange(self.n_res)
        if isinstance(to_check, np.ndarray):
            ok_res = to_check
        else:
            ok_res = self.res_where(to_check)
        return list_res[ok_res]

    ## eit_forward_results methods overwrite
    def v_0(
        self,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ):
        """
        Return baseline EIT voltages for the selected stacked results.

        Parameters
        ----------
        i_e : np.ndarray | int | None, optional
            Electrode indices to extract.
        i_f : np.ndarray | int | None, optional
            Frequency indices to extract.
        i_p : np.ndarray | int | None, optional
            Pattern indices to extract.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`eit_forward_results.v_0`.

        Returns
        -------
        np.ndarray
            Baseline voltages at the first time sample.
        """
        return super().v_0(i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)

    def get_idxs(
        self,
        i_res=0,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        n_t=None,
        **kwgs,
    ):
        """
        Build index arrays including the stacked result axis.

        Parameters
        ----------
        i_res : np.ndarray | int | None, optional
            Result indices to select.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        n_t : int | None, optional
            Number of time samples used when expanding ``i_t``.
        **kwgs : dict
            Unused placeholder kept for API compatibility.

        Returns
        -------
        tuple[np.ndarray]
            Index arrays ordered as result, then the inherited EIT axes.
        """
        idx_res = super().get_idxs(i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, n_t=n_t)
        i_res = set_idxs(i_res, self.n_res)
        idx_res_list = ()
        idx_res_list += (i_res,)
        for i in idx_res:
            idx_res_list += (i,)
        return idx_res_list

    ## Post processing
    def get_res(
        self,
        which: str = "v_eit",
        i_res: np.ndarray | int | None = None,
        t: np.ndarray | float | None = None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        v_abs: bool = False,
        **kwgs,
    ) -> np.ndarray:
        """
        Retrieve one signal family from the stacked result set.

        Parameters
        ----------
        which : str, optional
            Name of the accessor to use, such as ``"v_eit"`` or ``"dv_eit"``.
            Names ending with ``"_cap"`` are routed through :meth:`get_cap_res`.
        i_res : np.ndarray | int | None, optional
            Result indices to extract.
        t : np.ndarray | float | None, optional
            Evaluation times used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        v_abs : bool, optional
            If ``True``, return absolute values.
        **kwgs : dict
            Additional keyword arguments forwarded to the selected accessor.

        Returns
        -------
        np.ndarray
            Requested signal values.
        """
        if "_cap" in which:
            which = which.replace("_cap", "")
            __meth_str = f"self.get_cap_res(which='{which}', i_res=i_res, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)"
        else:
            __meth_str = f"self.{which}(i_res=i_res, t=t,i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs)"
        _v = eval(__meth_str)
        if v_abs:
            _v = np.abs(_v)
        return _v

    def error(
        self,
        which="v_eit",
        abs_err=True,
        i_res=None,
        i_res_ref=0,
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ):
        """
        Compute deviations from a reference result.

        Parameters
        ----------
        which : str, optional
            Signal family passed to :meth:`get_res`.
        abs_err : bool, optional
            If ``True``, return the absolute difference. Otherwise return the
            relative error normalized by the reference signal.
        i_res : np.ndarray | int | None, optional
            Result indices to compare. By default all results except
            ``i_res_ref``.
        i_res_ref : int, optional
            Reference result index.
        t : np.ndarray | float | None, optional
            Evaluation times used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_res`.

        Returns
        -------
        np.ndarray
            Absolute or relative error with respect to the reference result.
        """
        if i_res is None:
            i_res = np.arange(self.n_res)
            i_res = i_res[i_res != i_res_ref]
        _v = self.get_res(
            which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs
        )
        _v_ref = self.get_res(
            which=which,
            i_res=i_res_ref,
            t=t,
            i_t=i_t,
            i_e=i_e,
            i_f=i_f,
            i_p=i_p,
            **kwgs,
        )
        if abs_err:
            return _v - _v_ref
        else:
            return (_v - _v_ref) / _v_ref

    ## inconsistent output methods
    def _get_acap_i_res(self, i_l: int | np.ndarray, with_f: bool = True):
        """
        Convert flattened acquisition-line indices into result indices.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.
        with_f : bool, optional
            If ``True``, account for the frequency axis in the flattening rule.

        Returns
        -------
        int | np.ndarray
            Result indices associated with each flattened line.
        """
        n_product = self.n_e
        if self.is_multi_freqs and with_f:
            n_product *= self.n_f
        if self.is_multi_freqs and with_f:
            n_product *= self.n_p
        return (i_l // n_product) % self.n_res

    def _get_line_ppt(self, i_l: int | np.ndarray, with_f: bool = True):
        """
        Build line descriptors including the stacked result index.

        Parameters
        ----------
        i_l : int | np.ndarray
            Flattened line indices.
        with_f : bool, optional
            If ``True``, include frequency information in the descriptor.

        Returns
        -------
        np.ndarray
            Stacked rows describing result, frequency, and electrode indices.
        """
        return np.vstack(
            (
                self._get_acap_i_res(i_l, with_f=with_f),
                super()._get_line_ppt(i_l, with_f=with_f),
            )
        )

    def get_acap_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ):
        """
        Return the CAP summary table with voltage metrics for all results.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`get_acap_v_ppt`.
        verbose : bool, optional
            If ``True``, print intermediate arrays.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy forwarded to :meth:`get_acap_v_ppt`.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_acap_v_ppt`.

        Returns
        -------
        pd.DataFrame
            CAP summary dataframe for all stacked results.
        """
        return super().get_acap_v_ppt(
            thr=thr, verbose=verbose, store=store, i_res=None, **kwgs
        )

    def get_acap_t_ppt(
        self,
        thr: float = 0.05,
        verbose: bool = False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ):
        """
        Build a CAP timing table for all stored results.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`eit_forward_results.get_acap_t_ppt`.
        verbose : bool, optional
            If ``True``, print intermediate arrays.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy forwarded to the parent implementation.
        **kwgs : dict
            Additional keyword arguments forwarded to the parent implementation.

        Returns
        -------
        pd.DataFrame
            CAP timing dataframe aggregated across all results.
        """
        kwgs["i_res"] = None
        return super().get_acap_t_ppt(thr=thr, verbose=verbose, store=store, **kwgs)

    def get_acap_v_ppt(
        self,
        thr=0.05,
        verbose=False,
        store: Literal["default", "overwrite", "external"] = "default",
        **kwgs,
    ):
        """
        Build a CAP table with voltage metrics for all stored results.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`eit_forward_results.get_acap_v_ppt`.
        verbose : bool, optional
            If ``True``, print intermediate arrays.
        store : Literal["default", "overwrite", "external"], optional
            Storage policy forwarded to the parent implementation.
        **kwgs : dict
            Additional keyword arguments forwarded to the parent implementation.

        Returns
        -------
        pd.DataFrame
            CAP dataframe enriched with voltage metrics.
        """
        kwgs["i_res"] = None
        return super().get_acap_v_ppt(thr=thr, verbose=verbose, store=store, **kwgs)

    def get_cap_i_t(
        self, thr: float = 0.05, i_res: np.ndarray | int | None = None, **kwgs
    ) -> list:
        """
        Return CAP time-index groups for one or several results.

        Warning
        -------
        CAP durations can vary from one result to another, so the output is kept
        as a list rather than a homogeneous ``numpy.ndarray``.

        Parameters
        ----------
        thr : float, optional
            Threshold forwarded to :meth:`eit_forward_results.get_cap_i_t`.
        i_res : np.ndarray | int | None, optional
            Result indices to process. A scalar returns the parent implementation;
            an iterable returns one entry per requested result.
        **kwgs : dict
            Additional keyword arguments forwarded to the parent implementation.

        Returns
        -------
        list
            CAP time-index arrays grouped by result.
        """
        if not np.iterable(i_res):
            return super().get_cap_i_t(thr, i_res=i_res, **kwgs)
        i_res = set_idxs(i_res, self.n_res)
        _all_cap_i_t = [super().get_cap_i_t(thr, i_res=k, **kwgs) for k in i_res]
        return _all_cap_i_t

    def get_cap_i_t_lim(
        self,
        thr: float = 0.05,
        i_cap=None,
        ext_factor=None,
        expr: str | None = None,
        i_res: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
    ):
        """
        Return global CAP index limits matching a dataframe query.

        Parameters
        ----------
        thr : float, optional
            Threshold used to initialize the cached CAP table when needed.
        i_cap : int | None, optional
            CAP identifier used in the dataframe query.
        ext_factor : float | None, optional
            Optional multiplicative factor used to enlarge the returned range.
        expr : str | None, optional
            Extra pandas-query expression combined with the index filters.
        i_res, i_e, i_f, i_p : np.ndarray | int | None, optional
            Result, electrode, frequency, and pattern filters.

        Returns
        -------
        tuple[int, int]
            Minimum and maximum CAP time indices matching the query.
        """
        if self._cap_ppt is None:
            self.get_acap_t_ppt(thr=thr, i_res=None)
        _quer = get_query(
            i_cap=i_cap,
            i_res=i_res,
            i_e=i_e,
            i_f=i_f,
            i_p=i_p,
            sup1=expr,
        )
        if _quer is not None:
            _sel_cap_ppt = self._cap_ppt.query(_quer)
        else:
            _sel_cap_ppt = self._cap_ppt
        _cap_i_t_lim = [_sel_cap_ppt["i_t_min"].min(), _sel_cap_ppt["i_t_max"].max()]

        # Extend the temporal range
        if ext_factor is not None:
            lim_range = _cap_i_t_lim[1] - _cap_i_t_lim[0]
            lim_shift = int(((ext_factor - 1) * lim_range) / 2)
            _cap_i_t_lim[0] = max(0, _cap_i_t_lim[0] - lim_shift)
            _cap_i_t_lim[1] = min(self.n_t, _cap_i_t_lim[1] + lim_shift)
        return tuple(_cap_i_t_lim)

    def get_cap_res(
        self,
        thr: float = 0.05,
        ext_factor=None,
        expr: str | None = None,
        which="v_eit",
        with_t: bool = False,
        i_res: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        v_abs: bool = False,
        **kwgs,
    ) -> np.ndarray:
        """
        Extract a signal restricted to the detected CAP time window.

        Parameters
        ----------
        thr : float, optional
            Threshold used to build the CAP time limits.
        ext_factor : float | None, optional
            Optional factor used to enlarge the CAP time window.
        expr : str | None, optional
            Extra pandas-query expression applied to the CAP dataframe.
        which : str, optional
            Signal family forwarded to :meth:`get_res`.
        with_t : bool, optional
            If ``True``, also return the corresponding time vector.
        i_res, i_e, i_f, i_p : np.ndarray | int | None, optional
            Result, electrode, frequency, and pattern indices.
        v_abs : bool, optional
            If ``True``, return absolute values.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_res`.

        Returns
        -------
        np.ndarray | tuple[np.ndarray, np.ndarray]
            Signal restricted to the CAP window, optionally paired with time.
        """
        i_res = set_idxs(i_res, self.n_res)
        i_t_lim = self.get_cap_i_t_lim(
            thr=thr, ext_factor=ext_factor, i_res=i_res, expr=expr
        )
        i_t = np.arange(*i_t_lim)
        _cap_res = self.get_res(
            which=which,
            i_res=i_res,
            i_t=i_t,
            i_e=i_e,
            i_f=i_f,
            i_p=i_p,
            v_abs=v_abs,
            **kwgs,
        )
        if with_t:
            _cap_res = _cap_res, self["t"][i_t]
        return _cap_res

    def cap_duration(
        self,
        alpha=0.01,
        dv_pc=True,
        i_res=None,
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ):
        """
        Estimate CAP duration from thresholded differential signals.

        Parameters
        ----------
        alpha : float, optional
            Threshold applied to the normalized absolute differential signal.
        dv_pc : bool, optional
            If ``True``, use percentage differential voltages.
        i_res : np.ndarray | int | None, optional
            Result indices to process. Defaults to all results.
        t : np.ndarray | float | None, optional
            Evaluation times used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        **kwgs : dict
            Unused placeholder for API compatibility.

        Returns
        -------
        np.ndarray
            Duration estimate expressed in seconds.
        """
        if i_res is None:
            i_res = np.arange(self.n_res)
        __dv = abs(
            self.get_res(
                i_res=i_res,
                t=t,
                i_t=i_t,
                i_e=i_e,
                i_f=i_f,
                i_p=i_p,
                which="dv_eit",
                pc=dv_pc,
            )
        )
        __dv /= np.max(__dv, axis=0)
        return np.sum(__dv > alpha, axis=0) * self.dt

    ## numpy-like methodes
    def mean(
        self,
        which="v_eit",
        i_res=None,
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ):
        """
        Compute the mean signal across the selected results.

        Parameters
        ----------
        which : str, optional
            Signal family forwarded to :meth:`get_res`.
        i_res : np.ndarray | int | None, optional
            Result indices to include in the average.
        t : np.ndarray | float | None, optional
            Evaluation times used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_res`.

        Returns
        -------
        np.ndarray
            Mean value across the result axis.
        """
        _v = self.get_res(
            which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs
        )
        return np.mean(_v, axis=0)

    def std(
        self,
        which="v_eit",
        i_res=None,
        t=None,
        i_t: np.ndarray | int | None = None,
        i_e: np.ndarray | int | None = None,
        i_f: np.ndarray | int | None = None,
        i_p: np.ndarray | int | None = None,
        **kwgs,
    ):
        """
        Compute the standard deviation across the selected results.

        Parameters
        ----------
        which : str, optional
            Signal family forwarded to :meth:`get_res`.
        i_res : np.ndarray | int | None, optional
            Result indices to include.
        t : np.ndarray | float | None, optional
            Evaluation times used for interpolation.
        i_t, i_e, i_f, i_p : np.ndarray | int | None, optional
            Time, electrode, frequency, and pattern indices.
        **kwgs : dict
            Additional keyword arguments forwarded to :meth:`get_res`.

        Returns
        -------
        np.ndarray
            Standard deviation across the result axis.
        """
        _v = self.get_res(
            which=which, i_res=i_res, t=t, i_t=i_t, i_e=i_e, i_f=i_f, i_p=i_p, **kwgs
        )
        return np.std(_v, axis=0)


def res_list_from_labels(
    res_dnames: str | list, labels: str | list
) -> eit_results_list:
    """
    Build an :class:`eit_results_list` from result directories and labels.

    Parameters
    ----------
    res_dnames : str | list
        One directory or a list of directories containing serialized result
        files.
    labels : str | list
        One label or a list of labels used to locate ``"{label}_fem.json"``.

    Returns
    -------
    eit_results_list
        Result-list object initialized from all files found on disk.
    """
    fname_list = []
    if not isinstance(res_dnames, list):
        res_dnames = [res_dnames]
    if not isinstance(labels, list):
        labels = [labels]
    for dname in res_dnames:
        if not os.path.isdir(dname):
            print(f"results directory not found: {dname}")
        for label in labels:
            fem_res_file = f"{dname}/{label}_fem.json"
            if os.path.isfile(fem_res_file):
                fname_list += [fem_res_file]
            else:
                print(f"results file not found: {fem_res_file}")
    return eit_results_list(results=fname_list)


def sort_list_res(list_res: list):
    """
    Sort results so the longest simulation is processed first.

    Parameters
    ----------
    list_res : list
        Sequence of :class:`eit_forward_results` objects or file paths.

    Returns
    -------
    list[eit_forward_results]
        Result objects ordered with the largest ``t_sim`` first.
    """
    lr = []
    t_sim = 0
    for res_i in list_res:
        if isinstance(res_i, eit_forward_results):
            res = res_i
        else:
            res = eit_forward_results(data=res_i)
        if res["t"][-1] > t_sim:
            t_sim = res["t"][-1]
            lr = [res] + lr
        else:
            lr += [res]
    return lr
