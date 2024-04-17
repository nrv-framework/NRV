"""
NRV-:class:`.nerve_results` handling.
"""


from ...backend.NRV_Results import sim_results
from .fascicles_results import fascicle_results
from ...backend.log_interface import rise_error, rise_warning, pass_info
from ...backend.MCore import MCH

import matplotlib.pyplot as plt
import numpy as np


def number_in_str(s: str) -> bool:
    return any(i.isdigit() for i in s)

class nerve_results(sim_results):
    """

    """

    def __init__(self, context=None):
        super().__init__(context)


    def get_fascicle_results(self, ID: int) -> fascicle_results:
        if ID not in self.fascicles_IDs:
            rise_error(("Fascicle ID does not exists."))
        else:
            return(self[f'fascicle{ID}'])


    def get_fascicle_key(self) ->list:
        all_keys = self.keys()
        fascicle_keys = [ i for i in all_keys if ("fascicle" in i and number_in_str(i)) ]
        return(fascicle_keys)


    ## Representation methods
    def plot_recruited_fibers(
        self, axes:plt.axes, contour_color:str="k", myel_color:str="r", unmyel_color:str="b", elec_color:str="gold",num:bool=False, **kwgs
    ):
        """

        """
        if MCH.do_master_only_work():
            ## plot contour
            axes.add_patch(plt.Circle((self.y_grav_center, self.z_grav_center),self.D/2,color=contour_color,
                                fill=False,linewidth=4,))
            fasc_keys = self.get_fascicle_key()
            for key in fasc_keys:
                fasc_res = self[key]
                fasc_res.plot_recruited_fibers(axes=axes,contour_color="grey",
                    myel_color=myel_color,unmyel_color=unmyel_color,num=num,)
            if self.extra_stim is not None:
                self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.D)
            axes.set_xlim((-1.1*self.D/2, 1.1*self.D/2))
            axes.set_ylim((-1.1*self.D/2, 1.1*self.D/2))