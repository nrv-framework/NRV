r"""
The ``units`` module handles conversion to and from the default nrv units.
Several functions are included to simplify the use of these units.

The folowing table details the default units used in NRV and the lists of units available for conversion:
    .. list-table::
        :align: left
        :header-rows: 1

        *   - Category
            - Default
            - Existing
        *   - Voltage
            - mV
            - uV, V, kV, MV
        *   - Time
            - ms
            - us, s, minute, hour, day
        *   - Length
            - um
            - nm, mm, cm, dm, m
        *   - Currents
            - uA
            - nA, mA, A
        *   - Conductance
            - S
            - kS, mS, uS
        *   - Frequency
            - kHz
            - Hz, MHz, GHz
        *   - Capacitance
            - uF
            - F, mF, pF, nF
        *   - Angle
            - rad
            - deg

"""

import numpy as np
from copy import deepcopy
from math import isnan

###################
## defaulf units ##
###################
mV = 1  # default unit for Voltage is mV, as neuron
ms = 1  # default unit for time is ms, as neuron
um = 1  # default unit for length is um, as neuron
uA = 1  # default unit for current is uA, UNLESS NEURON who is by default in nA
S = 1  # default unit for conductance is S
kHz = 1  # default unit for frequency is kHz
uF = 1  # default unit for capacitance is uF
rad = 1  # default unit for capacitance is uF

######################
## voltage prefixes ##
######################
uV = 1e-3 * mV
V = 1e3 * mV
kV = 1e3 * V
MV = 1e3 * kV

#############################
## time prefixes and units ##
#############################
us = 1e-3 * ms
s = sec = 1e3 * ms
minute = 60 * sec
hour = 60 * minute
day = 24 * hour

########################
## frequency prefixes ##
########################

Hz = 1e-3 * kHz
MHz = 1e3 * kHz
GHz = 1e6 * kHz

#####################
## length prefixes ##
#####################
nm = 1e-3 * um
mm = 1e3 * um
cm = 1e1 * mm
dm = 1e1 * cm
m = 1e1 * dm

######################
## current prefixes ##
######################
nA = 1e-3 * uA
mA = 1e3 * uA
A = 1e3 * mA

###########################
## conductance prefixes ##
###########################
kS = 1e3 * S
mS = 1e-3 * S
uS = 1e-6 * S

###########################
## capacitance prefixes ##
###########################
F = 1e6 * uF
mF = 1e3 * uF
pF = 1e-3 * uF
nF = 1e-6 * uF

####################
## angle prefixes ##
####################
deg = rad * np.pi / 180

#############################
####  Usefull functions ####
#############################


def print_default_nrv_unit():
    """
    Print all the default units in nrv.
    """
    print(
        "Voltage: mV",
        "\nTime: ms",
        "\nLength: um",
        "\nCurrents: uA",
        "\nConductance: S",
        "\nFrequency: kHz",
        "\nCapacitance: uF",
    )


def from_nrv_unit(value, unit):
    """
    Convert a quantity ``value`` from the default nrv units to ``unit``.

    Parameters
    ----------
    value:      int, float, list or np.ndarray
        value or values wich should be converted.
    unit:     int or str
        unit from which value should be converted, see example.

    Returns
    -------
    int, float, list or np.ndarray
        rounded value or values, with the same type and shape than ``value``.

    Example
    -------
    Here are three ways of converting 4530um (default unit) into 4.53mm:

        >>> import nrv
        >>> val_default = 4530 # um
        >>> val_default / nrv.mm
        4.53
        >>> nrv.from_nrv_unit(val_default, nrv.mm)
        4.53
        >>> nrv.from_nrv_unit(val_default, "mm")
        4.53
    """
    if isinstance(unit, str):
        unit = eval(unit)
    if np.iterable(value) and not isinstance(value, np.ndarray):
        cp_value = deepcopy(value)
        for i, num in enumerate(value):
            cp_value[i] = from_nrv_unit(num, unit)
        return cp_value
    else:
        return value / unit


def to_nrv_unit(value, unit):
    """
    Convert a quantity ``value`` from unit to the default nrv ``unit``.

    Parameters
    ----------
    value:      int, float, list or np.ndarray
        value or values wich should be converted.
    unit:     int or str
        unit to which value should be converted, see examples.

    Returns
    -------
    int, float, list or np.ndarray
        rounded value or values, with the same type and shape than ``value``.

    Example
    -------
    Here are three ways of converting 0.12 MHz into the default unit of the corresponding nrv (kHz):

        >>> import nrv
        >>> val_MHz = 0.12 # MHz
        >>> val_MHz * nrv.MHz
        120.0
        >>> nrv.to_nrv_unit(val_MHz, nrv.MHz)
        120.0
        >>> nrv.to_nrv_unit(val_MHz, "MHz")
        120.0

    Here is how to convert a ``list`` or ``np.array`` of values in seconds
    to milliseconds (nrv's default unit):

        >>> import numpy as np
        >>> vals_s = [[1, 2, 3], [4, 5, 6]]  # s
        >>> nrv.to_nrv_unit(vals_s, nrv.s)  # ms
        [[1000.0, 2000.0, 3000.0], [4000.0, 5000.0, 6000.0]]
        >>> nrv.to_nrv_unit(np.array(vals_s), nrv.s)  # ms
        array([[1000., 2000., 3000.],
            [4000., 5000., 6000.]])

    """
    if isinstance(unit, str):
        unit = eval(unit)
    if np.iterable(value) and not isinstance(value, np.ndarray):
        cp_value = deepcopy(value)
        for i, num in enumerate(value):
            cp_value[i] = to_nrv_unit(num, unit)
        return cp_value
    else:
        return value * unit


def convert(value, unitin, unitout):
    """
    Convert a quantity ``value`` from ``unitin`` to ``unitout``.

    Parameters
    ----------
    value:      int, float, list or np.ndarray
        value or values wich should be converted.
    unit:     int or str
        unit to which value should be converted, see examples.

    Returns
    -------
    int, float, list or np.ndarray
        rounded value or values, with the same type and shape than ``value``.)

    Example
    -------
    Here are two ways of converting 0.2 S/m^{2} into S/cm^{2}:

        >>> import nrv
        >>> val_S_m = 0.2 # S/m**2
        >>> nrv.convert(val_S_m, nrv.S/nrv.m**2, nrv.S/nrv.cm**2)
        2e-05
        >>> nrv.convert(val_S_m, "S/m**2", "S/cm**2")
        2e-05
    """
    if np.iterable(value) and not isinstance(value, np.ndarray):
        cp_value = deepcopy(value)
        for i, num in enumerate(value):
            cp_value[i] = convert(num, unitin, unitout)
        return cp_value
    else:
        return from_nrv_unit(to_nrv_unit(value, unitin), unitout)


def sci_round(value, digits=3):
    """
    Rounds one or several values to ``digits`` significant digits.

    Parameters
    ----------
    value:      int, float, list or np.ndarray
        value or values wich should be rounded.
    digits:     int
        number of significant digits to keep.

    Returns
    -------
    int, float, list or np.ndarray
        rounded value or values, with the same type and shape than ``value``.
    """
    if np.iterable(value):
        cp_value = deepcopy(value)
        for i, num in enumerate(value):
            cp_value[i] = sci_round(num, digits)
        return cp_value
    else:
        if not isnan(value):
            power = "{:e}".format(value).split("e")[1]
            return round(value, -(int(power) - digits + 1))
        else:
            return value
