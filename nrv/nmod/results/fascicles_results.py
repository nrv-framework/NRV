"""
NRV-:class:`.fascicle_results` handling.
"""


from ...backend.NRV_Results import sim_results
from ...backend.log_interface import pass_info, rise_warning, rise_error
from ...backend.MCore import MCH
from ...fmod.electrodes import is_FEM_electrode
import matplotlib.pyplot as plt
import numpy as np


def number_in_str(s: str) -> bool:
    return any(i.isdigit() for i in s)

recognized_axon_types = ['all','myelinated','unmyelinated']
class fascicle_results(sim_results):
    """

    
    """
    def __init__(self, context=None):
        super().__init__(context)

    def get_axons_key(self, type:str = 'all') -> list:
        """

        """
        if (type not in recognized_axon_types):
            rise_error(f"Axon type specified not recognized. Recognized types are: {recognized_axon_types}")
        all_keys = self.keys()
        axon_keys = [ i for i in all_keys if ("axon" in i and number_in_str(i)) ]
        if type is not 'all':
            if type is 'unmyelinated':
                axon_keys = [ i for i in axon_keys if i.myelinated == False]
            else:
                axon_keys = [ i for i in axon_keys if i.myelinated == True]
        return(axon_keys)


    def get_recruited_axons(self, type:str = 'all') -> float:
        """

        """
        axons_keys = self.get_axons_key(type)
        n_recr = 0
        for axon in axons_keys:
            if (self[axon].is_recruited()):
                n_recr=+1
        return(n_recr/len(axons_keys))
    
    def get_recruited_axons_greater_than(self, diam:float, type:str = 'all') -> float:
        axons_keys = self.get_axons_key(type)
        n_recr = 0
        for axon in axons_keys:
            if (self[axon].is_recruited() and self[axon].diameter>diam):
                n_recr=+1
        return(n_recr/len(axons_keys))
    
    def get_recruited_axons_lesser_than(self, diam:float, type:str = 'all') -> float:
        axons_keys = self.get_axons_key(type)
        n_recr = 0
        for axon in axons_keys:
            if (self[axon].is_recruited() and self[axon].diameter<=diam):
                n_recr=+1
        return(n_recr/len(axons_keys))
            

    def get_axons(self) -> list: 
        axons_keys = self.get_axons_key()
        axon_diam = []
        axon_type = []
        axon_y = []
        axon_z = []
        axon_recruited = [] 
        for axon in axons_keys:
            axon_recruited.append(self[axon].is_recruited())
            axon_y.append(self[axon].y)
            axon_z.append(self[axon].z)
            axon_diam.append(self[axon].diameter)
            axon_type.append(self[axon].myelinated)
        return(axon_diam,axon_type,axon_y,axon_z,axon_recruited)


    ## Representation methods
    def plot_recruited_fibers(
        self, axes:plt.axes, contour_color:str="k", myel_color:str="r", unmyel_color:str="b", num:bool=False
    )->None:
        if MCH.do_master_only_work():
            ## plot contour
            axes.add_patch(plt.Circle((self.y_grav_center, self.z_grav_center),self.D/2,
                                        color=contour_color,fill=False,linewidth=2,))
            ## plot axons
            axon_diam,axon_type,axon_y,axon_z,axon_recruited = self.get_axons()
            for k,_ in enumerate(axon_diam):
                color = unmyel_color
                if axon_type[k]:
                    color = myel_color
                alpha = 0.1
                if (axon_recruited[k]):
                    alpha = 1
                axes.add_patch(plt.Circle((axon_y[k], axon_z[k]),axon_diam[k] / 2,
                                color=color,fill=True,alpha = alpha,))

            if self.extra_stim is not None:
                for electrode in self.extra_stim.electrodes:
                    if electrode.type == "LIFE":
                        axes.add_patch(plt.Circle((electrode.y, electrode.z),
                                electrode.D / 2,color="gold",fill=True,))
                    elif not is_FEM_electrode(electrode):
                        axes.scatter(electrode.y, electrode.z, color="gold")
            if num:
                for k in range(self.n_ax):
                    axes.text(self.axons_y[k], self.axons_z[k], str(k))
            axes.set_xlim((-1.1*self.D/2+self.y_grav_center, 1.1*self.D/2+self.y_grav_center))
            axes.set_ylim((-1.1*self.D/2+self.z_grav_center, 1.1*self.D/2+self.z_grav_center))
