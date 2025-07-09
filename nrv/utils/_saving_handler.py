"""
NRV-Cellular Level simulations
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""

from ..fmod._electrodes import *
from ..fmod._extracellular import *
from ..fmod._materials import *
from ._stimulus import *
from ..nmod._axons import *
from ..nmod._fascicles import *
from ..nmod._myelinated import *
from ..nmod._unmyelinated import *
from ..backend._log_interface import rise_warning

# --------- #
#  Loaders  #
# --------- #


def load_any_fascicle(
    data: str | dict,
    extracel_context: bool = False,
    intracel_context: bool = False,
    rec_context: bool = False,
) -> fascicle:
    """
    generate any kind of fascicle from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing fascicle information
    """
    rise_warning(DeprecationWarning, ": use load any intead")
    if type(data) == str:
        fasc_dic = json_load(data)
    else:
        fasc_dic = data
    fasc = fascicle()
    fasc.load(
        fasc_dic,
        extracel_context=extracel_context,
        intracel_context=intracel_context,
        rec_context=rec_context,
    )
    if extracel_context and rec_context:
        return fasc, fasc.extra_stim, fasc.recorder
    elif extracel_context:
        return fasc, fasc.extra_stim
    elif rec_context:
        return fasc, fasc.recorder
    else:
        return fasc


def load_any_axon(
    data, extracel_context=False, intracel_context=False, rec_context=False
) -> axon:
    """
    generate any kind of axon from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing axon information
    """
    rise_warning(DeprecationWarning, ": use load_any function intead")
    if type(data) == str:
        ax_dic = json_load(data)
    else:
        ax_dic = data

    if ax_dic["myelinated"] is True:
        ax = myelinated(0, 0, 1, 10)
    else:
        ax = unmyelinated(0, 0, 1, 10)

    ax.load(
        ax_dic,
        extracel_context=extracel_context,
        intracel_context=intracel_context,
        rec_context=rec_context,
    )
    if extracel_context and rec_context:
        return ax, ax.extra_stim, ax.recorder
    elif extracel_context:
        return ax, ax.extra_stim
    elif rec_context:
        return ax, ax.recorder
    else:
        return ax
