"""
NRV-Cellular Level simulations
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq / Thomas Couppey
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from .fascicles import *
from .axons import *
from .unmyelinated import *
from .myelinated import *
from .thin_myelinated import *
from .extracellular import *
from .electrodes import *
from .materials import *
from .stimulus import *
from .log_interface import rise_error, rise_warning, pass_info


###############################################################
#########################  Loaders  ###########################
###############################################################

def load_any_fascicle(data, extracel_context=False, intracel_context=False):
    """
    generate any kind of fascicle from a dictionary or a json file

    Parameters
    ----------
    data    : str or dict
        json file path or dictionary containing fascicle information
    """
    if type(data) == str:
        fasc_dic = json_load(data)
    else: 
        fasc_dic = data
    fasc = fascicle()
    fasc.load_axon(fasc_dic, extracel_context=extracel_context, intracel_context=intracel_context)
    return fasc

def load_any_axon(data, extracel_context=False, intracel_context=False):
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
        if ax_dic["thin"]:
            ax = thin_myelinated(0,0,1,10)
        else:
            ax = myelinated(0,0,1,10)
    elif ax_dic["myelinated"] is False:
        ax = unmyelinated(0,0,1,10)
    else:
        ax = axon(0,0,1,10)

    ax.load_axon(ax_dic, extracel_context=extracel_context, intracel_context=intracel_context)
    return ax


