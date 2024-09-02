import numpy as np

from ...utils._stimulus import stimulus, set_common_time_series
from ...fmod._extracellular import extracellular_context

from ...backend._NRV_Class import NRV_class, load_any, abstractmethod
from ...backend._NRV_Simulable import sim_results
from ...nmod.results._axons_results import axon_results
from ...nmod.results._fascicles_results import fascicle_results
from ...nmod.results._nerve_results import nerve_results
from ...utils._nrv_function import cost_evaluation
from ...ui._axon_postprocessing import *


class raster_count_CE(cost_evaluation):
    """
    Create a callable object which returne the number of spike from the result
    of a simulation
    """

    def __init__(self):
        super().__init__()

    def call_method(self, results: sim_results, **kwargs) -> float:
        """
        Returns the spike number from a simulation result
        """
        if "V_mem_raster_position" not in results:
            results.rasterize("V_mem")
        pos = results["V_mem_raster_position"]
        M = len(results["x_rec"]) - 1  # pos starts at 0
        i_first_pos = np.where(pos == 0)
        i_last_pos = np.where(pos == M)
        cost = (len(i_first_pos[0]) + len(i_last_pos[0])) / 2
        return cost


class recrutement_count_CE(cost_evaluation):
    r"""
    Callable object which returns the number of triggered fibre in the results

    Parameters
    ----------
    reverse     : bool
        if True, the final cost is the difference between the number total of fibre and the number of activate fibre

    Note
    ----
    if reverse is false:

    .. math::

        cost = N_{recruited}

    else:

    .. math::

        cost = N_{total} - N_{recruited}
    """

    def __init__(self, reverse=False):
        super().__init__()
        self.reverse = reverse

    def count_axon_activation(self, results: sim_results):
        cpt = results.is_recruited()
        if self.reverse:
            cpt = not cpt
        return int(cpt)

    def count_fascicle_activation(self, results: sim_results):
        cpt = 0
        for i in range(len(results["axons_diameter"])):
            if self.reverse:
                cpt += 1 - results["axon" + str(i)]["spike"]
            else:
                cpt += results["axon" + str(i)]["spike"]
        return cpt

    def call_method(self, results: sim_results, **kwargs) -> float:
        """
        Returns the spike number from a simulation result

        Parameters
        ----------
        results     : dict
            output of an axon simulation using Markov model for at least a node

        Returns
        -------
        cost        :int
            number of spike in the v_mem part
        """
        cost = 0
        if isinstance(results, axon_results):
            cost = self.count_axon_activation(results)
        else:
            cost = results.get_recruited_axons(ax_type="all", normalize=False)
            if self.reverse:
                cost = results.n_ax - cost
        return cost


class charge_quantity_CE(cost_evaluation):
    r"""
    Create a callable object which return a value proportionnal to the charge quantity injected by stimulus.

    .. math::

        cost = \sum_{e}\sum_{t_k}{i_{e,stim}(t_k)}

    with :math:`t_k` is the discrete time step of the simulation
    """

    def __init__(self, id_elec=None, dt_res=0.0001):
        super().__init__()
        self.id_elec = id_elec
        self.dt_res = dt_res

    def compute_stimulus_cost(self, stim: stimulus):
        stim_ = stimulus()
        t_min, t_max = stim.t[0], stim.t[-1]
        N_pts = int((t_max - t_min) // self.dt_res)
        stim_.t = np.linspace(t_min, t_max, N_pts)
        set_common_time_series(stim, stim_)
        return abs(stim).integrate()

    def call_method(self, results: sim_results, **kwargs) -> float:
        extra_stim = load_any(results["extra_stim"])
        N_elec = len(extra_stim.stimuli)
        cost = 0
        if self.id_elec is None:
            self.id_elec = [k for k in range(N_elec)]
        elif isinstance(self.id_elec, int):
            self.id_elec = [self.id_elec]
        for i in self.id_elec:
            cost += self.compute_stimulus_cost(extra_stim.stimuli[i])
        return cost


class stim_energy_CE(cost_evaluation):
    r"""
    Create a callable object which return a value proportionnal to the stimulus energy, assuming the electrode impedance is a constant.

    .. math::

        cost = \sum_{e}\sum_{t_k}{i_{e,stim}^2(t_k)}

    with :math:`t_k` is the discrete time step of the simulation

    Parameters
    ----------
    id_elec : None | int | list[int]
        id or list id of the electrode of the to from which the energy should be computed. If None,
    dt_res  : float
        resolotion time step use to compute the cost value
    """

    def __init__(self, id_elec: None | int | list[int] = None, dt_res: float = 0.0001):
        super().__init__()
        self.id_elec = id_elec
        self.dt_res = dt_res

    def compute_stimulus_cost(self, stim: stimulus):
        stim_ = stimulus()
        t_min, t_max = stim.t[0], stim.t[-1]
        N_pts = int((t_max - t_min) // self.dt_res)
        stim_.t = np.linspace(t_min, t_max, N_pts)
        set_common_time_series(stim, stim_)
        stim.s = stim.s * stim.s
        return abs(stim).integrate()

    def call_method(self, results: sim_results, **kwargs) -> float:
        extra_stim = load_any(results["extra_stim"])
        N_elec = len(extra_stim.stimuli)
        cost = 0
        if self.id_elec is None:
            self.id_elec = [k for k in range(N_elec)]
        elif isinstance(self.id_elec, int):
            self.id_elec = [self.id_elec]
        for i in self.id_elec:
            cost += self.compute_stimulus_cost(extra_stim.stimuli[i])
        return cost
