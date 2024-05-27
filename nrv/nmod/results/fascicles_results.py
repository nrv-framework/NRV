"""
NRV-:class:`.fascicle_results` handling.
"""


from ...backend.NRV_Results import sim_results
from ...backend.log_interface import pass_info, rise_warning, rise_error
from ...backend.MCore import MCH
from ...fmod.electrodes import is_FEM_electrode
from ...utils.units import nm, convert, from_nrv_unit, to_nrv_unit
from ...utils.misc import membrane_capacitance_from_model, compute_complex_admitance
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

    def get_axons_key(self, ax_type:str = 'all') -> list:
        """

        """
        if (ax_type not in recognized_axon_types):
            rise_error(f"Axon type specified not recognized. Recognized types are: {recognized_axon_types}")
        all_keys = self.keys()
        axon_keys = [ i for i in all_keys if ("axon" in i and number_in_str(i)) ]
        if ax_type is not 'all':
            if ax_type is 'unmyelinated':
                axon_keys = [ i for i in axon_keys if self[i].myelinated == False]
            else:
                axon_keys = [ i for i in axon_keys if self[i].myelinated == True]
        return(axon_keys)



    def get_recruited_axons(self, ax_type:str = 'all') -> float:
        """

        """
        axons_keys = self.get_axons_key(ax_type)
        n_recr = 0
        for axon in axons_keys:
            if (self[axon].is_recruited()):
                n_recr+=1
        return(n_recr/len(axons_keys))
    
    def get_recruited_axons_greater_than(self, diam:float, ax_type:str = 'all') -> float:
        axons_keys = self.get_axons_key(ax_type)
        n_recr = 0
        for axon in axons_keys:
            if (self[axon].is_recruited() and self[axon].diameter>diam):
                n_recr=+1
        return(n_recr/len(axons_keys))
    
    def get_recruited_axons_lesser_than(self, diam:float, ax_type:str = 'all') -> float:
        axons_keys = self.get_axons_key(ax_type)
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

    def n_ax(self):
        """
        Number of axons in the fascicle
        """
        return len(self.axons_diameter)

    ## Representation methods
    def plot_recruited_fibers(
        self, axes:plt.axes, contour_color:str="k", myel_color:str="r", unmyel_color:str="b", num:bool=False
    ) -> None:
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
                self.extra_stim.plot(axes=axes, color="gold", nerve_d=self.D)
            if num:
                for k in range(self.n_ax):
                    axes.text(self.axons_y[k], self.axons_z[k], str(k))
            axes.set_xlim((-1.1*self.D/2+self.y_grav_center, 1.1*self.D/2+self.y_grav_center))
            axes.set_ylim((-1.1*self.D/2+self.z_grav_center, 1.1*self.D/2+self.z_grav_center))


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
        a_keys = self.get_axons_key()
        for key in a_keys:
            g_ = self[key].get_membrane_conductivity(x=x, t=t, unit=unit, mem_th=mem_th)
            if g_ is not None:
                g = np.concatenate((g,[g_]))
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

            - the surface capacitance in [S]/([m]*[m]): from neuron simulation
            - the permitivity in [S]/[m]:  by multiplying surface conductivity by membrane thickness
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
        u_c, m_c = self.get_membrane_capacitance(mem_th=mem_th)
        eps = (self.axons_type * (m_c - u_c)) + u_c
        g = self.get_membrane_conductivity(x=x, t=t, mem_th=mem_th)
        f_mem = g/(2*np.pi*eps)

        # in [MHz] as g_mem in [S/cm^{2}] and c_mem [uF/cm^{2}]
        # [MHz] to convert to [kHz]
        f_mem = to_nrv_unit(f_mem, "MHz")

        Y = compute_complex_admitance(f=f, g=g, fc=f_mem)

        if "2" in unit:
            return convert(Y, "S/cm**2", unit)
        # permitivity in [F]/[m]
        else:
            Y *= from_nrv_unit(mem_th, "cm")
            return convert(Y, "S/cm", unit)