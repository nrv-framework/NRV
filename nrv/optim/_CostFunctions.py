"""
NRV-:class:`.cost_function` handling.
"""

import numpy as np
from ..backend._NRV_Class import NRV_class, load_any
from ..backend._NRV_Simulable import NRV_simulable, sim_results
from ..backend._log_interface import rise_warning


class cost_function(NRV_class):
    """
    A class to define cost from position input vector

    Parameters
    ----------
    static_context      : str | dict
        saving dictionary or saving file name of a nrv_simulable object
        which should be use as static context of the optimisation
    context_modifier   : funct
        function creating a context from a particle position, parameters:
            >>> context_modifier(X: np.ndarray, static_context: NRV_simulable, **kwargs) -> NRV_simulable:
        returns
            context        : values of a context (array)
    cost_evaluation            : funct
        function calculating a cost from a axon simulation results, parameters:
            >>> cost_evaluation(results: sim_results, **kwargs) -> float:
    simulation  : funct
        optional
    kwargs_CM           : dict
        key word arguments of context_modifier function, by default {}
    kwargs_S           : dict
        key word arguments of simulate_context function, by default {}
    kwargs_CE            : dict
        key word arguments of cost_evaluation function, by default {}
    t_sim           : float
        time of the simulation on wich the cost will be calculated in ms (ms), by default 100ms
    dt              : float
        simulation time stem for neuron (ms), by default 1us
    filter         : funct or None
        function wich return a filtered postition from a position, if None, position is unfiltered,
        by default None
    saver         : funct or None
        function added at the end after calculating the cost for personalized savings, if None,
        nothing will be saved,  by default None
    """

    def __init__(
        self,
        static_context=None,
        context_modifier=None,
        cost_evaluation=None,
        simulation=None,
        kwargs_CM={},
        kwargs_S={},
        kwargs_CE={},
        filter=None,
        saver=None,
        file_name="cost_saver.csv",
        **kawrgs
    ):
        super().__init__()
        self.static_context = static_context
        self.context_modifier = context_modifier
        self.simulation = simulation
        self.cost_evaluation = cost_evaluation
        self.kwargs_CM = kwargs_CM
        self.kwargs_S = kwargs_S
        self.kwargs_CE = kwargs_CE
        self.filter = filter
        self.saver = saver
        self.file_name = file_name

        self.kwargs_CM.update(kawrgs)
        self.kwargs_S.update(kawrgs)
        self.kwargs_CE.update(kawrgs)

        self.simulation_context = None
        self.results = None
        self.cost = None

        # not ideal but prevent having multiple t_sim
        self.static_t_sim = 0
        self.global_t_sim = 0

        self._m_proc_CostFunction = None
        self.keep_results = False
        self.__check_mch()
        self.__synchronise_t_sim()

    ####################################
    ###### automating methods ##########
    ####################################
    def __clear_results(self):
        """
        clear result for re-use
        """
        del self.simulation_context
        del self.results
        self.simulation_context = None
        self.results = None

    @property
    def is_m_proc_func(self) -> bool:
        if self.static_context is not None and self._m_proc_CostFunction is None:
            static_context = load_any(self.static_context)
            self.static_t_sim = static_context.t_sim
            self._m_proc_CostFunction = static_context.nrv_type in ["fascicle", "nerve"]
        return self._m_proc_CostFunction

    def __check_mch(self):
        """
        check is the simulation will be handle in single or multiple cores
        """
        if self.static_context is not None and self._m_proc_CostFunction is None:
            static_context = load_any(self.static_context)
            self.static_t_sim = static_context.t_sim
            if static_context.nrv_type in ["fascicle", "nerve"]:
                self._m_proc_CostFunction = True
            del static_context

    def __synchronise_t_sim(self):
        if "t_sim" in self.kwargs_S:
            self.global_t_sim = self.kwargs_S["t_sim"]
        elif "t_sim" in self.kwargs_CM:
            self.global_t_sim = self.kwargs_CM["t_sim"]
        elif "t_sim" in self.kwargs_CE:
            self.global_t_sim = self.kwargs_CE["t_sim"]
        else:
            self.global_t_sim = self.static_t_sim

        self.kwargs_S["t_sim"] = self.global_t_sim
        self.kwargs_CM["t_sim"] = self.global_t_sim
        self.kwargs_CE["t_sim"] = self.global_t_sim
        pass

    @property
    def __cost_function_ok(self):
        s_status = []
        if self.static_context is None:
            s_status += ["static_context"]
        if self.context_modifier is None:
            s_status += ["context_modifier"]
        if self.cost_evaluation is None:
            s_status += ["cost_evaluation"]
        if len(s_status) == 0:
            return True
        else:
            rise_warning(
                "Cost function cannot be called because the following parameters are not defined: ",
                s_status,
            )
            return False

    ## Setters
    def set_static_context(self, static_context: str | dict, **kwgs):
        """
        set the cost static_context after the instantiation


        Parameters
        ----------
        static_context      : str | dict
            saving dictionary or saving file name of a nrv_simulable object
            which should be use as static context of the optimisation
        """
        self.static_context = static_context
        self.kwargs_S = kwgs
        self.__check_mch()
        self.__synchronise_t_sim()

    def set_context_modifier(self, context_modifier: callable, **kwgs):
        """
        set the cost context modifier after the instantiation

        Parameters
        ----------
        context_modifier   : funct
            function creating a context from a particle position, parameters:
                >>> context_modifier(X: np.ndarray, static_context: NRV_simulable, **kwargs) -> NRV_simulable:
        """
        self.context_modifier = context_modifier
        self.kwargs_CM = kwgs
        self.__synchronise_t_sim()

    def set_cost_evaluation(self, cost_evaluation: callable, **kwgs):
        """
        set the cost evalutation function after the instantiation

        Parameters
        ----------
        cost_evaluation            : funct
            function calculating a cost from a axon simulation results, parameters:
                >>> cost_evaluation(results: sim_results, **kwargs) -> float:
        """
        self.cost_evaluation = cost_evaluation
        self.kwargs_CE = kwgs
        self.__synchronise_t_sim()

    def simulate_context(self):
        ## See what's the use of simulation
        if callable(self.simulation):
            results = self.simulation(self.simulation_context, **self.kwargs_S)
        if self.simulation is None:
            # if not pr
            if "return_parameters_only" not in self.kwargs_S:
                self.kwargs_S["return_parameters_only"] = False
            if "save_results" not in self.kwargs_S:
                self.kwargs_S["save_results"] = False
            results = self.simulation_context(**self.kwargs_S)
        return results

    #############################
    ###### Call method ##########
    #############################
    def get_sim_results(self, X: np.ndarray) -> sim_results:
        """
        Simulated the static context modified with the tuning paramters X

        Note
        ----
        This method follows the same step than when the cost function is called without evaluating the cost, simulation results is returned insteat

        Parameters
        ----------
        X : np.ndarray
            tunning parameters of the simulation which will be evaluated by the cost function

        Returns
        -------
        sim_results
            Simulation results of the static context modified with the tuning paramters X
        """
        self.keep_results = True

        if self.filter is not None:
            X_ = self.filter(X)
        else:
            X_ = X

        # Interpolation
        self.simulation_context = self.context_modifier(
            X_, self.static_context, **self.kwargs_CM
        )
        # Simulation
        results = self.simulate_context()
        self.__clear_results()
        return results

    def __call__(self, X: np.ndarray) -> float:
        """
        When called cost function evaluate the impact of tuning
        parameters X on static context and evaluate a cost from the simulation results using
        cost_evaluation

        Parameters
        ----------
        X : np.ndarray
            tunning parameters of the simulation which will be evaluated by the cost function

        Returns
        -------
        float
            cost corresponding to the input parameter
        """
        # Filter
        if self.filter is not None:
            X_ = self.filter(X)
        else:
            X_ = X

        # Interpolation
        self.simulation_context = self.context_modifier(
            X_, self.static_context, **self.kwargs_CM
        )

        # Simulation
        self.results = self.simulate_context()

        # Cost calculation
        self.cost = self.cost_evaluation(self.results, **self.kwargs_CE)
        # Savings
        if self.saver is not None:
            data = {
                "position": X,
                "context": self.simulation_context,
                "results": self.results,
                "cost": self.cost,
            }
            self.saver(data, file_name=self.file_name)
        if not self.keep_results:
            self.__clear_results()
        return self.cost
