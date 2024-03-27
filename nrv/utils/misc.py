"""
Miscellaneous functions usefull functions used in and to use with NRV
"""

import numpy as np


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


#########################################################
############# Fascicles related functions ###############
#########################################################


def get_perineurial_thickness(fasc_d:float, nerve_type:str="default") -> float:
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