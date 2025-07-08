"""
NRV-:class:`.fascicle_results` handling.
"""

from ...backend._NRV_Results import sim_results
from ...backend._log_interface import pass_info, rise_warning, rise_error
from ...fmod._electrodes import is_FEM_electrode
from ...utils._units import nm, convert, from_nrv_unit, to_nrv_unit
from ...utils._misc import membrane_capacitance_from_model, compute_complex_admitance
from ...utils.geom import CShape
import matplotlib.pyplot as plt
import numpy as np
from typing import Literal


def number_in_str(s: str) -> bool:
    return any(i.isdigit() for i in s)


recognized_axon_types = ["all", "myelinated", "unmyelinated"]


class fascicle_results(sim_results):
    """ """

    def __init__(self, context=None):
        super().__init__(context)

    @property
    def n_ax(self) -> int:
        """
        Number of axons in the fascicle
        """
        return len(self.axons["diameters"])

    @property
    def geom(self) -> CShape:
        """
        Simulated fascicle geometry
        """
        return self.axons.geom

    def get_n_ax(self, ax_type: str = "all") -> int:
        """
        Number of myelinated axons in the fascicle
        """
        return len(self.get_axons_key(ax_type))

    def get_axons_key(self, ax_type: str = "all") -> list:
        """ """
        if ax_type not in recognized_axon_types:
            rise_error(
                f"Axon type specified not recognized. Recognized types are: {recognized_axon_types}"
            )
        all_keys = self.keys()
        axon_keys = [i for i in all_keys if ("axon" in i and number_in_str(i))]
        if ax_type != "all":
            if ax_type == "unmyelinated":
                axon_keys = [i for i in axon_keys if self[i].myelinated == False]
            else:
                axon_keys = [i for i in axon_keys if self[i].myelinated == True]
        return axon_keys

    def __compute_recruited_axons(
        self,
        vm_key: str = "V_mem",
        t_start: float = None,
        otype: None | Literal["list", "numpy"] = None,
    ) -> np.ndarray[bool]:
        """
        Check which of the axons are recruited, add "is_recruited" from
        """
        df_key = f"is_recruited_{vm_key}"
        if df_key not in self.axons.axon_pop:
            axons_keys = self.get_axons_key()
            axon_recruited = []
            for axon in axons_keys:
                axon_recruited.append(self[axon].is_recruited(vm_key, t_start))
            self.axons.add_mask(
                data=axon_recruited, label=df_key, mask_on=self.sim_mask
            )
        self.axons.add_mask(
            data=self.axons[df_key], label="is_recruited", mask_on=self.sim_mask
        )
        if otype is None:
            return self.axons["is_recruited"]
        else:
            return eval(f"self.axons['is_recruited'].to_{otype}()")

    def get_recruited_axons(
        self,
        ax_type: str = "all",
        normalize: bool = False,
        vm_key: str = "V_mem",
        t_start: float = None,
    ) -> int | float:
        """
        Return the number or the ratio of recruited axons in the fascicle

        Parameters
        ----------
        ax_type : str, optional
            type of axon counted,possible options:
             - "all" (default)
             - "unmyelinated"
             - "myelinated"
        normalize : bool, optional
            if False the total number of recruited axons is returned, else the ratio is returned, by default False

        Returns
        -------
        int or float
            number of recruited axons
        """
        axons_keys = self.get_axons_key(ax_type)
        n_recr = self.__compute_recruited_axons(vm_key, t_start).sum()
        if normalize:
            n_recr /= self.get_n_ax(ax_type)
        return n_recr

    def get_recruited_axons_greater_than(
        self,
        diam: float,
        ax_type: str = "all",
        normalize: bool = False,
        vm_key: str = "V_mem",
        t_start: float = None,
    ) -> float:
        """
        Return the number or the ratio of recruited axons with a diameter greater than `diam` in the fascicle

        Parameters
        ----------
        ax_type : str, optional
            type of axon counted, possible options:
                - "all" (default)
                - "unmyelinated"
                - "myelinated"
        normalize : bool, optional
            if False the total number of recruited axons is returned, else the ratio is returned, by default False

        Returns
        -------
        int or float
            number of recruited axons
        """
        axons_keys = self.get_axons_key(ax_type)
        n_recr = 0
        n_tot = 0
        for axon in axons_keys:
            if self[axon].diameter > diam:
                n_tot += 1
                if self[axon].is_recruited(vm_key, t_start):
                    n_recr += 1
        if normalize:
            n_recr /= n_tot
        return n_recr

    def get_recruited_axons_lesser_than(
        self,
        diam: float,
        ax_type: str = "all",
        normalize: bool = False,
        vm_key: str = "V_mem",
        t_start: float = None,
    ) -> float:
        """
        Return the number or the ratio of recruited axons with a diameter smaller than `diam` in the fascicle

        Parameters
        ----------
        ax_type : str, optional
            type of axon counted, possible options:
                - "all" (default)
                - "unmyelinated"
                - "myelinated"
        normalize : bool, optional
            if False the total number of recruited axons is returned, else the ratio is returned, by default False

        Returns
        -------
        int or float
            number of recruited axons
        """
        axons_keys = self.get_axons_key(ax_type)
        n_recr = 0
        n_tot = 0
        for axon in axons_keys:
            if self[axon].diameter < diam:
                n_tot += 1
                if self[axon].is_recruited(vm_key, t_start):
                    n_recr += 1
        if normalize:
            n_recr /= n_tot
        return n_recr

    def get_axons(self, vm_key: str = "V_mem", t_start: float = None) -> list:
        """
        Get simulated axons properties

        Parameters
        ----------
        vm_key : str, optional
            _description_, by default "V_mem"
        t_start : float, optional
            _description_, by default None

        Returns
        -------
        list
            _description_
        """
        _m = self.axons.get_mask(mask_labels=self.sim_mask)
        axon_diam = self.axons["diameters"][_m]
        axon_type = self.axons["types"][_m]
        axon_y = self.axons["y"][_m]
        axon_z = self.axons["z"][_m]
        axon_recruited = self.__compute_recruited_axons(
            vm_key=vm_key, t_start=t_start, otype="list"
        )
        return (axon_diam, axon_type, axon_y, axon_z, axon_recruited)

    def get_block_summary_axons(
        self, AP_start: float, freq: float = None, t_refractory: float = 1
    ) -> list:
        axons_keys = self.get_axons_key()
        _m = self.axons.get_mask(mask_labels=self.sim_mask)
        axon_diam = self.axons["diameters"][_m]
        axon_type = self.axons["types"][_m]
        axon_y = self.axons["y"][_m]
        axon_z = self.axons["z"][_m]
        is_blocked = []
        n_onset = []
        for axon in axons_keys:
            self[axon].block_summary(AP_start, freq, t_refractory)
            is_blocked.append(self[axon].is_blocked)
            n_onset.append(self[axon].n_onset)
        self.axons.add_mask(data=is_blocked, label="is_blocked", mask_on=self.sim_mask)
        self.axons.add_mask(data=n_onset, label="n_onset", mask_on=self.sim_mask)
        return (axon_diam, axon_type, axon_y, axon_z, is_blocked, n_onset)

    # impeddance related methods
    def get_membrane_conductivity(
        self, x: float = 0, t: float = 0, unit: str = "S/cm**2", mem_th: float = 7 * nm
    ) -> np.array:
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
                g = np.concatenate((g, [g_]))
            else:
                return None
        return g

    def get_membrane_capacitance(
        self, unit: str = "uF/cm**2", mem_th: float = 7 * nm
    ) -> tuple[float]:
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

    def get_membrane_complexe_admitance(
        self,
        f: float = 1.0,
        x: float = 0,
        t: float = 0,
        unit: str = "S/m",
        mem_th: float = 7 * nm,
    ) -> np.array:
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
        eps = (self.axons["types"] * (m_c - u_c)) + u_c
        g = self.get_membrane_conductivity(x=x, t=t, mem_th=mem_th)
        f_mem = g / (2 * np.pi * eps)

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

    def get_block_summary(
        self,
        AP_start: float,
        freq: float = None,
        t_refractory_m: float = 1,
        t_refractory_um: float = 1,
    ) -> None:
        """
        Get block characteristics (blocked, onset response, number of APs) for each axon of the fascicle

        Parameters
        ----------
        AP_start : float
            timestamp of the test pulse start, in ms.
        freq : float, optional
            Frequency of the stimulation, for KES block, by default None
        t_refractory_m : float, optional
            Axon refractory period for myelinated fibers, by default 1
        t_refractory_um : float, optional
            Axon refractory period for unmyelinated fibers, by default 1
        """
        axons_keys = self.get_axons_key()
        for axon in axons_keys:
            if self[axon].myelinated == True:
                self[axon].block_summary(AP_start, freq, t_refractory_m)
            else:
                self[axon].block_summary(AP_start, freq, t_refractory_um)

    ## Representation methods
    def plot_recruited_fibers(
        self,
        axes: plt.axes,
        contour_color: str = "k",
        myel_color: str = "b",
        unmyel_color: str = "r",
        num: bool = False,
    ) -> None:
        ## plot axons
        self.get_axons()

        self.axons.plot(
            axes=axes,
            mask_labels=[],
            contour_color=(contour_color, 0.1),
            myel_color=(myel_color, 0.1),
            unmyel_color=(unmyel_color, 0.1),
            num=num,
        )

        self.axons.plot(
            axes=axes,
            mask_labels=["is_recruited"],
            contour_color=(contour_color, 1),
            myel_color=(myel_color, 1),
            unmyel_color=(unmyel_color, 1),
            num=num,
        )

        if "extra_stim" in self:
            if self.extra_stim is not None:
                self.extra_stim.plot(
                    axes=axes, color="gold", nerve_d=2 * self.axons.geom.radius
                )
        if num:
            for k in range(self.n_ax):
                axes.text(
                    self.axons["y"][k],
                    self.axons["z"][k],
                    str(k),
                    horizontalalignment="center",
                    verticalalignment="center",
                )

    def plot_block_summary(
        self,
        axes: plt.axes,
        AP_start: float,
        freq: float = None,
        t_refractory: float = 1,
        contour_color: str = "k",
        num: bool = False,
    ) -> None:
        """
        plot the block_summary of the fascicle in the Y-Z plane (transverse section)
        Color code:
        Green: fiber is blocked without any onset
        Blue: fiber is blocked with some onset
        Red: fiber is not blocked but has onset
        Grey: Fiber is nor blocked nor has onset

        A cross-mark on the fiber means block state can't be evaluted (is_blocked returned None)
        Alpha colorfill represents number of onset APs.

        Parameters
        ----------
        axes    : matplotlib.axes
            axes of the figure to display the fascicle
        AP_start : float
            timestamp of the test pulse start, in ms.
        freq : float, optional
            Frequency of the stimulation, for KES block, by default None
        t_refractory : float, optional
            Axon refractory period for myelinated fibers, by default 1
        contour_color   : str
            matplotlib color string applied to the contour. Black by default
        num             : bool
            if True, the index of each axon is displayed on top of the circle
        """

        ## plot contour
        self.axons.plot(axes, myel_color=("b", 0.1), unmyel_color=("r", 0.1))
        ## plot axons
        axon_diam, _, axon_y, axon_z, is_blocked, n_onset = (
            self.get_block_summary_axons(
                AP_start=AP_start, freq=freq, t_refractory=t_refractory
            )
        )
        alpha_g = 1 / np.max(n_onset)

        # cmap = plt.get_cmap('viridis')
        # norm = plt.Normalize(min(n_onset), max(n_onset))
        # line_colors = cmap((n_onset))

        for k, _ in enumerate(axon_diam):
            if is_blocked[k] is not True:
                if n_onset[k] == 0:
                    c = "grey"
                    alpha = 0.5
                else:
                    c = "orangered"
                    alpha = n_onset[k] * alpha_g
                if is_blocked[k] is None:
                    axes.scatter(axon_y[k], axon_z[k], marker="x", s=20, c="k")

            else:
                if n_onset[k] == 0:
                    c = "seagreen"
                    alpha = 1
                else:
                    c = "steelblue"
                    alpha = n_onset[k] * alpha_g

            axes.add_patch(
                plt.Circle(
                    (axon_y[k], axon_z[k]),
                    axon_diam[k] / 2,
                    color=c,
                    fill=True,
                    alpha=alpha,
                )
            )

        if self.extra_stim is not None:
            self.extra_stim.plot(axes=axes, color="gold", nerve_d=self.geom.radius * 2)
        if num:
            for k in range(self.n_ax):
                axes.text(
                    self.axons["y"][k], self.axons["z"][k], str(k)
                )  # horizontalalignment='center',verticalalignment='center')
