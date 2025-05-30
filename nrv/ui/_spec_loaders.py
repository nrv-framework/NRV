from ..backend._NRV_Class import load_any
from ..backend._log_interface import rise_warning

from ..nmod import fascicle, nerve, axon, myelinated, unmyelinated



def load_nerve(data, **kwargs)->nerve:
    """
    loads a nerve from a json file or a dictionary generated with NRV_class.save

    Parameters
    ----------
    data : str, dict, nrv_class
        data from which the object should be generated:

            - if str, data will be loaded from the corresponding json file
            - if dict, data will be loaded from a dictionnary
            - if nrv_class, same object will be returned
    **kwargs
        additionnal argument to use for the loading

    Returns
    -------
    nerve | None
    """

    obj = load_any(data, **kwargs)
    if not isinstance(obj, nerve):
        rise_warning(data, " not a loadable nerve")
        return None
    return obj

def load_fascicle(data, **kwargs)->fascicle:
    """
    loads a fascicle from a json file or a dictionary generated with NRV_class.save

    Parameters
    ----------
    data : str, dict, nrv_class
        data from which the object should be generated:

            - if str, data will be loaded from the corresponding json file
            - if dict, data will be loaded from a dictionnary
            - if nrv_class, same object will be returned
    **kwargs
        additionnal argument to use for the loading

    Returns
    -------
    fascicle | None
    """
    obj = load_any(data, **kwargs)
    if not isinstance(obj, fascicle):
        rise_warning(data, " not a loadable fascicle")
        return None
    return obj


def load_axon(data, **kwargs)->myelinated|unmyelinated:
    """
    loads a fascicle from a json file or a dictionary generated with NRV_class.save

    Parameters
    ----------
    data : str, dict, nrv_class
        data from which the object should be generated:

            - if str, data will be loaded from the corresponding json file
            - if dict, data will be loaded from a dictionnary
            - if nrv_class, same object will be returned
    **kwargs
        additionnal argument to use for the loading

    Returns
    -------
    myelinated|unmyelinated|None
    """
    obj = load_any(data, **kwargs)
    if not isinstance(obj, axon):
        rise_warning(data, " not a loadable axon")
        return None
    return obj

