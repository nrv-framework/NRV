import numpy as np
import matplotlib.pyplot as plt
import csv

from ...backend._file_handler import rmv_ext
from ...backend._log_interface import rise_warning
from ...utils._nrv_function import nrv_interp


####################################################################
################# generate waveform functions ######################
####################################################################


## interpolation
def interpolate(
    y: np.ndarray,
    x: np.ndarray = [],
    scale=4,
    intertype="Spline",
    bounds=(0, 0),
    save=False,
    filename="interpolate.dat",
    save_scale=False,
    kwargs_interp={},
):
    """
    :meta private:

    Parameters
    ----------
    y : np.ndarray
        _description_
    x : np.ndarray, optional
        _description_, by default []
    scale : int, optional
        _description_, by default 4
    intertype : str, optional
        _description_, by default "Spline"
    bounds : tuple, optional
        _description_, by default (0, 0)
    save : bool, optional
        _description_, by default False
    filename : str, optional
        _description_, by default "interpolate.dat"
    save_scale : bool, optional
        _description_, by default False
    kwargs_interp : dict, optional
        _description_, by default {}

    Returns
    -------
    _type_
        _description_
    """

    y_scale = []

    if len(x) == 0:
        x = [i + 1 for i in range(len(y))]

    if type(scale) == float or type(scale) == int:
        x_scale = np.linspace(x[0], x[-1], int(scale))
    elif len(scale) >= 1:
        x_scale = scale
    else:
        x_scale = np.linspace(x[0], x[-1], (1 / 100) * (len(x) - 1) + 1)

    if intertype.lower() == "spline":
        intertype = "catmull-rom"
    y_interpol = nrv_interp(x, y, kind=intertype.lower(), **kwargs_interp)
    y_scale = y_interpol(x_scale)

    if bounds[0] != bounds[1]:
        for i in range(len(y_scale)):
            if y_scale[i] < min(bounds):
                y_scale[i] = min(bounds)

            if y_scale[i] > max(bounds):
                y_scale[i] = max(bounds)

    if save:
        np.set_printoptions(threshold=40000)
        if save_scale and filename[-3:] == "csv":
            np.savetxt(
                filename, np.transpose(np.array([x_scale, y_scale])), delimiter=","
            )
        else:
            y_str = np.array2string(y_scale, separator="\n")
            file = open(filename, "w")
            file.write(y_str[1:-2])
            file.close()
        np.set_printoptions(threshold=10)
    return y_scale


def interpolate_amp(
    position: np.ndarray,
    t_sim: float = 100,
    t_end: float = None,
    dt: float = 0.005,
    intertype: str = "Spline",
    bounds: tuple[float] = (0, 0),
    save: bool = False,
    filename: str = "interpolate_part.dat",
    save_scale: bool = False,
) -> np.ndarray:
    """
    genarte a waveform from a particle position using interpolate where the position values are the output waveform amplitudes at constant sample rate

    Parameters
    ----------
    position    : array
        particle position in n dimension output waveform amplitudes at regular times
    t_sim       : float
        simulation time (ms), by default 100
    dt       	: float
        time step of the simulation (ms), by default 0.005
    intertype   : str
        type of interpolation perform, by default 'Spline'
        type possibly:

            - 'Spline'                : Cubic spline interpolation
    bounds      : tupple
        limit range of the interpolation, if both equal no limit,by default (0,0)
    save        : bool
        save or not the output in a .dat file, by default False
    filename    : str
        name of the file on wich the output should be saved, by default 'interpolate_part.dat'

    Returns
    -------
    waveform     : np.ndarray
        result of the interpolation
    """
    if t_end is None:
        t_end = t_sim

    dim = len(position)
    time_particle = np.linspace(0, t_end, dim)
    scale = int(t_end / dt)

    waveform = interpolate(
        position,
        x=time_particle,
        scale=scale,
        intertype=intertype,
        bounds=bounds,
        save=save,
        filename=filename,
        save_scale=save_scale,
    )

    if t_end < t_sim:
        dif = int((t_sim - t_end) / dt)
        waveform = np.concatenate((waveform, np.ones(dif)))
    elif t_end > t_sim:
        waveform = waveform[: int(t_sim / dt) + 1]

    return waveform


def interpolate_Npts(
    position,
    t_sim: float = 100,
    dt: float = 0.005,
    amp_start: float = 0,
    amp_stop: float = 1,
    intertype: str = "Spline",
    bounds: tuple[float] = (0, 0),
    fixed_order: bool = False,
    t_end: float = None,
    t_shift: float = None,
    save: bool = False,
    fname: str = "interpolate_2pts.dat",
    plot: bool = False,
    save_scale: bool = False,
    generatefigure: bool = True,
    strict_bounds: bool = True,
    kwargs_interp: dict = {},
    **kwargs
):
    r"""
    genarte a waveform from a particle position using interpolate where the position
    values are the coordonnate of N points which should be reached by the output waveform

    Note
    ----
    If :math:`t_{i}` and :math:`I_{i}` are the time and amplitude of the :math:`ith` point the position vector :math:`\mathcal{X}` should be:

    .. math::

        \mathcal{X} = \begin{pmatrix} t_{1} & I_{1} & t_{2} & I_{2} & ... & t_{N} & I_{N}   \end{pmatrix}

    Parameters
    ----------
    position    : np.ndarray
        particle position in 2N dimensions with the coordonnate of the N points to interpolate.
    t_sim       : float
        simulation time (ms), by default 100
    dt          : float
        time step of the simulation (ms), by default 0.005
    amp_start   : float
        amplitude at the beginning of the interpolation
    amp_stop    : float
        amplitude at the end of the interpolation
    intertype   : str
        type of interpolation perform, by default 'Spline'
        type possibly:

            - 'Spline'                : Cubic spline interpolation
            - 'linear'
    bounds      : tupple
        limit range of the interpolation, if both equal no limit, by default (0,0)
    fixed_order         :bool
        fix the order of the points to interpolate
    t_end           :float
        optionnal, if not None, time of the stimulation at which the interpollation should reach amp_stop
    t_shift         :float
        optionnal, if not None, interpolation will be shifted of this time
    save        : bool
        save or not the output in a .dat file, by default False
    fname    : str
        name of the file on wich the output should be saved, by default 'interpolate_2pts.dat'
    strict_bounds    :bool
        if True values out of bound will be set to closer bound
    kwargs_interp   : dict
        kwargs to add to the interpollation

    Returns
    -------
    waveform     : np.ndarray
        waveform generated from position
    """

    n_dim = len(position)
    n_pts = n_dim // 2
    X = np.array(
        [[position[2 * k], position[2 * k + 1]] for k in range(n_pts)], dtype=float
    )

    # if odd number of dimention the last scalar is use to set t_end
    if n_dim % 2 == 1:
        t_end = max(position[-1], 2 * n_pts * dt)
        X[:, 0] *= t_end
    elif t_end is None:
        t_end = t_sim

    for i in range(n_pts):
        if X[i, 0] < dt:
            X[i, 0] += dt
        elif X[i, 0] > t_end - (n_pts * dt):
            X[i, 0] -= n_pts * dt
    if fixed_order:
        rise_warning(NotImplemented, "fixed_order not NotImplemented")
        fixed_order = False
    if fixed_order:
        pass
    else:
        I = np.argsort(X[:, 0])
        X = X[I]
        for i in range(n_pts):
            for j in range(i + 1, n_pts):
                if X[i, 0] + dt > X[j, 0]:
                    X[j, 0] = X[j, 0] + dt

    t = np.concatenate([[0], X[:, 0], [t_end]])
    x = np.concatenate([[amp_start], X[:, 1], [amp_stop]])

    I = np.argsort(t)
    t = t[I]
    x = x[I]

    if strict_bounds:
        bds = bounds
    else:
        bds = (0, 0)

    waveform = interpolate(
        y=x,
        x=t,
        scale=int(t_end / dt) + 1,
        intertype=intertype,
        bounds=bds,
        save=False,
        save_scale=save_scale,
        **kwargs_interp
    )

    if t_shift is not None:
        dif = int(t_shift / dt)
        waveform = np.concatenate((amp_start * np.ones(dif), waveform))
        t_end += t_shift
    if t_end < t_sim:
        dif = int((t_sim - t_end) / dt)
        waveform = np.concatenate((waveform, amp_stop * np.ones(dif)))
    elif t_end > t_sim:
        waveform = waveform[: int(t_sim / dt) + 1]
    if save or plot:
        T = np.linspace(0, t_sim, len(waveform))
        if generatefigure:
            plt.figure()
        plt.plot(T, waveform)
        plt.scatter(t, x)
        if save:
            plt.savefig(fname)
    return waveform


####################################################################
########################### savers #################################
####################################################################


def cost_position_saver(data, file_name="document.csv"):
    """
    Simple saver which can be used in a cost_function to save the cost
    and position in a .csv file (see .Optim.cost_function)

    Parameters
    ----------
    data        : dict
        dict containing the keys 'cost' and 'position'
    file_name:
        name of the saving file.
        NB: if missing, extension ".csv" will be add at the end of the file
    """
    save = [str(data["cost"])]
    position = data["position"]
    fname = rmv_ext(file_name) + ".csv"
    dim = len(position)
    for i in range(dim):
        save += [position[i]]
    with open(fname, "a", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(save)
