from ..backend._NRV_Class import load_any
from ..backend._log_interface import rise_warning, pass_info
from ..backend._NRV_Class import NRV_class

from ..nmod import fascicle, nerve, axon, myelinated, unmyelinated
from ..backend._file_handler import rmv_ext


def load_nerve(
    data: str | dict | NRV_class,
    extracel_context: bool = False,
    intracel_context: bool = False,
    rec_context: bool = False,
    **kwargs,
) -> nerve:
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

    obj = load_any(
        data,
        extracel_context=extracel_context,
        intracel_context=intracel_context,
        rec_context=rec_context,
        **kwargs,
    )
    if not isinstance(obj, nerve):
        rise_warning(data, " not a loadable nerve")
        return None
    return obj


def load_fascicle(
    data: str | dict | NRV_class,
    extracel_context: bool = False,
    intracel_context: bool = False,
    rec_context: bool = False,
    **kwargs,
) -> fascicle:
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
    obj = load_any(
        data,
        extracel_context=extracel_context,
        intracel_context=intracel_context,
        rec_context=rec_context,
        **kwargs,
    )
    if not isinstance(obj, fascicle):
        rise_warning(data, " not a loadable fascicle")
        return None
    return obj


def load_axon(
    data: str | dict | NRV_class,
    extracel_context: bool = False,
    intracel_context: bool = False,
    rec_context: bool = False,
    **kwargs,
) -> myelinated | unmyelinated:
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
    obj = load_any(
        data,
        extracel_context=extracel_context,
        intracel_context=intracel_context,
        rec_context=rec_context,
        **kwargs,
    )
    if not isinstance(obj, axon):
        rise_warning(data, " not a loadable axon")
        return None
    return obj


# ---------- #
#  Updaters  #
# ---------- #


def update_fascicle_file(
    fname_in: str, fname_out: str | None = None, overwrite: bool = False
):
    """
    Update a file containing a deprecated version of saved fascicle

    Parameters
    ----------
    fname_in : str
        File to load
    fname_out : str | None, optional
        File use to save the updated fascicle, if None two cases:

            - `overwrite == True`: `fname_out` is set to `fname_in`
            - `overwrite == True` (default): `fname_out` is set to `fname_in + "_updated"`
    overwrite : bool, optional
        If True original file can be overwritten, by default False
    """

    if fname_out is None:
        if overwrite:
            fname_out = fname_in
        else:
            fname_out = rmv_ext(fname_in) + "_updated"

    fasc = load_fascicle(
        data=fname_in, extracel_context=True, intracel_context=True, rec_context=True
    )
    pass_info(f"{fname_in} loaded")
    fasc.save(
        data=fname_out, extracel_context=True, intracel_context=True, rec_context=True
    )
    pass_info(f"updated and saved in {fname_in}")
