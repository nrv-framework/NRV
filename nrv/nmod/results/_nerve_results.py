"""
NRV-:class:`.nerve_results` handling.
"""

from ...backend._NRV_Results import sim_results
from ._fascicles_results import fascicle_results
from ._axons_results import axon_results
from ...backend._log_interface import rise_error, rise_warning, pass_info
from ...utils._units import nm, convert, from_nrv_unit
from ...utils._misc import membrane_capacitance_from_model


import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, concat


def number_in_str(s: str) -> bool:
    return any(i.isdigit() for i in s)


class nerve_results(sim_results):
    """ """

    def __init__(self, context=None):
        super().__init__(context)
        self._axons: DataFrame = DataFrame()

    @property
    def fascicle_keys(self) -> list:
        """
        Number of fascicles in the fascicle
        """
        all_keys = self.keys()
        return [i for i in all_keys if ("fascicle" in i and number_in_str(i))]

    @property
    def n_fasc(self) -> int:
        """
        Number of fascicles in the fascicle
        """
        return len(self.fascicles)

    @property
    def n_ax(self) -> int:
        """
        Number of axons in the fascicle
        """
        fasc_keys = self.fascicle_keys
        _n_ax = 0
        for key in fasc_keys:
            _n_ax += self[key].n_ax
        return _n_ax

    @property
    def axons_type(self) -> np.ndarray:
        """
        type of axons of each fascicles

        Returns
        -------
        np.ndarray (self.n_ax, 2)
            _description_
        """
        return self.axons_pop_properties[:, [0, 2]]

    @property
    def fasc_properties(self) -> np.ndarray:
        """
        Porperties of axons population of each fascicles

        Returns
        -------
        np.ndarray (self.n_ax, 6)
            ndarray gathering, for all fascicles in the nerve, fascicle IDs, diameter and y and z positions.
        """
        fasc_keys = self.fascicle_keys
        _fasc = np.zeros((self.n_fasc, 4))
        for i_fasc, key in enumerate(fasc_keys):
            fasc_ = self[key]
            _fasc[i_fasc, :] = np.array(
                [
                    fasc_.ID,
                    fasc_.geom.radius * 2,
                    fasc_.geom.y,
                    fasc_.geom.z,
                ]
            )
        return _fasc

    @property
    def fasc_geometries(self) -> dict:
        """
        Porperties of axons population of each fascicles

        Returns
        -------
        np.ndarray (self.n_ax, 6)
            ndarray gathering, for all fascicles in the nerve, fascicle IDs, diameter and y and z positions.
        """
        fasc_keys = self.fascicle_keys
        _fasc_geom = {}
        for i_fasc, key in enumerate(fasc_keys):
            _fasc = self[key]
            _fasc_geom[str(_fasc.ID)] = _fasc.geom
        return _fasc

    @property
    def axons_pop_properties(self) -> np.ndarray:
        """
        Porperties of axons population of each fascicles


        Returns
        -------
        np.ndarray (self.n_ax, 6)
            ndarray gathering, for all axons in the nerve, corresponding fascicle and axon IDs, myelinating type, diameter and y and z positions.
        """
        fasc_keys = self.fascicle_keys
        _mye = np.zeros((self.n_ax, 6))
        _offset = 0
        for key in fasc_keys:
            fasc_n_ax = self[key].n_ax
            fasc_axons = np.vstack(
                (
                    self[key].ID * np.ones(fasc_n_ax),
                    np.arange(fasc_n_ax),
                    self[key].axons[["types", "diameters", "y", "z"]].to_numpy(),
                )
            ).T
            _mye[_offset : _offset + fasc_n_ax, :] = fasc_axons
            _offset += fasc_n_ax
        return _mye

    @property
    def axons(self) -> np.ndarray:
        """
        Porperties of axons population of each fascicles


        Returns
        -------
        np.ndarray (self.n_ax, 6)
            ndarray gathering, for all axons in the nerve, corresponding fascicle and axon IDs, myelinating type, diameter and y and z positions.
        """
        if self._axons.empty:
            fasc_keys = self.fascicle_keys
            for key in fasc_keys:
                _ax_pop = self[key].axons.axon_pop
                _ax_pop["fkey"] = [key for _ in range(len(_ax_pop))]
                self._axons = concat((self._axons, _ax_pop))
                print(self[key].axons.axon_pop.keys())
        return self._axons

    def get_fascicle_results(self, ID: int) -> fascicle_results:
        if ID not in self.fascicles_IDs:
            rise_error(("Fascicle ID does not exists."))
        else:
            return self[f"fascicle{ID}"]

    def get_axon_results(self, fasc_ID: int, ax_ID: int) -> axon_results:
        fasc_ID = int(fasc_ID)
        ax_ID = int(ax_ID)
        if fasc_ID not in self.fascicles_IDs:
            rise_error(f"Fascicle ID: {fasc_ID} does not exists.")
        else:
            if ax_ID >= self[f"fascicle{fasc_ID}"].n_ax:
                rise_error(f"Axon ID: {ax_ID} does not exists in Fascicle {fasc_ID} .")
            else:
                return self[f"fascicle{fasc_ID}"][f"axon{ax_ID}"]

    def get_fascicle_key(self) -> list:
        all_keys = self.keys()
        fascicle_keys = [i for i in all_keys if ("fascicle" in i and number_in_str(i))]
        return fascicle_keys

    def get_recruited_axons(
        self, ax_type: str = "all", normalize: bool = False
    ) -> int | float:
        """
        Return the number or the ratio of recruited axons in the nerve

        Parameters
        ----------
        diam : float
            diameter above wich axon should be counted.
        ax_type : str, optional
            type of axon counted,possible options:
             - "all" (default)
             - "unmyelinated"
             - "myelinated"
        normalize : bool, optional
            if False the total number of recruited axons is returned, else the ratio is returned, by default False

        Returns
        -------
        float
            number of recruited axons
        """
        fasc_keys = self.fascicle_keys
        n_recr = 0
        for key in fasc_keys:
            fasc_res = self[key]
            n_recr += fasc_res.get_recruited_axons(ax_type=ax_type, normalize=normalize)
        if normalize:
            n_recr /= self.n_fasc
        return n_recr

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
        f_keys = self.get_fascicle_key()
        for key in f_keys:
            g_ = self[key].get_membrane_conductivity(x=x, t=t, unit=unit, mem_th=mem_th)
            if g_ is not None:
                g = np.concatenate((g, g_))
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
        Y = []
        f_keys = self.get_fascicle_key()
        for key in f_keys:
            Y_ = self[key].get_membrane_complexe_admitance(
                f=f, x=x, t=t, unit=unit, mem_th=mem_th
            )
            if Y_ is not None:
                Y = np.concatenate((Y, Y_))
            else:
                return None
        return Y

    ## Representation methods
    def plot_recruited_fibers(
        self,
        axes: plt.axes,
        contour_color: str = "k",
        myel_color: str = "b",
        unmyel_color: str = "r",
        elec_color: str = "gold",
        num: bool = False,
        **kwgs,
    ):
        """ """
        ## plot contour
        axes.add_patch(
            plt.Circle(
                (self.y_grav_center, self.z_grav_center),
                self.D / 2,
                color=contour_color,
                fill=False,
                linewidth=4,
            )
        )
        fasc_keys = self.get_fascicle_key()
        for key in fasc_keys:
            fasc_res = self[key]
            fasc_res.plot_recruited_fibers(
                axes=axes,
                contour_color="grey",
                myel_color=myel_color,
                unmyel_color=unmyel_color,
                num=num,
            )

        if "extra_stim" in self:
            if self.extra_stim is not None:
                self.extra_stim.plot(axes=axes, color=elec_color, nerve_d=self.D)
        axes.set_xlim((-1.1 * self.D / 2, 1.1 * self.D / 2))
        axes.set_ylim((-1.1 * self.D / 2, 1.1 * self.D / 2))
