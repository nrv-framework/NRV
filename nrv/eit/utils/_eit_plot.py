import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from pandas import DataFrame
import seaborn as sns

from ..results import eit_results_list

from ...backend import load_any
from ...fmod import CUFF_MP_electrode
from ...ui import load_nerve
from ...utils import sci_round, get_MRG_parameters

eit_fig_ppt = {
    8: {
        "fig_dim": (3, 3),
        "i_plots": [[0, 1], [0, 2], [1, 2], [2, 2], [2, 1], [2, 0], [1, 0], [0, 0]],
        "i_center": (1, 1),
    },
    12: {
        "fig_dim": (5, 5),
        "i_plots": [
            [0, 2],
            [0, 3],
            [1, 4],
            [2, 4],
            [3, 4],
            [4, 3],
            [4, 2],
            [4, 1],
            [3, 0],
            [2, 0],
            [1, 0],
            [0, 1],
        ],
        "i_center": (slice(1, 4), slice(1, 4)),
    },
    14: {
        "fig_dim": (10, 10),
        "i_plots": [
            [slice(0, 2), slice(4, 6)],
            [slice(0, 2), slice(6, 8)],
            [slice(1, 3), slice(8, 10)],
            [slice(3, 5), slice(8, 10)],
            [slice(5, 7), slice(8, 10)],
            [slice(7, 9), slice(8, 10)],
            [slice(8, 10), slice(6, 8)],
            [slice(8, 10), slice(4, 6)],
            [slice(8, 10), slice(2, 4)],
            [slice(7, 9), slice(0, 2)],
            [slice(5, 7), slice(0, 2)],
            [slice(3, 5), slice(0, 2)],
            [slice(1, 3), slice(0, 2)],
            [slice(0, 2), slice(2, 4)],
        ],
        "i_center": (slice(2, 8), slice(2, 8)),
    },
    16: {
        "fig_dim": (5, 5),
        "i_plots": [
            [0, 2],
            [0, 3],
            [0, 4],
            [1, 4],
            [2, 4],
            [3, 4],
            [4, 4],
            [4, 3],
            [4, 2],
            [4, 1],
            [4, 0],
            [3, 0],
            [2, 0],
            [1, 0],
            [0, 0],
            [0, 1],
        ],
        "i_center": [slice(1, 4), slice(1, 4)],
    },
}


class Figure_elec:
    """
    Helper class organizing one subplot per electrode around a central nerve view.
    """

    def __init__(
        self, n_e, fig=None, spec=None, ij_offset=(0, 0), small_fig=False, **fig_kwgs
    ):
        """
        Create an electrode-centered figure layout.

        Parameters
        ----------
        n_e : int
            Number of electrodes to display.
        fig : matplotlib.figure.Figure | None, optional
            Existing figure to populate.
        spec : matplotlib.gridspec.GridSpec | None, optional
            Existing subplot specification to reuse.
        ij_offset : tuple[int, int], optional
            Row and column offset applied when nesting the layout inside a larger
            gridspec.
        small_fig : bool, optional
            If ``True``, move titles on the bottom row slightly downward.
        **fig_kwgs : dict
            Keyword arguments used when creating a new figure.
        """
        self.n_e = n_e
        self._fig = fig
        self.spec = spec
        self.ij_offset = ij_offset
        self.small_fig = small_fig
        self.__init_figure(**fig_kwgs)

    @property
    def fig(self):
        """
        Underlying Matplotlib figure.

        Returns
        -------
        matplotlib.figure.Figure
            Figure containing the electrode subplots.
        """
        return self._fig

    @property
    def axs(self):
        """
        Axes composing the figure layout.

        Returns
        -------
        list[matplotlib.axes.Axes]
            One axis per electrode plus the central axis.
        """
        return self._axs

    def __init_figure(self, **fig_kwgs):
        """
        Build the subplot layout associated with the configured electrode count.

        Parameters
        ----------
        **fig_kwgs : dict
            Keyword arguments used when a new figure needs to be created.
        """
        assert self.n_e in eit_fig_ppt
        fig_dim, i_plots, i_center = eit_fig_ppt[self.n_e].values()
        mask = np.ones(fig_dim, dtype=bool)
        mask[*i_center] = False
        if self.spec is None:
            if self._fig is None:
                self._fig = plt.figure(**fig_kwgs)
            self.spec = self._fig.add_gridspec(*fig_dim)
        else:
            i_plots[:, 0] += self.ij_offset[0]
            i_plots[:, 1] += self.ij_offset[1]
            i_center[0] += self.ij_offset[0]
            i_center[1] += self.ij_offset[1]
        # fig, axs = plt.subplots(*fig_dim)
        self._axs = []
        for i_ in range(self.n_e):
            ax_ = self._fig.add_subplot(self.spec[*i_plots[i_]])
            if i_plots[i_][0] == fig_dim[0] - 1 and self.small_fig:
                ax_.set_title(f"E{i_}", y=-0.1)
            else:
                ax_.set_title(f"E{i_}")
            ax_.set_axis_off()

            self._axs += [ax_]
        self._axs += [self._fig.add_subplot(self.spec[*i_center])]

    def __setup_data(self, data, t=None, i_res=0, which="dv_eit"):
        """
        Normalize plotting inputs into an array/time pair.

        Parameters
        ----------
        data : eit_results_list | np.ndarray
            Source data to plot.
        t : np.ndarray | None, optional
            Time vector used when ``data`` is a raw array.
        i_res : int, optional
            Result index extracted from an :class:`eit_results_list`.
        which : str, optional
            Signal family extracted from an :class:`eit_results_list`.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Signal array and associated time vector.
        """
        if isinstance(data, eit_results_list):
            if self.n_e == data.n_e:
                _dv = data.get_res(i_res=i_res, which=which)
                _t = data.t()
            else:
                raise ValueError(
                    f"Wrong number of electrodes (figure: {self.n_e}, res_list: {data.n_e}) Data cannot be ploted"
                )
        elif isinstance(data, np.ndarray):
            if self.n_e == data.shape[-1]:
                _dv = data
                _t = t
            else:
                raise ValueError(
                    f"Wrong number of electrodes (figure: {self.n_e}, data: {data.shape[-1]}) Data cannot be ploted"
                )
        return _dv, _t

    def plot_all_elec(self, data, t=None, i_res=0, which="dv_eit", **kwgs):
        """
        Plot one signal trace per electrode on the managed figure.

        Parameters
        ----------
        data : list | eit_results_list | np.ndarray
            Data source to plot.
        t : np.ndarray | list | None, optional
            Time vector or list of time vectors used with raw arrays.
        i_res : int, optional
            Result index extracted from an :class:`eit_results_list`.
        which : str, optional
            Signal family extracted from an :class:`eit_results_list`.
        **kwgs : dict
            Additional keyword arguments forwarded to ``Axes.plot``.

        Returns
        -------
        list[matplotlib.axes.Axes]
            Managed axes.
        """
        if isinstance(data, list):
            for _i_d, _d in enumerate(data):
                if isinstance(t, list):
                    self.plot_all_elec(
                        data=_d, t=t[_i_d], i_res=i_res, which=which, **kwgs
                    )
                else:
                    self.plot_all_elec(data=_d, t=t, i_res=i_res, which=which, **kwgs)
        else:
            _dv, _t = self.__setup_data(
                data=data,
                t=t,
                i_res=i_res,
                which=which,
            )
            if _dv.ndim == 0:
                raise ValueError("Not enough dimensions. Data cannot be ploted")
            if _dv.ndim == 1:
                for i_e in range(self.n_e):
                    self.axs[i_e].plot(_t, _dv, **kwgs)
            elif _dv.ndim == 2:
                for i_e in range(self.n_e):
                    dv_i = _dv[:, i_e]
                    self.axs[i_e].plot(_t, dv_i, **kwgs)
            elif _dv.ndim == 3:
                n_plots = _dv.shape[0]
                t_i = deepcopy(_t)
                for i_p in range(n_plots):
                    if _t.ndim == 2:
                        t_i = _t[i_p]
                    for i_e in range(self.n_e):
                        dv_i = _dv[i_p, :, i_e]
                        self.axs[i_e].plot(t_i, dv_i, **kwgs)
        return self.axs

    def boxplot(self, data: DataFrame, expr="", **kwgs):
        """
        Draw one seaborn boxplot per electrode from a dataframe.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe containing at least an ``i_e`` column.
        expr : str, optional
            Optional pandas-query expression used to subset the dataframe before
            plotting.
        **kwgs : dict
            Additional keyword arguments forwarded to ``seaborn.boxplot``.

        Returns
        -------
        list[matplotlib.axes.Axes]
            Managed axes.
        """
        if "i_e" not in data:
            raise ValueError("no electrode colone in DataFrame")
        if len(expr) != 0:
            expr += " and "
        kwgs["legend"] = False
        for i_e in range(self.n_e):
            _ax = self.axs[i_e]
            _subdata = data.query(expr + f"i_e=={i_e}")
            sns.boxplot(ax=_ax, data=_subdata, **kwgs)
        return self.axs

    def snsplot(data: DataFrame, type="lineplot", expr="", **kwgs):
        """
        Placeholder for seaborn-based electrode plotting from dataframe inputs.
        """
        pass

    def fill_between_all_elec(
        self, data_1, data_2, t=None, i_res=0, which="dv_eit", **kwgs
    ):
        """
        Fill the area between two signals for each electrode axis.

        Parameters
        ----------
        data_1, data_2 : eit_results_list | np.ndarray
            Lower and upper data sources.
        t : np.ndarray | None, optional
            Time vector used with raw arrays.
        i_res : int, optional
            Result index extracted from an :class:`eit_results_list`.
        which : str, optional
            Signal family extracted from an :class:`eit_results_list`.
        **kwgs : dict
            Additional keyword arguments forwarded to ``Axes.fill_between``.

        Returns
        -------
        list[matplotlib.axes.Axes]
            Managed axes.
        """
        _dv_1, _ = self.__setup_data(
            data=data_1,
            t=t,
            i_res=i_res,
            which=which,
        )
        _dv_2, _t = self.__setup_data(
            data=data_2,
            t=t,
            i_res=i_res,
            which=which,
        )
        is_multi_t = _t.ndim > 1
        t_i = deepcopy(_t)
        for i_e in range(self.n_e):
            ax_ = self.axs[i_e]
            dv_i_1 = _dv_1[..., i_e]
            dv_i_2 = _dv_2[..., i_e]
            if is_multi_t:
                t_i = _t[0]

            if len(t.shape) < len(dv_i_1.shape):
                dv_i_1 = dv_i_1.T
                dv_i_1 = dv_i_1.T
            if len(t.shape) < len(dv_i_2.shape):
                dv_i_2 = dv_i_2.T
                dv_i_2 = dv_i_2.T
            ax_.fill_between(t_i, dv_i_1, dv_i_2, **kwgs)
        return self.axs

    def add_nerve_plot(
        self,
        data,
        add_elec=True,
        drive_pair=(0, 2),
        e_label=True,
        n_lwidth=2,
        e_lwidth=3,
        alpha_lab=1.2,
        **kwgs,
    ):
        """
        Draw the nerve cross-section and optionally the cuff electrodes in the center axis.

        Parameters
        ----------
        data : Any
            Object or path loadable with :func:`load_any`.
        add_elec : bool, optional
            If ``True``, overlay cuff electrodes.
        drive_pair : tuple[int, int], optional
            Electrode pair highlighted as the current-driving pair.
        e_label : bool, optional
            If ``True``, display electrode labels.
        n_lwidth : float, optional
            Line width used for the nerve outline.
        e_lwidth : float, optional
            Line width used for electrodes.
        alpha_lab : float, optional
            Alpha factor used for electrode labels.
        **kwgs : dict
            Additional keyword arguments forwarded to :func:`add_nerve_plot`.
        """
        return add_nerve_plot(
            axs=self.axs,
            data=data,
            add_elec=add_elec,
            drive_pair=drive_pair,
            e_label=e_label,
            n_lwidth=n_lwidth,
            e_lwidth=e_lwidth,
            alpha_lab=alpha_lab,
            **kwgs,
        )

    def color_elec(self, data, n_e, list_e, **kwgs):
        """
        Highlight a subset of electrodes on the central nerve axis.

        Parameters
        ----------
        data : Any
            Object or path loadable with :func:`load_any`.
        n_e : int
            Total number of electrodes.
        list_e : int | list[int]
            Electrode identifier or identifiers to highlight.
        **kwgs : dict
            Additional keyword arguments forwarded to :func:`color_elec`.
        """
        return color_elec(
            axs=self.axs,
            data=data,
            n_e=n_e,
            list_e=list_e,
            **kwgs,
        )

    def scale_axs(
        self,
        i_ax=-2,
        unit_x="ms",
        unit_y="V",
        e_gnd=[0],
        zerox=False,
        zeroy=False,
        has_nerve=True,
    ):
        """
        Harmonize electrode-axis limits and draw scale bars.

        Parameters
        ----------
        i_ax : int | tuple[int, int], optional
            Axis indices used to place the y and x scale bars.
        unit_x : str, optional
            Label appended to the x scale bar.
        unit_y : str, optional
            Label appended to the y scale bar.
        e_gnd : list[int], optional
            Electrodes excluded when computing common y-limits.
        zerox : bool, optional
            If ``True``, draw a horizontal zero line.
        zeroy : bool, optional
            If ``True``, draw a vertical zero line.
        has_nerve : bool, optional
            If ``True``, ignore the last axis when rescaling because it contains
            the nerve drawing.
        """
        scale_axs(
            axs=self.axs,
            i_ax=i_ax,
            unit_x=unit_x,
            unit_y=unit_y,
            e_gnd=e_gnd,
            zerox=zerox,
            zeroy=zeroy,
            has_nerve=has_nerve,
        )


def gen_fig_elec(
    n_e, fig=None, spec=None, ij_offset=(0, 0), small_fig=False, **fig_kwgs
):
    """
    Create a figure layout with one axis per electrode and one central axis.

    Parameters
    ----------
    n_e : int
        Number of electrodes.
    fig : matplotlib.figure.Figure | None, optional
        Existing figure to populate.
    spec : matplotlib.gridspec.GridSpec | None, optional
        Existing subplot specification to reuse.
    ij_offset : tuple[int, int], optional
        Row and column offset applied when nesting the layout.
    small_fig : bool, optional
        If ``True``, shift bottom titles slightly downward.
    **fig_kwgs : dict
        Keyword arguments used when creating a new figure.

    Returns
    -------
    tuple
        Figure and axes list.
    """
    assert n_e in eit_fig_ppt
    fig_dim, i_plots, i_center = eit_fig_ppt[n_e].values()
    mask = np.ones(fig_dim, dtype=bool)
    mask[*i_center] = False
    if spec is None:
        if fig is None:
            fig = plt.figure(**fig_kwgs)
        spec = fig.add_gridspec(*fig_dim)
    else:
        i_plots[:, 0] += ij_offset[0]
        i_plots[:, 1] += ij_offset[1]
        i_center[0] += ij_offset[0]
        i_center[1] += ij_offset[1]
    # fig, axs = plt.subplots(*fig_dim)
    axs = []
    for i_ in range(n_e):

        ax_ = fig.add_subplot(spec[*i_plots[i_]])
        if i_plots[i_][0] == fig_dim[0] - 1 and small_fig:
            ax_.set_title(f"E{i_}", y=-0.1)
        else:
            ax_.set_title(f"E{i_}")
        ax_.set_axis_off()

        axs += [ax_]
    axs += [fig.add_subplot(spec[*i_center])]
    return fig, axs


def plot_all_elec(
    res_list,
    t=None,
    axs=None,
    i_res=0,
    which="dv_eit",
    same_scale=True,
    labels=None,
    scale_x=True,
    **kwgs,
):
    """
    Plot one signal trace per electrode on an existing or generated layout.

    Parameters
    ----------
    res_list : eit_results_list | np.ndarray
        Data source to plot.
    t : np.ndarray | None, optional
        Time vector used with raw arrays.
    axs : list[matplotlib.axes.Axes] | None, optional
        Existing axes. When omitted, a new figure is generated.
    i_res : int, optional
        Result index extracted from an :class:`eit_results_list`.
    which : str, optional
        Signal family extracted from an :class:`eit_results_list`.
    same_scale : bool, optional
        Reserved for future scaling behavior.
    labels : Any, optional
        Reserved for future labeling behavior.
    scale_x : bool, optional
        If ``True``, set x-limits from ``0`` to ``t[-1]``.
    **kwgs : dict
        Additional keyword arguments forwarded to ``Axes.plot``.

    Returns
    -------
    tuple | list[matplotlib.axes.Axes]
        Generated figure and axes, or updated axes when ``axs`` is provided.
    """
    if isinstance(res_list, eit_results_list):
        n_e = res_list.n_e
        _dv = res_list.get_res(i_res=i_res, which=which)
        t = res_list.t()
    elif isinstance(res_list, np.ndarray):
        n_e = res_list.shape[-1]
        _dv = res_list

    is_generated = axs is None
    if is_generated:
        fig, axs = gen_fig_elec(n_e)
    for i_e in range(n_e):
        ax_ = axs[i_e]
        dv_i = _dv[..., i_e]
        if len(t.shape) < len(dv_i.shape):
            dv_i = dv_i.T
        ax_.plot(t, dv_i, **kwgs)
        if scale_x:
            ax_.set_xlim(0, t[-1])

    if is_generated:
        return fig, axs
    return axs


def fill_between_all_elec(axs, res_list_1, res_list_2, t=None, **kwgs):
    """
    Fill the area between two electrode-wise signals.

    Parameters
    ----------
    axs : list[matplotlib.axes.Axes]
        Axes to update.
    res_list_1, res_list_2 : np.ndarray
        Arrays containing the lower and upper traces.
    t : np.ndarray | None, optional
        Time vector.
    **kwgs : dict
        Additional keyword arguments forwarded to ``Axes.fill_between``.

    Returns
    -------
    list[matplotlib.axes.Axes]
        Updated axes.
    """
    if isinstance(res_list_1, np.ndarray):
        n_e = res_list_1.shape[-1]
        dv_1 = res_list_1
        dv_2 = res_list_2

    for i_e in range(n_e):
        ax_ = axs[i_e]
        dv_i_1 = dv_1[..., i_e]
        dv_i_2 = dv_2[..., i_e]
        if len(t.shape) < len(dv_i_1.shape):
            dv_i_1 = dv_i_1.T
            dv_i_1 = dv_i_1.T
        if len(t.shape) < len(dv_i_2.shape):
            dv_i_2 = dv_i_2.T
            dv_i_2 = dv_i_2.T
        ax_.fill_between(t, dv_i_1, dv_i_2, **kwgs)
    return axs


def add_nerve_plot(
    axs,
    data,
    add_elec=True,
    drive_pair=(0, 2),
    e_label=True,
    n_lwidth=2,
    e_lwidth=3,
    alpha_lab=1.2,
    **kwgs,
):
    """
    Draw a nerve cross-section and optionally the electrode geometry.

    Parameters
    ----------
    axs : list[matplotlib.axes.Axes]
        Axes list whose last axis is used for the nerve drawing.
    data : Any
        Object or path loadable with :func:`load_any`.
    add_elec : bool, optional
        If ``True``, overlay cuff electrodes.
    drive_pair : tuple[int, int], optional
        Electrode pair highlighted as the current-driving pair.
    e_label : bool, optional
        If ``True``, display electrode labels.
    n_lwidth : float, optional
        Line width of the nerve drawing.
    e_lwidth : float, optional
        Line width of the electrode drawing.
    alpha_lab : float, optional
        Alpha factor used for electrode labels.
    **kwgs : dict
        Additional keyword arguments reserved for future use.

    Returns
    -------
    list[matplotlib.axes.Axes]
        Updated axes.
    """
    nerve = load_any(data)
    nerve.plot(axs[-1], linewidth=n_lwidth)
    axs[-1].set_axis_off()
    if add_elec:
        if "n_e" not in kwgs:
            n_e = len(axs) - 1
        else:
            n_e = kwgs.pop("n_e")
        w_elec = 0.5 * np.pi * nerve.D / n_e
        elec = CUFF_MP_electrode(
            N_contact=n_e,
            x_center=100,
            contact_width=w_elec,
            contact_length=100,
            insulator=False,
        )
        elec.plot(
            axs[-1],
            nerve_d=nerve.D,
            color="k",
            e_label=e_label,
            linewidth=e_lwidth,
            alpha_lab=alpha_lab,
        )
        elec.plot(
            axs[-1],
            nerve_d=nerve.D,
            list_e=drive_pair[0],
            color="r",
            e_label=False,
            linewidth=e_lwidth,
        )
        elec.plot(
            axs[-1],
            nerve_d=nerve.D,
            list_e=drive_pair[1],
            color="b",
            e_label=False,
            linewidth=e_lwidth,
        )
    del nerve
    return axs


def color_elec(axs, data, n_e, list_e, **kwgs):
    """
    Highlight selected cuff electrodes on the nerve plot.

    Parameters
    ----------
    axs : list[matplotlib.axes.Axes]
        Axes list whose last axis contains the nerve drawing.
    data : Any
        Object or path loadable with :func:`load_any`.
    n_e : int
        Total number of electrodes.
    list_e : int | list[int]
        Electrode identifier or identifiers to highlight.
    **kwgs : dict
        Additional keyword arguments forwarded to the electrode plotter.

    Returns
    -------
    list[matplotlib.axes.Axes]
        Updated axes.
    """
    nerve = load_any(data)
    w_elec = 0.5 * np.pi * nerve.D / n_e
    elec = CUFF_MP_electrode(
        N_contact=n_e,
        x_center=100,
        contact_width=w_elec,
        contact_length=100,
        insulator=False,
    )
    elec.plot(axs[-1], nerve_d=nerve.D, list_e=list_e, **kwgs)
    del nerve
    return axs


def scale_axs(
    axs,
    i_ax=-2,
    unit_x="ms",
    unit_y="V",
    e_gnd=[0],
    zerox=False,
    zeroy=False,
    has_nerve=True,
):
    """
    Harmonize y-limits across electrode axes and add scale bars.

    Parameters
    ----------
    axs : list[matplotlib.axes.Axes]
        Axes to update.
    i_ax : int | tuple[int, int], optional
        Axis indices used to draw the y and x scale bars.
    unit_x : str, optional
        Label appended to the x scale bar.
    unit_y : str, optional
        Label appended to the y scale bar.
    e_gnd : list[int], optional
        Electrodes excluded from the y-limit aggregation.
    zerox : bool, optional
        If ``True``, draw a horizontal zero line.
    zeroy : bool, optional
        If ``True``, draw a vertical zero line.
    has_nerve : bool, optional
        If ``True``, ignore the last axis when rescaling.

    Returns
    -------
    list[matplotlib.axes.Axes]
        Updated axes.
    """
    if has_nerve:
        __axs = axs[:-1]
    else:
        __axs = axs
    min_y, max_y = 0, 0
    for i_e, ax_ in enumerate(__axs):
        if i_e not in e_gnd:
            _min_y, _max_y = ax_.get_ylim()
            min_y = min(_min_y, min_y)
            max_y = max(_max_y, max_y)

    for ax_ in __axs:
        ax_.set_ylim(min_y, max_y)
        if zerox:
            _min_x, _max_x = ax_.get_xlim()
            ax_.plot([_min_x, _max_x], [0, 0], "k")
        if zeroy:
            ax_.plot([0, 0], [_min_y, _max_y], "k")

    if i_ax is None:
        return axs
    if np.iterable(i_ax):
        y_i_ax = i_ax[0]
        t_i_ax = i_ax[1]
    else:
        y_i_ax, t_i_ax = i_ax, i_ax

    # Adding y scale
    ax_y = axs[y_i_ax]
    ax_t = axs[t_i_ax]

    _min_y, _max_y = ax_.get_ylim()
    Dy = _max_y - _min_y
    _min_t, _max_t = ax_.get_xlim()
    Dt = _max_t - _min_t
    scale_t = sci_round(0.2 * (Dt), 1)
    if scale_t >= 1:
        scale_t = int(scale_t)
    x_st = [0.1 * (Dt), 0.1 * (Dt) + scale_t]
    y_st = [_min_y + 0.1 * Dy, _min_y + 0.1 * Dy]
    ax_t.plot(x_st, y_st, color="k", linewidth=3)
    ax_t.text(
        x_st[0],
        y_st[0] + 0.01 * Dy,
        f"{scale_t}{unit_x}",
        ha="left",
        va="bottom",
        style="italic",
    )

    # Adding t(x) scale
    scale_y = sci_round(0.2 * Dy, 1)
    if scale_y >= 1:
        scale_y = int(scale_y)
    x_sy = [_min_t + 0.1 * (Dt), _min_t + 0.1 * (Dt)]
    y_sy = [_min_y + 0.2 * Dy, _min_y + 0.2 * Dy + scale_y]

    ax_y.plot(x_sy, y_sy, color="k", linewidth=3)
    ax_y.text(
        x_sy[0] + 0.05 * Dt,
        np.mean(y_sy),
        f"{scale_y}{unit_y}",
        ha="left",
        va="center",
        style="italic",
    )

    return axs


def plot_nerve_nor(fname, l_elec, x_rec, fasc_ID="1"):
    """
    Plot node-of-Ranvier alignment relative to one electrode window.

    Parameters
    ----------
    fname : str
        Path to the serialized nerve description.
    l_elec : float
        Electrode length.
    x_rec : float
        Electrode center position.
    fasc_ID : str | int, optional
        Fascicle identifier to inspect.

    Returns
    -------
    tuple
        Matplotlib figure and axes.
    """
    fasc_ID = str(fasc_ID)
    x_min, x_max = x_rec - l_elec / 2, x_rec + l_elec / 2
    fasc = load_nerve(fname).fascicles[fasc_ID]
    fig, axs = plt.subplots(3)
    fasc.plot_x(axs[0])
    del fasc

    fasc = load_nerve(fname).fascicles[fasc_ID]
    fasc.NoR_relative_position *= 0
    fasc.plot_x(axs[2])
    deltaxs = get_MRG_parameters(fasc.axons_diameter)[5]
    for i, dx in enumerate(deltaxs):
        axs[2].plot([0, dx], [i, i])
    del fasc
    axs[2].axvline(x_min, color="red")
    axs[2].axvline(x_max, color="red")

    fasc1 = load_nerve(fname).fascicles[fasc_ID]
    axs[0].set_xlim(x_min, x_max)
    deltaxs = get_MRG_parameters(fasc1.axons_diameter)[5]
    fasc1.define_length(x_max - x_min)
    l1 = fasc1.NoR_relative_position * deltaxs
    x_l = np.mod((l1 - x_min), deltaxs)
    fasc1.NoR_relative_position = x_l / deltaxs
    fasc1.plot_x(
        axs[1],
    )
    return fig, axs
