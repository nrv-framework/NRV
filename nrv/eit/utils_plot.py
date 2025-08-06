import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from nrv import load_any, load_nerve, CUFF_MP_electrode, sci_round, get_MRG_parameters
from pandas import DataFrame
import seaborn as sns
from ._eit_results_list import eit_results_list





class Figure_elec():
    def __init__(self, n_e, fig=None, spec=None, ij_offset=(0,0), small_fig=False, **fig_kwgs):
        self.n_e = n_e
        self._fig = fig
        self.spec = spec
        self.ij_offset = ij_offset
        self.small_fig = small_fig
        self.__init_figure(**fig_kwgs)

    @property
    def fig(self):
        return self._fig

    @property
    def axs(self):
        return self._axs

    def __init_figure(self, **fig_kwgs):
        if self.n_e == 8:
            fig_dim = (3, 3)
            i_plots = np.array([[0,1], [0,2], [1,2], [2,2], [2,1], [2,0], [1,0], [0,0]])
            i_center = (1,1)
        elif self.n_e == 12:
            fig_dim = (4, 4)
            i_plots = np.array([[0,1], [0,2], [0,3], [1,3], [2,3], [3,3], [3,2], [3,1], [3,0], [1,0], [0,0]])
            idxs = np.arange(2)+1
            i_center = (slice(1,3),slice(1,3))
        elif self.n_e == 16:
            fig_dim = (5, 5)
            i_plots = np.array([ [0,2], [0,3], [0,4], [1,4], [2,4], [3,4], [4,4], [4,3], [4,2], [4,1], [4,0], [3,0], [2,0], [1,0], [0,0], [0,1]])
            i_center = (slice(1,4),slice(1,4))

        mask = np.ones(fig_dim, dtype=bool)
        mask[*i_center] = False
        if self.spec is None:
            if self._fig is None:
                self._fig = plt.figure(**fig_kwgs)
            self.spec = self._fig.add_gridspec(*fig_dim)
        else:
            i_plots[:,0] += self.ij_offset[0]
            i_plots[:,1] += self.ij_offset[1]
            i_center[0] += self.ij_offset[0]
            i_center[1] += self.ij_offset[1]
        # fig, axs = plt.subplots(*fig_dim)
        self._axs = []
        for i_ in range(self.n_e):
            ax_ = self._fig.add_subplot(self.spec[*i_plots[i_]])
            if i_plots[i_][0]==fig_dim[0]-1 and self.small_fig:
                ax_.set_title(f"E{i_}", y=-.1)
            else:
                ax_.set_title(f"E{i_}")
            ax_.set_axis_off()

            self._axs += [ax_]
        self._axs += [self._fig.add_subplot(self.spec[*i_center])]

    def __setup_data(self, data, t=None, i_res=0, which="dv_eit"):
        if isinstance(data, eit_results_list):
            if self.n_e == data.n_e:
                _dv = data.get_res(i_res=i_res, which=which)
                _t = data.t()
            else:
                raise ValueError(f"Wrong number of electrodes (figure: {self.n_e}, res_list: {data.n_e}) Data cannot be ploted")
        elif isinstance(data, np.ndarray):
            if self.n_e == data.shape[-1]:
                _dv = data
                _t = t
            else:
                raise ValueError(f"Wrong number of electrodes (figure: {self.n_e}, data: {data.shape[-1]}) Data cannot be ploted")
        return _dv, _t

    def plot_all_elec(self, data, t=None, i_res=0, which="dv_eit", **kwgs):
        if isinstance(data, list):
            for _i_d, _d in enumerate(data):
                if isinstance(t, list):
                    self.plot_all_elec(data=_d, t=t[_i_d],i_res=i_res,which=which, **kwgs)
                else:
                    self.plot_all_elec(data=_d, t=t,i_res=i_res,which=which, **kwgs)
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
                    self.axs[i_e].plot(_t, _dv,**kwgs)
            elif _dv.ndim == 2:
                for i_e in range(self.n_e):
                    dv_i = _dv[:,i_e]
                    self.axs[i_e].plot(_t, dv_i,**kwgs)
            elif _dv.ndim == 3:
                n_plots = _dv.shape[0]
                t_i = deepcopy(_t)
                for i_p in range(n_plots):
                    if _t.ndim == 2:
                        t_i = _t[i_p]
                    for i_e in range(self.n_e):
                        dv_i = _dv[i_p,:,i_e]
                        self.axs[i_e].plot(t_i, dv_i,**kwgs)
        return self.axs
    
    def boxplot(self, data:DataFrame, expr="", **kwgs):
        if not 'i_e' in data:
            raise ValueError("no electrode colone in DataFrame")
        if len(expr) != 0:
            expr += " and "
        kwgs["legend"]=False
        for i_e in range(self.n_e):
            _ax=self.axs[i_e]
            _subdata = data.query(expr+f"i_e=={i_e}")
            p = sns.boxplot(ax=_ax, data=_subdata, **kwgs)
        return self.axs

    def snsplot(data:DataFrame, type="lineplot", expr="", **kwgs):
        pass


    def fill_between_all_elec(self, data_1, data_2, t=None, i_res=0, which="dv_eit", **kwgs):
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
            dv_i_1 = _dv_1[...,i_e]
            dv_i_2 = _dv_2[...,i_e]
            if is_multi_t:
                t_i = _t[0]

            if len(t.shape)<len(dv_i_1.shape):
                dv_i_1 = dv_i_1.T
                dv_i_1 = dv_i_1.T
            if len(t.shape)<len(dv_i_2.shape):
                dv_i_2 = dv_i_2.T
                dv_i_2 = dv_i_2.T
            ax_.fill_between(t_i,dv_i_1,dv_i_2, **kwgs)
        return self.axs


    def add_nerve_plot(self, data, add_elec=True, drive_pair=(0,2), e_label=True, n_lwidth=2, e_lwidth=3,**kwgs):
        nerve = load_any(data)
        nerve.plot(self.axs[-1], linewidth=n_lwidth)
        self.axs[-1].set_axis_off()
        if add_elec:
            if "n_e" not in kwgs:
                n_e = len(self.axs)-1
            else:
                n_e = kwgs.pop("n_e")
            w_elec= 0.5 * np.pi * nerve.D / n_e
            elec = CUFF_MP_electrode(N_contact=n_e, x_center=100,contact_width=w_elec, contact_length=100, insulator=False)
            elec.plot(self.axs[-1], nerve_d=nerve.D, color="k", e_label=e_label, linewidth=e_lwidth)
            if drive_pair is not None:
                elec.plot(self.axs[-1], nerve_d=nerve.D, list_e=drive_pair[0],color="r", e_label=False, linewidth=e_lwidth)
                elec.plot(self.axs[-1], nerve_d=nerve.D, list_e=drive_pair[1],color="b", e_label=False, linewidth=e_lwidth)
        del nerve
        return self.axs

    def color_elec(self, data, n_e, list_e, **kwgs):
        nerve = load_any(data)
        w_elec= 0.5 * np.pi * nerve.D / n_e
        elec = CUFF_MP_electrode(N_contact=n_e, x_center=100,contact_width=w_elec, contact_length=100, insulator=False)
        elec.plot(self.axs[-1], nerve_d=nerve.D, list_e=list_e,**kwgs)
        del nerve
        return self.axs

    def scale_axs(self, i_ax=-2, unit_x="ms", unit_y="V", e_gnd=[0], zerox=False, zeroy=False, has_nerve=True):
        if has_nerve:
            __axs = self.axs[:-1]
        else:
            __axs = self.axs
        min_y, max_y = 0, 0
        for i_e, ax_ in enumerate(__axs):
            if i_e not in e_gnd:
                _min_y, _max_y = ax_.get_ylim()
                min_y = min(_min_y,min_y)
                max_y = max(_max_y,max_y)

        for ax_ in __axs:
            ax_.set_ylim(min_y, max_y)
            if zerox:
                _min_x, _max_x = ax_.get_xlim()
                ax_.plot([_min_x, _max_x], [0,0],"k")
            if zeroy:
                ax_.plot([0,0], [_min_y, _max_y],"k")

        if np.iterable(i_ax):
            y_i_ax = i_ax[0]
            t_i_ax = i_ax[1]
        else:
            y_i_ax, t_i_ax = i_ax, i_ax
        if i_ax is None:
            return self.axs
        # Adding y scale
        ax_y = self.axs[y_i_ax]
        ax_t = self.axs[t_i_ax]

        _min_y, _max_y = ax_.get_ylim()
        Dy =_max_y-_min_y
        _min_t, _max_t = ax_.get_xlim()
        Dt =_max_t-_min_t
        scale_t = sci_round(0.2*(Dt),1)
        if scale_t>=1:
            scale_t = int(scale_t)
        x_st = [0.1*(Dt), 0.1*(Dt)+scale_t]
        y_st = [_min_y+0.1*Dy, _min_y+0.1*Dy]
        ax_t.plot(x_st, y_st, color="k", linewidth=3)
        ax_t.text(x_st[0], y_st[0]+0.01*Dy, f"{scale_t}{unit_x}", ha="left", va="bottom",style="italic")

        # Adding t(x) scale
        scale_y = sci_round(0.2*Dy,1)
        if scale_y>=1:
            scale_y = int(scale_y)
        x_sy = [_min_t+0.1*(Dt), _min_t+0.1*(Dt)]
        y_sy = [_min_y+0.2*Dy, _min_y+0.2*Dy+scale_y]

        ax_y.plot(x_sy, y_sy, color="k", linewidth=3)
        ax_y.text(x_sy[0]+0.05*Dt, np.mean(y_sy), f"{scale_y}{unit_y}", ha="left", va="center",style="italic")

        return self.axs



def gen_fig_elec(n_e, fig=None, spec=None, ij_offset=(0,0), small_fig=False, **fig_kwgs):
    if n_e == 8:
        fig_dim = (3, 3)
        i_plots = np.array([[0,1], [0,2], [1,2], [2,2], [2,1], [2,0], [1,0], [0,0]])
        i_center = (1,1)
    elif n_e == 12:
        fig_dim = (4, 4)
        i_plots = np.array([[0,1], [0,2], [0,3], [1,3], [2,3], [3,3], [3,2], [3,1], [3,0], [1,0], [0,0]])
        idxs = np.arange(2)+1
        i_center = (idxs[:,np.newaxis],idxs)
    elif n_e == 16:
        fig_dim = (5, 5)
        i_plots = np.array([ [0,2], [0,3], [0,4], [1,4], [2,4], [3,4], [4,4], [4,3], [4,2], [4,1], [4,0], [3,0], [2,0], [1,0], [0,0], [0,1]])
        # idxs = np.arange(3)+1
        # i_center = (idxs[:,np.newaxis],idxs)
        i_center = (slice(1,4),slice(1,4))

    mask = np.ones(fig_dim, dtype=bool)
    mask[*i_center] = False
    if spec is None:
        if fig is None:
            fig = plt.figure(**fig_kwgs)
        spec = fig.add_gridspec(*fig_dim)
    else:
        i_plots[:,0] += ij_offset[0]
        i_plots[:,1] += ij_offset[1]
        i_center[0] += ij_offset[0]
        i_center[1] += ij_offset[1]
    # fig, axs = plt.subplots(*fig_dim)
    axs = []
    for i_ in range(n_e):

        ax_ = fig.add_subplot(spec[*i_plots[i_]])
        if i_plots[i_][0]==fig_dim[0]-1 and small_fig:
            ax_.set_title(f"E{i_}", y=-.1)
        else:
            ax_.set_title(f"E{i_}")
        ax_.set_axis_off()

        axs += [ax_]
    axs += [fig.add_subplot(spec[*i_center])]
    return fig, axs

def plot_all_elec(res_list, t=None, axs=None, i_res=0, which="dv_eit", same_scale=True, labels=None,**kwgs):
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
        dv_i = _dv[...,i_e]
        if len(t.shape)<len(dv_i.shape):
            dv_i = dv_i.T
        ax_.plot(t, dv_i,**kwgs)
        ax_.set_xlim(0, t[-1])

    if is_generated:
        return fig, axs
    return axs


def fill_between_all_elec(axs, res_list_1, res_list_2, t=None,**kwgs):
    if isinstance(res_list_1, np.ndarray):
        n_e = res_list_1.shape[-1]
        dv_1 = res_list_1
        dv_2 = res_list_2

    for i_e in range(n_e):
        ax_ = axs[i_e]
        dv_i_1 = dv_1[...,i_e]
        dv_i_2 = dv_2[...,i_e]
        if len(t.shape)<len(dv_i_1.shape):
            dv_i_1 = dv_i_1.T
            dv_i_1 = dv_i_1.T
        if len(t.shape)<len(dv_i_2.shape):
            dv_i_2 = dv_i_2.T
            dv_i_2 = dv_i_2.T
        ax_.fill_between(t,dv_i_1,dv_i_2, **kwgs)
    return axs


def add_nerve_plot(axs, data, add_elec=True, drive_pair=(0,2), e_label=True, n_lwidth=2, e_lwidth=3,**kwgs):
    nerve = load_any(data)
    nerve.plot(axs[-1], linewidth=n_lwidth)
    axs[-1].set_axis_off()
    if add_elec:
        if "n_e" not in kwgs:
            n_e = len(axs)-1
        else:
            n_e = kwgs.pop("n_e")
        w_elec= 0.5 * np.pi * nerve.D / n_e
        elec = CUFF_MP_electrode(N_contact=n_e, x_center=100,contact_width=w_elec, contact_length=100, insulator=False)
        elec.plot(axs[-1], nerve_d=nerve.D, color="k", e_label=e_label, linewidth=e_lwidth)
        elec.plot(axs[-1], nerve_d=nerve.D, list_e=drive_pair[0],color="r", e_label=False, linewidth=e_lwidth)
        elec.plot(axs[-1], nerve_d=nerve.D, list_e=drive_pair[1],color="b", e_label=False, linewidth=e_lwidth)
    del nerve
    return axs

def color_elec(axs, data, n_e, list_e, **kwgs):
    nerve = load_any(data)
    w_elec= 0.5 * np.pi * nerve.D / n_e
    elec = CUFF_MP_electrode(N_contact=n_e, x_center=100,contact_width=w_elec, contact_length=100, insulator=False)
    elec.plot(axs[-1], nerve_d=nerve.D, list_e=list_e,**kwgs)
    del nerve
    return axs

def scale_axs(axs, i_ax=-2, unit_x="ms", unit_y="V", e_gnd=[0], zerox=False, zeroy=False, has_nerve=True):
    if has_nerve:
        __axs = axs[:-1]
    else:
        __axs = axs
    min_y, max_y = 0, 0
    for i_e, ax_ in enumerate(__axs):
        if i_e not in e_gnd:
            _min_y, _max_y = ax_.get_ylim()
            min_y = min(_min_y,min_y)
            max_y = max(_max_y,max_y)

    for ax_ in __axs:
        ax_.set_ylim(min_y, max_y)
        if zerox:
            _min_x, _max_x = ax_.get_xlim()
            ax_.plot([_min_x, _max_x], [0,0],"k")
        if zeroy:
            ax_.plot([0,0], [_min_y, _max_y],"k")

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
    Dy =_max_y-_min_y
    _min_t, _max_t = ax_.get_xlim()
    Dt =_max_t-_min_t
    scale_t = sci_round(0.2*(Dt),1)
    if scale_t>=1:
        scale_t = int(scale_t)
    x_st = [0.1*(Dt), 0.1*(Dt)+scale_t]
    y_st = [_min_y+0.1*Dy, _min_y+0.1*Dy]
    ax_t.plot(x_st, y_st, color="k", linewidth=3)
    ax_t.text(x_st[0], y_st[0]+0.01*Dy, f"{scale_t}{unit_x}", ha="left", va="bottom",style="italic")

    # Adding t(x) scale
    scale_y = sci_round(0.2*Dy,1)
    if scale_y>=1:
        scale_y = int(scale_y)
    x_sy = [_min_t+0.1*(Dt), _min_t+0.1*(Dt)]
    y_sy = [_min_y+0.2*Dy, _min_y+0.2*Dy+scale_y]

    ax_y.plot(x_sy, y_sy, color="k", linewidth=3)
    ax_y.text(x_sy[0]+0.05*Dt, np.mean(y_sy), f"{scale_y}{unit_y}", ha="left", va="center",style="italic")

    return axs

def plot_nerve_nor(fname, l_elec, x_rec, fasc_ID="1"):
    fasc_ID = str(fasc_ID)
    x_min, x_max = x_rec-l_elec/2, x_rec+l_elec/2
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
    fasc1.define_length(x_max-x_min)
    l1 = fasc1.NoR_relative_position*deltaxs
    x_l = np.mod((l1 - x_min),deltaxs)
    fasc1.NoR_relative_position = x_l / deltaxs
    fasc1.plot_x(axs[1],)
    return fig, axs