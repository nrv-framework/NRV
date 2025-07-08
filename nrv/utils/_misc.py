"""
Miscellaneous functions usefull functions used in and to use with NRV
"""

import math
import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame
from copy import deepcopy


from ._units import to_nrv_unit


#############################
## miscellaneous functions ##
#############################
def distance_point2point(x_1, y_1, x_2=0, y_2=0):
    """
    Computes the distance between a point (x_p,y_p) and a line defined as y=a*x+b

    Parameters
    ----------
    x_1 : float
        first point x coordinate,
    y_1 : float
        firstpoint y coordinate,
    x_2 : float
        second point x coordinate, by default 0
    y_2 : float
        second point y coordinate, , by default 0

    Returns
    --------
    d : float
        distance between the point and the orthogonal projection of (x_p,y_p) on it
    """
    d = ((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2) ** 0.5
    return d


def distance_point2line(x_p, y_p, a, b):
    """
    Computes the distance between a point (x_p,y_p) and a line defined as y=a*x+b

    Parameters
    ----------
    x_p : float
        point x coordinate,
    y_p : float
        point y coordinate,
    a   : float
        line direction coeefficient
    b   : float
        line y for x = 0

    Returns
    --------
    d : float
        distance between the point and the orthogonal projection of (x_p,y_p) on it
    """
    d = np.abs(a * x_p - y_p + b) / (np.sqrt(a**2 + 1))
    return d


def nearest_idx(array: NDArray, val: float) -> int:
    """
    Return index of neareast value

    Parameters
    ----------
    array : NDArray
        array of values
    val : float
        neareast value to find index

    Returns
    -------
    int
        index of the neareast value
    """
    return (np.absolute(array - val)).argmin()


def nearest_greater_idx(array: NDArray, val: float) -> int:
    """
    Return index of neareast greater value

    Parameters
    ----------
    array : NDArray
        array of values
    val : float
        neareast greater value to find index

    Returns
    -------
    int
        index of the neareast greater value
    """
    diff = array - val
    mask = np.ma.MaskedArray(diff, diff < 0)
    return mask.argmin()


def in_tol(test: float, ref: float, tol: float = 0.1) -> bool:
    """
    Check if a value is equal to a value +- a tol (excluded).

    Parameters
    ----------
    test : float
        Value to test
    ref : float
        Reference value
    tol : float, optional
        Tolerance, expressed as a proportion of ref. By default 0.1

    Returns
    -------
    bool
        True if within tolerance, else False.
    """
    up_bound = ref * (1 + tol)
    down_bound = ref * (1 - tol)
    return np.abs(test) < up_bound and np.abs(test) > down_bound


def rotate_2D(
    point: tuple[np.ndarray, np.ndarray],
    angle: float,
    degree: bool = False,
    center: tuple[float, float] = (0, 0),
    as_array: bool = False,
):
    if degree:
        angle = to_nrv_unit(angle, "deg")
    if isinstance(point, np.ndarray):
        X = deepcopy(point)
    else:
        X = np.array(point).astype(float).T

    rot_mat = np.array(
        [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
    )
    c = np.array(center)

    # Translate center to (0,0)
    X -= c
    # rot around center
    X @= rot_mat

    # Translate back center to  its initial position
    X += c

    # Check if the normalized point is inside the unit circle
    if as_array:
        return X.T
    if len(X.shape) == 1:
        return X[0], X[1]
    return X[:, 0], X[:, 1]


####################################################
############# nmod related functions ###############
####################################################
def get_perineurial_thickness(fasc_d: float, nerve_type: str = "default") -> float:
    """
    Return a fascicle's perineurium thickness from its diameter.
    Relationship extract from [1]

    Parameters
    ----------
    fasc_d: float
        diameter of the fascicle
    nerve_type: str
        type of nerve containing the fascicle, possible types:

                        - "default"
                        - "sciatic"
                        - "medial popliteal"
                        - "lateral popliteal"
                        - "ulnar"
                        - "radial"
                        - "median"

    Return
    ------
    float:
        thickness of the perineurium

    Note
    ----
    [1] Y. Grinberg, M. A. Schiefer, D. J. Tyler, and K. J. Gustafson, “Fascicular Perineurium Thickness, Size, and Position Affect Model Predictions of Neural Excitation,” IEEE Trans. Neural Syst. Rehabil. Eng., vol. 16, no. 6, pp. 572–581, Dec. 2008.
    """
    thpc = 0.03
    if nerve_type.lower() == "sciatic":
        thpc = 0.033
    elif nerve_type.lower() == "medial popliteal":
        thpc = 0.026
    elif nerve_type.lower() == "lateral popliteal":
        thpc = 0.028
    elif nerve_type.lower() == "ulnar":
        thpc = 0.026
    elif nerve_type.lower() == "radial":
        thpc = 0.03
    elif nerve_type.lower() == "median":
        thpc = 0.033

    return fasc_d * thpc


MRG_data = DataFrame(
    data={
        "fiberD": np.asarray([1, 2, 5.7, 7.3, 8.7, 10.0, 11.5, 12.8, 14.0, 15.0, 16.0]),
        "g": np.asarray(
            [
                0.565,
                0.585,
                0.605,
                0.630,
                0.661,
                0.690,
                0.700,
                0.719,
                0.739,
                0.767,
                0.791,
            ]
        ),
        "axonD": np.asarray([0.8, 1.6, 3.4, 4.6, 5.8, 6.9, 8.1, 9.2, 10.4, 11.5, 12.7]),
        "nodeD": np.asarray([0.7, 1.4, 1.9, 2.4, 2.8, 3.3, 3.7, 4.2, 4.7, 5.0, 5.5]),
        "paraD1": np.asarray([0.7, 1.4, 1.9, 2.4, 2.8, 3.3, 3.7, 4.2, 4.7, 5.0, 5.5]),
        "paraD2": np.asarray(
            [0.8, 1.6, 3.4, 4.6, 5.8, 6.9, 8.1, 9.2, 10.4, 11.5, 12.7]
        ),
        "deltax": np.asarray(
            [100, 200, 500, 750, 1000, 1150, 1250, 1350, 1400, 1450, 1500]
        ),
        "paralength2": np.asarray([5, 10, 35, 38, 40, 46, 50, 54, 56, 58, 60]),
        "nl": np.asarray([15, 20, 80, 100, 110, 120, 130, 135, 140, 145, 150]),
    }
)


def get_MRG_parameters(diameter: float | NDArray, fit_all: bool = False) -> tuple[8]:
    """
    Compute the MRG geometrical parameters from interpolation of original data [1]

    Note
    ----
    The data used is stored in the ``MRG_data`` DataFrame, so it can be printed as follows
        >>> print(nrv.MRG_data)

    Parameters
    ----------
    diameter    : float
        diameter of the unmylinated axon to implement, in um
    fit_all     : bool
        if False, for diameters included in ``MRG_data``, original data are used without interpollation


    Returns
    -------
    g           : float
    axonD       : float
    nodeD       : float
    paraD1      : float
    paraD2      : float
    deltax      : float
    paralength2 : float
    nl          : float

    Note
    ----
    [1] McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle. Journal of Neurophysiology 87:995-1006, 2002.
    """
    MRG_fiberD = MRG_data.fiberD.to_numpy()
    MRG_g = MRG_data.g.to_numpy()
    MRG_axonD = MRG_data.axonD.to_numpy()
    MRG_nodeD = MRG_data.nodeD.to_numpy()
    MRG_paraD1 = MRG_data.paraD1.to_numpy()
    MRG_paraD2 = MRG_data.paraD2.to_numpy()
    MRG_deltax = MRG_data.deltax.to_numpy()
    MRG_paralength2 = MRG_data.paralength2.to_numpy()
    MRG_nl = MRG_data.nl.to_numpy()

    fit_all |= isinstance(diameter, np.ndarray)
    if not fit_all and diameter in MRG_fiberD:
        index = np.where(MRG_fiberD == diameter)[0]
        g = MRG_g[index]
        axonD = MRG_axonD[index]
        nodeD = MRG_nodeD[index]
        paraD1 = MRG_paraD1[index]
        paraD2 = MRG_paraD2[index]
        deltax = MRG_deltax[index]
        paralength2 = MRG_paralength2[index]
        nl = MRG_nl[index]
    else:
        # create fiting polynomyals
        g_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_g, 3))
        axonD_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_axonD, 3))
        nodeD_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_nodeD, 3))
        paraD1_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paraD1, 3))
        paraD2_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paraD2, 3))

        # outside of the MRG originla limit, take 1st order approx,
        paralength2_poly_OoB = np.poly1d(np.polyfit(MRG_fiberD, MRG_paralength2, 3))
        deltax_poly_OoB = np.poly1d(np.polyfit(MRG_fiberD, MRG_deltax, 2))

        # try to fit a bit better
        paralength2_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paralength2, 5))
        deltax_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_deltax, 5))
        nl_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_nl, 3))

        # evaluate for the requested diameter
        g = g_poly(diameter)
        axonD = axonD_poly(diameter)
        nodeD = nodeD_poly(diameter)
        paraD1 = paraD1_poly(diameter)
        paraD2 = paraD2_poly(diameter)
        nl = nl_poly(diameter)

        if isinstance(diameter, np.ndarray):
            paralength2 = np.zeros(len(diameter))
            deltax = np.zeros(len(diameter))
            I_OoB = (diameter < 1.0) | (diameter > 14.0)
            paralength2[I_OoB] = paralength2_poly_OoB(diameter[I_OoB])
            deltax[I_OoB] = deltax_poly_OoB(diameter[I_OoB])
            paralength2[~I_OoB] = paralength2_poly(diameter[~I_OoB])
            deltax[~I_OoB] = deltax_poly(diameter[~I_OoB])
            return (
                g,
                axonD,
                nodeD,
                paraD1,
                paraD2,
                deltax,
                paralength2,
                nl,
            )
        else:
            if diameter < 1.0 or diameter > 14.0:
                paralength2 = paralength2_poly_OoB(diameter)
                deltax = deltax_poly_OoB(diameter)
            else:
                paralength2 = paralength2_poly(diameter)
                deltax = deltax_poly(diameter)
    return (
        float(g),
        float(axonD),
        float(nodeD),
        float(paraD1),
        float(paraD2),
        float(deltax),
        float(paralength2),
        float(nl),
    )


def get_length_from_nodes(diameter, nodes):
    """
    Function to compute the length of a myelinated axon to get the correct number of Nodes of Ranvier
    For Myelinated models only (not compatible with A delta thin myelinated models)

    Parameters
    ----------
    diameter    : float
        diameter of the axon in um
    nodes       : int
        number of nodes in the axon

    Returns
    -------
    length      : float
        lenth of the axon with the correct number of nodes in um
    """
    MRG_fiberD = MRG_data.fiberD.to_numpy()
    MRG_deltax = MRG_data.deltax.to_numpy()
    if diameter in MRG_fiberD:
        index = np.where(MRG_fiberD == diameter)[0]
        deltax = MRG_deltax[index]
    else:
        deltax_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_deltax, 4))
        deltax = deltax_poly(diameter)
    return float(math.ceil(deltax * (nodes - 1)))


def membrane_capacitance_from_model(model):
    if model in ["MRG", "Gaines_motor", "Gaines_sensory"]:
        return 2
    if "Schild" in model:
        return 1.326291192
    return 1


def compute_complex_admitance(
    f: float | np.ndarray, g: float | np.ndarray, fc: float | np.ndarray
) -> complex:
    """
    compute the complex admitance of a first oder system (of cutoff frequency fc and conductivity g) at a given frequency f

    Parameters
    ----------
    f : float or np.array
        frequency or frequencies for which the admitance should be computed
    g : float
        conductivity of the system
    fc : float
        cutoff frequency of the system

    Returns
    -------
    complex
        complex admitance
    """
    if isinstance(g, np.ndarray) and isinstance(f, np.ndarray):
        return g * (1 + 1j * f[:, np.newaxis] / fc)

    return g * (1 + 1j * f / fc)
