import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d
import scipy.signal as sig

from ...backend.log_interface import rise_warning
from ...utils.nrv_function import nrv_interp


####################################################################
################# generate_waveform functions ######################
####################################################################

## interpolation
def interpolate(y, x=[], scale=4, intertype="Spline", bounds=(0, 0),
    save=False, filename="interpolate.dat", save_scale=False, kwargs_interp={}):
    y_scale = []

    if len(x) == 0:
        x = [i+1 for i in range(len(y))]

    if type(scale) == float or type(scale) == int:
        x_scale = np.linspace(x[0],x[-1],int(scale))
    elif len(scale) >= 1:
        x_scale = scale
    else:
        x_scale = np.linspace(x[0],x[-1],(1/100)*(len(x)-1)+1)

    if intertype.lower() == "spline":
        intertype =  "catmull-rom"
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
        if save_scale and filename[-3:]=='csv':
            np.savetxt(filename, np.transpose(np.array([x_scale,y_scale])), delimiter=",")
        else:
            y_str = np.array2string(y_scale, separator='\n')
            file = open(filename,"w")
            file.write(y_str[1:-2])
            file.close()
        np.set_printoptions(threshold=10)
    return y_scale


def interpolate_part(position, t_sim=100, t_end=None, dt=0.005, intertype="Spline", bounds=(0, 0), save=False,
    filename="interpolate_part.dat", save_scale=False):

    """
    genarte a waveform from a particle position using interpolate where the position
    values are the output waveform amplitudes at regular times

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
                'Spline'                : Cubic spline interpolation
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
    scale = int(t_end/dt)

    waveform = interpolate(position, x=time_particle, scale=scale, intertype=intertype, bounds=bounds,
        save=save, filename=filename, save_scale=save_scale)

    if t_end < t_sim:
        dif = int((t_sim - t_end)/dt)
        waveform = np.concatenate((waveform, np.ones(dif)))
    elif t_end > t_sim:
        waveform = waveform[:int(t_sim/dt)+1]

    return waveform



## 2nd order filter response

def second_order_response(position, t_sim=100, dt=0.005, amplitude=1, save=False,
    filename="tesecond_order_responsest.dat"):
    """
    genarte a waveform from a particle position using interpolate where the position
    values are the coordonnate of two points where 

    Parameters
    ----------
    position    : array
        particle position in 2 dimensions, the first one is the filter half pseudo-perdiod
        the second is the 1st overflow fraction
    t_sim       : float
        simulation time (ms), by default 100
    dt          : float
        time step of the simulation (ms), by default 0.005
    amplitude   :float
        final amplitude of the waveform.
    save        : bool
        save or not the output in a .dat file, by default False
    filename    : str
        name of the file on wich the output should be saved, by default 'second_order_response.dat'

    Returns
    -------
    waveform     : np.ndarray
        waveform generated from position
    """
    T0, D= position[0],position[1]
    if D > 0: 
        w0 = np.pi/T0
        m = (1/(1+(np.pi/np.log(D))**2))**0.5
        wn = w0 / ((1-m**2)**0.5)
    else:
        wn = 1
        m = T0/(6*wn)
    G = 1.
    # KHFC parameters
    waveform_duration = 100

    # waveform computation
    H_waveform = sig.lti([G], [1/wn**2, 2*m/wn, 1])
    T = np.linspace(0,waveform_duration, num=int(t_sim/dt))
    t, waveform = sig.step(H_waveform, T=T)

    waveform = np.append(waveform, G)
    waveform *= amplitude

    if save:
        fig = plt.figure()
        fig.plot(waveform, T)
        fig.suptitle("Waveform gernrated using second order filter response")
        plt.savefig(filename)

    return waveform

def interpolate_2pts(position, t_sim=100, dt=0.005, amp_start=0, amp_stop=1, intertype="Spline",
    bounds=(0, 0), fixed_order=False, t_end=None, save=False, fname="interpolate_2pts.dat", 
    save_scale=False, **kwargs):

    """
    genarte a waveform from a particle position using interpolate where the position
    values are the coordonnate of two points which should be reached by the output waveform

    Parameters
    ----------
    position    : array
        particle position in 4 dimensions where the first two are the coordonate of the first point
        the last two are the coordonate of the second, syntax: X = (time, amplitude)
    t_sim       : float
        simulation time (ms), by default 100
    dt          : float
        time step of the simulation (ms), by default 0.005
    intertype   : str
        type of interpolation perform, by default 'Spline'
        type possibly:
                'Spline'                : Cubic spline interpolation
    bounds      : tupple
        limit range of the interpolation, if both equal no limit, by default (0,0)
    save        : bool
        save or not the output in a .dat file, by default False
    filename    : str
        name of the file on wich the output should be saved, by default 'interpolate_2pts.dat'

    Returns
    -------
    waveform     : np.ndarray
        waveform generated from position
    """
    rise_warning("DeprecationWarning: use interpolate_Npts rather than interpolate_2pts")
    return interpolate_Npts(
        position=position,
        t_sim=t_sim,
        dt=dt,
        amp_start=amp_start,
        amp_stop=amp_stop,
        intertype=intertype,
        bounds=bounds,
        fixed_order=fixed_order,
        t_end=t_end,
        save=save,
        fname=fname,
        save_scale=save_scale,
        **kwargs,
    )


def interpolate_Npts(position, t_sim=100, dt=0.005, amp_start=0, amp_stop=1, intertype="Spline",
    bounds=(0, 0), fixed_order=False, t_end=None, save=False, fname="interpolate_2pts.dat", 
    plot=False, save_scale=False, generatefigure=True, strict_bounds=True, kwargs_interp={}, **kwargs):

    """
    genarte a waveform from a particle position using interpolate where the position
    values are the coordonnate of two points which should be reached by the output waveform

    Parameters
    ----------
    position    : array
        particle position in 4 dimensions where the first two are the coordonate of the first point
        the last two are the coordonate of the second, syntax: X = (time, amplitude)
    t_sim       : float
        simulation time (ms), by default 100
    dt          : float
        time step of the simulation (ms), by default 0.005
    intertype   : str
        type of interpolation perform, by default 'Spline'
        type possibly:
                'Spline'                : Cubic spline interpolation
    bounds      : tupple
        limit range of the interpolation, if both equal no limit, by default (0,0)
    save        : bool
        save or not the output in a .dat file, by default False
    filename    : str
        name of the file on wich the output should be saved, by default 'interpolate_2pts.dat'
    strict_bounds    :bool
        if True values out of bound will be set to closer bound

    Returns
    -------
    waveform     : np.ndarray
        waveform generated from position
    """

    n_dim = len(position)
    n_pts = n_dim//2
    X = np.array([[position[2*k], position[2*k+1]] for k in range(n_pts)], dtype=float)

    # if odd number of dimention the last scalar is use to set t_end
    if n_dim%2 == 1:
        t_end = max(position[-1], (n_pts + 2) * dt)
        X[:, 0] *= t_end
    elif t_end is None:
        t_end = t_sim


    for i in range(n_pts):
        if X[i, 0] < dt:
            X[i, 0] += dt
        elif X[i, 0] > t_end-(n_pts*dt):
            X[i, 0] -= n_pts*dt
    if fixed_order:
        rise_warning(NotImplemented, "fixed_order not NotImplemented")
        fixed_order=False
    if fixed_order:
        pass
    else:
        I = np.argsort(X[:,0])
        X = X[I]
        for i in range(n_pts):
            for j in range(i+1, n_pts):
                if X[i,0] + dt > X[j,0]:
                    X[j,0] = X[j,0] + dt

    t = np.concatenate([[0], X[:,0], [t_end]])
    x = np.concatenate([[amp_start], X[:,1], [amp_stop]])

    I = np.argsort(t)
    t = t[I]
    x = x[I]
    mask = [True for _ in t]
    """for i in range(len(t)-1):
        if mask[i]:
            for j in range(i+1, len(t)):
                if t[i]+dt > t[j]:
                    mask[j] = False"""
    t = t[mask]
    x = x[mask]
    if strict_bounds:
        bds = bounds
    else:
        bds = (0,0)

    waveform = interpolate(y=x, x=t, scale=int(t_end/dt)+1, intertype=intertype, bounds=bds,
        save=False, save_scale=save_scale, **kwargs_interp)

    if t_end < t_sim:
        dif = int((t_sim - t_end)/dt)
        waveform = np.concatenate((waveform, amp_stop * np.ones(dif)))
    elif t_end > t_sim:
        waveform = waveform[:int(t_sim/dt)+1]
    if save or plot:
        T = np.linspace(0, t_sim, len(waveform))
        if generatefigure:
            plt.figure()
        plt.plot(T, waveform)
        plt.scatter(t,x)
        if save:
            plt.savefig(fname)
    return waveform
