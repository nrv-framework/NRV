from ..nmod._nerve import nerve
from ..nmod._fascicles import fascicle
from ..nmod._myelinated import get_MRG_parameters


def crop_fascicle(fasc: fascicle, x0: float, new_l: float) -> fascicle:
    """_summary_

    Parameters
    ----------
    fasc : fascicle
        fascicle to crop
    x0 : float
        x position of the begining of the new fascicle
    new_l : float
        length of the new fascicle

    Returns
    -------
    fascicle
        fascicle cropped
    """
    fasc.define_length(new_l)
    if not (fasc.L is None or len(fasc.NoR_relative_position) == 0):
        for i in range(fasc.n_ax):
            if fasc.axons_type[i] == 1:
                _, _, _, _, _, deltax, _, _ = get_MRG_parameters(fasc.axons_diameter[i])
                fasc.NoR_relative_position = fasc.NoR_relative_position + (x0 / deltax)

                fasc.NoR_relative_position -= int(fasc.NoR_relative_position)
    return fasc


def crop_nerve(nerv: nerve, x0: float, new_l: float) -> nerve:
    """_summary_

    Parameters
    ----------
    nerv : nerve
        nerve to crop
    x0 : float
        x position of the begining of the new fascicle
    new_l : float
        length of the new fascicle

    Returns
    -------
    nerve
        nerve cropped
    """
    nerv.define_length(new_l)
    for fasc in nerv.fascicles.values:
        fasc = crop_fascicle(fasc, x0, new_l)
    return nerv
