"""
NRV-Cellular Level simulations
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from ..backend.MCore import *
from ..fmod.electrodes import *
from ..fmod.extracellular import *
from ..fmod.materials import *
from ..fmod.stimulus import *
from ..nmod.axons import *
from ..nmod.fascicles import *
from ..nmod.myelinated import *
from ..nmod.unmyelinated import *

###############################################################
#########################  Loaders  ###########################
###############################################################


def load_any_fascicle(
    data, extracel_context=False, intracel_context=False, rec_context=False
):
    """
    generate any kind of fascicle from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing fascicle information
    """
    synchronize_processes()
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
):
    """
    generate any kind of axon from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing axon information
    """
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
