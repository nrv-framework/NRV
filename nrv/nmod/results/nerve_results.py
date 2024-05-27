"""
NRV-:class:`.nerve_results` handling.
"""


from ...backend.NRV_Results import sim_results
from .fascicles_results import fascicle_results
from ...backend.log_interface import rise_error, rise_warning, pass_info
from ...backend.MCore import MCH
from ...utils.units import nm, convert, from_nrv_unit
from ...utils.misc import membrane_capacitance_from_model


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


    # impeddance related methods
    def get_membrane_conductivity(self, x:float=0, t:float=0, unit:str="S/cm**2", mem_th:float=7*nm)->np.array:
        """
        get the membran conductivity of each axon at a position x and a time t

        Parameters
        ----------
        x : float, optional
            x-position in um where to get the conductivity, by default 0
        t : float, optional
            simulation time in ms when to get the conductivity, by default 0
        unit : str, optional
            unit of the returned conductivity see `units`, by default "S/cm**2"
        mem_th : float, optional
            membrane thickness in um, by default 7*nm

        Note
        ----
        depending of the unit parameter this function either return :

            - the surface conductivity in [S]/([m]*[m]): from neuron simulation
            - the conductivity in [S]/[m]:  by multiplying surface conductivity by membrane thickness
        """

        g = []
        f_keys = self.get_fascicle_key()
        for key in f_keys:
            g_ = self[key].get_membrane_conductivity(x=x, t=t, unit=unit, mem_th=mem_th)
            if g_ is not None:
                g = np.concatenate((g,g_))
            else:
                return None
        return g

    def get_membrane_capacitance(self, unit:str="uF/cm**2", mem_th:float=7*nm)->tuple[float]:
            """
            get the membrane capacitance or permitivity of unmyelinated and myelinated axons filling the ner

            Parameters
            ----------
            unit : str, optional
                unit of the returned conductivity see `units`, by default "S/cm**2"
            mem_th : float, optional
                membrane thickness in um, by default 7*nm

            Note
            ----
            depending of the unit parameter this function either return :

                - the surface conductivity in [S]/([m]*[m]): from neuron simulation
                - the conductivity in [S]/[m]:  by multiplying surface conductivity by membrane thickness
            """
            u_c_mem = membrane_capacitance_from_model(self.unmyelinated_param["model"])
            m_c_mem = membrane_capacitance_from_model(self.myelinated_param["model"])

            # Surface capacity in [F]/([m]*[m])
            if "2" in unit:
                return convert(u_c_mem, "S/cm**2", unit), convert(m_c_mem, "S/cm**2", unit)
            # permitivity in [F]/[m]
            else:
                u_c_mem *= from_nrv_unit(mem_th, "cm")
                m_c_mem *= from_nrv_unit(mem_th, "cm")
                return convert(u_c_mem, "S/cm", unit), convert(m_c_mem, "S/cm", unit)


    def get_membrane_complexe_admitance(self, f:float=1., x:float=0, t:float=0, unit:str="S/m", mem_th:float=7*nm)->np.array:
        """
        get the membran complexe admitance of each axon at a position x and a time t for a given frequency

        Parameters
        ----------
        f : float or np.array, optional
            effective frequency in kHz, by default 1
        x : float, optional
            x-position in um where to get the conductivity, by default 0
        t : float, optional
            simulation time in ms when to get the conductivity, by default 0
        unit : str, optional
            unit of the returned conductivity see `units`, by default "S/cm**2"
        mem_th : float, optional
            membrane thickness in um, by default 7*nm
        """
        Y = []
        f_keys = self.get_fascicle_key()
        for key in f_keys:
            Y_ = self[key].get_membrane_complexe_admitance(f=f, x=x, t=t, unit=unit, mem_th=mem_th)
            if Y_ is not None:
                Y = np.concatenate((Y,Y_))
            else:
                return None
        return Y