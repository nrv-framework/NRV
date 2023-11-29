from ..backend.NRV_Class import NRV_class, load_any
from ..backend.NRV_Simulable import NRV_simulable
from ..backend.MCore import MCH, synchronize_processes

class CostFunction(NRV_class):
    """
    A class to define cost from position input vector

    Parameters
    ----------
    context_modifier   : funct
        function creating a context from a particle position, parameters:
            position        : particle position in each dimensions (array)
            t_sim           : simulation time (float)
            dt              : time step of the context (float)
            kwargs          : keys word arguments
        returns
            context        : values of a context (array)
    simulate_context   : funct
        function which perform the NEURON simulation, parameters:
            context        : context to use for the simulation (array)
            t_sim           : simulation time (float)
            dt              : time step of the context (float)
            kwargs          : keys word arguments
        returns
            results        : axon simulaiton results (dictionary)
    cost_evaluation            : funct
        function calculating a cost from a axon simulation results, parameters:
            results        : axon simulaiton results (dictionary)
            kwargs          : keys word arguments
        returns
            cost              : cost evaluation value (float)
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
    part_filter         : funct or None
        function wich return a filtered postition from a position, if None, position is unfiltered,
        by default None
    saver         : funct or None
        function added at the end after calculating the cost for personalized savings, if None,
        nothing will be saved,  by default None

    """

    def __init__(
        self,
        static_context,
        context_modifier,
        cost_evaluation,
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

        self._MCore_CostFunction = False
        self.__check_cost_function()

    def __clear_results(self):
        del self.simulation_context
        del self.results
        self.simulation_context = None
        self.results = None

    def __check_cost_function(self):
        static_contect = load_any(self.static_context)
        if (
            not MCH.is_alone() and
            static_contect.nrv_type in ["fascicle","nerve"]
        ):
            self._MCore_CostFunction = True
        del static_contect

    def simulate_context(self):
        if callable(self.simulation):
            results = self.simulation(self.simulation_context, **self.kwargs_S)
        if self.simulation is None:
            if "return_parameters_only" not in self.kwargs_S:
                self.kwargs_S["return_parameters_only"] = False
            results = self.simulation_context(**self.kwargs_S)
        return results

    def __call__(self, X):
        # Broadcasting to slave wich are waiting for simulation
        if MCH.do_master_only_work() and self._MCore_CostFunction:
            slave_status = {"status": "Simulate", "X":X}
            MCH.master_broadcasts_array_to_all(slave_status)
        if self._MCore_CostFunction:
            synchronize_processes()

        # Filter
        if self.filter is not None:
            X_ = self.filter(X)
        else:
            X_ = X

        # Interpolation
        self.simulation_context = self.context_modifier(X_, self.static_context, **self.kwargs_CM)

        # Simulation
        self.results = self.simulate_context()
        if MCH.do_master_only_work() or not self._MCore_CostFunction:
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
            self.__clear_results()
            return self.cost
        else:
            return 0
