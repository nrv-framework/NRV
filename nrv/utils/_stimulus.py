"""
NRV-:class:`.stimulus` handling.
"""

import faulthandler

import numpy as np

from ..backend._log_interface import pass_info, rise_warning, rise_error
from ..backend._NRV_Class import NRV_class
import matplotlib.pyplot as plt

# enable faulthandler to ease "segmentation faults" debug
faulthandler.enable()


###############
## Functions ##
###############
def is_stim(stim):
    """
    check if an object is a stimulus, return True if yes, else False

    Parameters
    ----------
    stim : object
        object to test

    Returns
    -------
    bool
        True it the type is a stimulus object
    """
    return isinstance(stim, stimulus)


def set_common_time_series(stim1, stim2):
    """
    set two signals at the same time samples, missing samples are reconstructed by holding a value

    Parameters
    ----------
    stim1   : stimulus object
        First stimulus to synchronize
    stim2   : stimulus object
        Second object to synchronize
    """
    stim1.insert_samples(stim2.t)
    stim2.insert_samples(stim1.t)


def get_equal_timing_copies(stim1, stim2):
    """
    create two stimuli with equal timing as copies of the input ones

    Parameters
    ----------
    stim1   : stimulus object
        First stimulus to synchronize
    stim2   : stimulus object
        Second object to synchronize

    Returns
    --------
    stima : stimulus object
        copie of stim1 with timings from stim1 and stim2
    stimb : stimulus object
        copie of stim2 with timings from stim1 and stim2
    """
    stim_a = stimulus()
    stim_a.s = stim1.s
    stim_a.t = stim1.t
    stim_b = stimulus()
    stim_b.s = stim2.s
    stim_b.t = stim2.t
    stim_a.insert_samples(stim_b.t)
    stim_b.insert_samples(stim_a.t)
    return stim_a, stim_b


def datfile_2_stim(fname, dt=0.005):
    """Creates a stimulus from sampled data specified in a .dat file

    Parameters
    ----------
    fname : str
        name of the file containing the sampled data
    dt    : float, optional
        value of the sampling period, in ms. By default set to 0.005ms
    """
    stim_1 = stimulus()
    # open the dat file and feed the stimulus
    data = np.genfromtxt(fname)
    stim_1.t = np.arange(len(data)) * dt
    stim_1.s = data
    return stim_1


################################
## Stimulus object definition ##
################################
class stimulus(NRV_class):
    """
    Stimulus class for NRV2,
    signals are defined as asynchronous signals, with s the values and t as occurence timings.
    """

    def __init__(self, s_init=0):
        """
        Instantiation of a stimulus object.

        Parameters
        ----------
        s_init  : float
            initial value of the signal, by default 0
        """
        super().__init__()
        self.type = "stimulus"
        self.s = np.array([s_init])
        self.t = np.array([0])

    ## Save and Load mehtods
    def save_stimulus(self, save=False, fname="stimulus.json"):
        rise_warning("save_stimulus is a deprecated method use save")
        self.save(save=save, fname=fname)

    def load_stimulus(self, data="stimulus.json"):
        rise_warning("load_stimulus is a deprecated method use load")
        self.load(data=data)

    ############################
    ## basic handling methods ##
    ############################
    def append(self, s, t):
        """
        Append a sample to the signal, internal use only.

        Parameters
        ----------
        s   : float
            value of the signal to append, numpy array like
        t   : float
            time of signal change
        """
        self.s = np.append(self.s, np.asarray(s))
        self.t = np.append(self.t, np.asarray(t))

    def concatenate(self, s, t, t_shift=0):
        """
        Concatenate samples to a signal, internal use only.

        Parameters
        ----------
        s       : float
            values of signal, numpy array like
        t       : float
            time serie of the values, numpy array like
        t_shift : float
            time to shift the t values at the end of original signal, by default equal to 0.
            Here to prevent possible duplicates if the t serie starts with 0
        """
        self.s = np.append(self.s, np.asarray(s))
        self.t = np.append(self.t, np.asarray(t) + self.t[-1] + t_shift)

    def len(self):
        """
        Returns the length of the signal

        Returns
        -------
        len : int
            length of the signal (s and t attribute should have the same length
            if the signal is not corrupted)
        """
        return len(self.s)

    def sort(self):
        """
        Sort the signal with increasing timings
        """
        ordered_ind = np.argsort(self.t)
        self.s = self.s[ordered_ind]
        self.t = self.t[ordered_ind]

    def insert_samples(self, t):
        """
        Insert samples inside a signal and adapt values consequently

        Parameters
        ----------
        t   : array, np.array or list
            time serie of samples to insert, numpy array-like, dosent have to be sorted
        """
        # add the new time values at their place and remove duplicates
        new_t = np.unique(np.sort(np.append(self.t, np.asarray(t))))
        new_s = [self.s[0]]
        j = 1
        for k in range(1, len(new_t)):
            if j < self.len():
                if new_t[k] < self.t[j]:  # added sample, hold the last value
                    new_s.append(new_s[-1])
                else:  # orinal sample, retrieve value in original signal and increment counter
                    new_s.append(self.s[j])
                    j += 1
            else:
                new_s.append(self.s[-1])
        self.s = np.asarray(new_s)
        self.t = new_t

    def snap_time(self, dt_min):
        i_mask = [True for _ in range(len(self.t))]
        for i in range(len(self.t) - 1):
            j = 0
            if self.t[i + 1] - self.t[i] < dt_min:
                while i > j and not i_mask[i - j]:
                    j += 1
                if self.t[i + 1] - self.t[i - j] < dt_min:
                    i_mask[i + 1] = False
        self.s = self.s[i_mask]
        self.t = self.t[i_mask]

    def plot(self, ax: plt.axes, scatter=False, **ax_kwargs):
        """
        Plot the stimulus
        """
        if scatter:
            ax.scatter(self.t, self.s, **ax_kwargs)
        else:
            ax.step(self.t, self.s, where="post", **ax_kwargs)

    #####################
    ## special methods ##
    #####################
    def __len__(self):
        return self.len()

    def __abs__(self):
        stim = stimulus()
        stim.s = np.absolute(self.s)
        stim.t = self.t
        return stim

    def __neg__(self):
        stim = stimulus()
        stim.s = -self.s
        stim.t = self.t
        return stim

    def __add__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = A.s + B.s
            C.t = A.t
        else:
            C.s = self.s + float(b)
            C.t = self.t
        return C

    def __sub__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = A.s - B.s
            C.t = A.t
        else:
            C.s = self.s - float(b)
            C.t = self.t
        return C

    def __mul__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = A.s * B.s
            C.t = A.t
        else:
            C.s = self.s * float(b)
            C.t = self.t
        return C

    def __radd__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = B.s + A.s
            C.t = A.t
        else:
            C.s = float(b) + self.s
            C.t = self.t
        return C

    def __rsub__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = B.s - A.s
            C.t = A.t
        else:
            C.s = float(b) - self.s
            C.t = self.t
        return C

    def __rmul__(self, b):
        C = stimulus()
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            C.s = B.s * A.s
            C.t = A.t
        else:
            C.s = float(b) * self.s
            C.t = self.t
        return C

    def __pow__(self, p):
        C = stimulus()
        C.s = self.s ** float(p)
        return C

    def __eq__(self, b):
        if is_stim(b):
            A, B = get_equal_timing_copies(self, b)
            flag = np.array_equal(A.s, B.s) and np.array_equal(A.t, B.t)
        else:
            flag = True
            for value in self.s:
                if value != b:
                    flag = False
        return flag

    def __ne__(self, b):  # self != b
        return not self == b

    def integrate(self):
        return np.trapz(self.s, x=self.t)

    #######################
    ## signal generators ##
    #######################
    def constant(self, value, start=0):
        """
        Ceat a constant signal

        Parameters
        ----------
        value : float
            Value of the constant signal
        start :float
            starting time of the constant signal, by default set to 0
        """
        self.append(value, start)

    def pulse(self, start, value, duration=0):
        """
        Create pulse shape signal samples

        Parameters
        ----------
        value       : float
            value of the pulse
        start       : float
            starting time of the pulse
        duration    : float
            duration of the pulse, optional and by default equal to zero, if non zero value,
            a point is added at the end of the pulse with the previous value
        """
        s_last = self.s[-1]
        self.append(value, start)
        if duration != 0:
            self.append(s_last, start + duration)

    def biphasic_pulse(
        self, start, s_cathod, t_stim, s_anod, t_inter, anod_first=False
    ):
        """
        Create a biphasic pulse waveform

        Parameters
        ----------
        start       : float
            starting time of the waveform, in ms
        s_cathod    : float
            cathodic (negative stimulation value) current, in uA
        t_stim      : float
            stimulation time, in ms
        s_anod      : float
            anodic (positive stimulation value) current and, in uA
        t_inter     : float
            inter pulse timing, in ms
        anod_first  : bool
            if true, stimulation is anodic and begins with the anodic value
            and is balanced with cathodic value, else stimuation is cathodic
            and begins with the cathodic value and is balances with anodic value,
            by default set to False (cathodic first as most stimulation protocols)

        Warning
        -------
        `s_cathod` must always positive, the user give here the absolute value
        """
        if not anod_first:
            s_1 = -s_cathod
            s_2 = s_anod
        else:
            s_2 = -s_cathod
            s_1 = s_anod
        if s_2 != 0:
            t_balance = abs(s_1 / s_2) * t_stim
        else:
            t_balance = 0
        self.concatenate(s_1, start)
        if t_inter == 0:
            self.concatenate(s_2, t_stim)
            if t_balance != 0:
                self.concatenate(0, t_balance)
        else:
            self.concatenate(0, t_stim)
            self.concatenate(s_2, t_inter)
            if t_balance != 0:
                self.concatenate(0, t_balance)

    def sinus(self, start, duration, amplitude, freq, offset=0, phase=0, dt=0):
        """
        Create a sinusoidal waveform

        Parameters
        ----------
        start       : float
            starting time of the waveform, in ms
        duration    : float
            duration of the waveform, in ms
        amplitude   : float
            amplitude of the waveform, in uA
        freq        : float
            frequency of the waveform, in kHz
        offset      : float
            offset current of the waveform, in uA, by default set to 0
        phase       : float
            initial phase of the waveform, in rad, by default set to 0
        anod_first  : bool
            if true, stimulation is anodic and begins with the anodic value
            and is balanced with cathodic value, else stimuation is cathodic
            and begins with the cathodic value and is balances with anodic value,
            by default set to False (cathodic first as most stimulation protocols)
        """
        # check the pseudo sampling period
        if dt == 0:
            dt = 1 / (freq * 100)
        elif freq > (1.0 / (2 * dt)):
            rise_warning(
                "dt too low in stimulus creation, Shannon criterion not respected"
            )
        Nb_points = int(duration / dt)
        # create the signal
        if start == 0:
            self.s[0] = amplitude * np.sin(phase) + offset
            t = np.linspace(dt, start + duration, num=Nb_points - 1)
            s = amplitude * np.sin(2 * np.pi * freq * t + phase) + offset
            self.concatenate(s, t, t_shift=0)
        else:
            t = np.linspace(0, duration, num=Nb_points)
            s = amplitude * np.sin(2 * np.pi * freq * t + phase) + offset
            t = np.linspace(start, start + duration, num=Nb_points)  # add start
            self.concatenate(s, t, t_shift=0)

    def harmonic_pulse(self, start, t_pulse, amplitude, amp_list, phase_list, dt=0):
        """
        Create a pulse waveform based on N harmonic

        Parameters
        ----------
        start       : float
            starting time of the waveform, in ms
        t_pulse      : float
            pulse duration, in ms
        amplitude   : float
            final amplitude of the pulse, in uA
            WARNING: always positive, the user give here the absolute value
        amp_list    : list
            list of relative sine amplitude, between 0 and 1
        phase_list  : list
            list of sine pulse phases
        dt          : float
            sampling time period to generate the sinusoidal shape. If equal to 0,
            dt is automatically set to match 100 samples per sinusoid period by default set to 0
        """
        if len(amp_list) != len(phase_list):
            rise_error("amp_list and phase_list must be of same length")
        n_sine = len(amp_list)
        freq = 1 / (2 * t_pulse)
        if dt == 0:
            dt = 1 / (n_sine * freq * 100)

        elif freq > (1.0 / (2 * dt)):
            rise_warning(
                "dt too low in stimulus creation, Shannon criterion not respected"
            )
        Nb_points = int(t_pulse / dt)

        # create the signal
        freq_harmonic = freq
        if start == 0:
            t = np.linspace(dt, t_pulse, num=Nb_points - 1)
            self.s[0] = 0
            s = 0
            for i in range(n_sine):
                self.s[0] += amp_list[i] * np.sin(phase_list[i])
                s += amp_list[i] * np.sin(
                    2 * np.pi * freq_harmonic * t + phase_list[i] - np.pi
                )
                freq_harmonic = freq * (i + 2)
            s = s - np.max(s)  # shift s to avoid any postive values
            s = s * amplitude / np.max(np.abs(s))  # rescale s to finale amp
            s[-1] = 0
            self.concatenate(s, t, t_shift=0)
        else:
            t = np.linspace(0, t_pulse, num=Nb_points)
            s = 0
            for i in range(n_sine):
                s += amp_list[i] * np.sin(
                    2 * np.pi * freq_harmonic * t + phase_list[i] - np.pi
                )
                freq_harmonic = freq * (i + 2)
            s = s - np.max(s)  # shift s to avoid any postive values
            s = s * amplitude / np.max(np.abs(s))  # rescale s to finale amp
            s[-1] = 0
            t = np.linspace(start, start + t_pulse, num=Nb_points)
            self.concatenate(s, t, t_shift=0)

    def square(self, start, duration, freq, amplitude, offset, anod_first=False):
        """
        Create a repetitive (periodic) square waveform

        Parameters
        ----------
        start       : float
            starting time of the waveform, in ms
        duration    : float
            duration of the waveform, in ms
        amplitude   : float
            amplitude of the waveform, in uA
        freq        : float
            frequency of the waveform, in kHz
        offset      : float
            offset current of the waveform, in uA, by default set to 0
        dt          : float
            sampling time period to generate the sinusoidal shape. If equal to 0,
            dt is automatically set to match 100 samples per sinusoid period by default set to 0
        """
        Nb_pts = 2 * int(duration / freq) - 1
        dt = 1 / (2 * freq)
        t = np.linspace(0, duration, num=Nb_pts)
        s = np.ones(Nb_pts) * amplitude
        k_start = 0
        if anod_first:
            k_start = 1
        for k in range(k_start, len(s), 2):
            s[k] *= -1
        s += offset
        self.concatenate(s, t, t_shift=start)

    def ramp(
        self, slope, start, duration, dt, bounds=(0, float("inf")), printslope=False
    ):
        """
        Create a ramp waveform with slop value

        Parameters
        ----------
        slope       : float
            slope of the waveform, in uA.ms-1
        start       : float
            starting time of the waveform, in ms
        duration    : float
            duration of the waveform, in ms
        dt          : float
            sampling time period to generate the sinusoidal shape
        bounds      : tuple
            boundary vaues of the ramp signal
        printslope  : bool, optional
            if True, the value of the slope is printed on the prompt
        """
        # create the signal
        if printslope:
            pass_info("slope = " + str(slope))
        Nb_points = int(duration / dt)
        t = np.array([k * dt for k in range(Nb_points)])
        if slope < 0:
            s = max(bounds) * np.ones(Nb_points)
        else:
            s = min(bounds) * np.ones(Nb_points)
        point_start = int(start / dt)
        for i in range(point_start, Nb_points):
            if slope >= 0:
                s[i] = min(bounds[1], bounds[0] + (i - point_start) * slope * dt)
            if slope < 0:
                s[i] = max(bounds[0], bounds[1] + (i - point_start) * slope * dt)
        self.concatenate(s, t, t_shift=0)

    def ramp_lim(self, tstart, tstop, ampstart, ampmax, duration, dt, printslope=False):
        """
        Create a ramp waveform with bounds values

        Parameters
        ----------
        ampstart    : float
            initiale amplitude of the waveform, in uA
        ampmax      : float
            final amplitude of the waveform, in uA
        tstart      : float
            starting time of the waveform, in ms
        tmax        : float
            starting time of the waveform, in ms
        duration    : float
            duration of the waveform, in ms
        dt          : float
            sampling time period to generate the sinusoidal shape
        printslope  : bool, optional
            if True, the value of the slope is printed on the prompt
        """
        slope = (ampstart - ampmax) / (tstart - tstop)
        bounds = (min(ampstart, ampmax), max(ampstart, ampmax))
        self.ramp(slope, tstart, duration, dt, bounds, printslope)
