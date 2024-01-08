import numpy as np

from ...fmod.stimulus import stimulus, set_common_time_series
from ...fmod.extracellular import extracellular_context

from ...backend.NRV_Class import NRV_class, load_any, abstractmethod
from ...backend.NRV_Simulable import sim_results
from ...utils.nrv_function import CostEvaluation
from ...utils.cell.CL_postprocessing import *


class raster_count_CE(CostEvaluation):
    def __init__(self):
        """
        Create a callable object which returne the number of spike from the result
        of a simulation

        Parameters
        ----------
        results     : dict
            output of an axon simulation using Markov model for at least a node

        Returns
        -------
        cost        :int
            number of spike in the v_mem part
        """
        super().__init__()

    def call_method(self, results: sim_results, **kwargs) -> float:
        """
        Returns the spike number from a simulation result
        """
        if "V_mem_raster_position" not in results:
            rasterize(results, "V_mem")
        pos = results["V_mem_raster_position"]
        M = len(results["x_rec"]) - 1  # pos starts at 0
        i_first_pos = np.where(pos == 0)
        i_last_pos = np.where(pos == M)
        cost = (len(i_first_pos[0]) + len(i_last_pos[0])) / 2
        return cost


class charge_quantity_CE(CostEvaluation):
    def __init__(self, id_elec=None, dt_res=0.0001):
        """
        Create a callable object which return the charge injected

        Parameters
        ----------

        Returns
        -------

        """
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
        """ """
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


class stim_energy_CE(CostEvaluation):
    def __init__(self, id_elec=None, dt_res=0.0001):
        """
        Create a callable object which return a value proportionnal to the stimulus energy, assuming Zelec is a constant

        Parameters
        ----------

        Returns
        -------

        """
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
        """ """
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


class recrutement_count_CE(CostEvaluation):
    """
    Callable object which returns the number of activated fibre in the results

    Parameters
    ----------
    results     : dict
        output of an axon simulation using Markov model for at least a node

    Returns
    -------
    cost        :int
        number of spike in the v_mem part
    """

    def __init__(self, reverse=False):
        """
        Create a callable object which returns the number of activated fibre in the results

        Parameters
        ----------
        reverse     : bool
            output of an axon simulation using Markov model for at least a node

        """
        super().__init__()
        self.reverse = reverse

    def count_axon_activation(self, results: sim_results):
        if len(results["V_mem_raster_position"]) == 0:
            # no spike
            return 0
        else:
            return 1

    def count_fascicle_activation(self, results: sim_results):
        cpt = 0
        for i in range(results["N"]):
            if self.reverse:
                cpt += 1 - results["axon" + str(i)]["spike"]
            else:
                cpt += results["axon" + str(i)]["spike"]
        return cpt

    def call_method(self, results: sim_results, **kwargs) -> float:
        """
        Returns the spike number from a simulation result
        """
        cost = 0
        if "myelinated" in results["result_type"]:
            cost = self.count_axon_activation(results)
        elif results["result_type"] == "fascicle":
            cost = self.count_fascicle_activation(results)
        else:
            # nerve simulation
            for i in range(len(results["fascicles_IDs"])):
                cost += self.count_fascicle_activation(results["fascicle" + str(i)])
        return cost
