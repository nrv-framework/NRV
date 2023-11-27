from ..backend.NRV_Class import NRV_class
from ..backend.NRV_Simulable import NRV_simulable


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
    kwargs_gw           : dict
        key word arguments of context_modifier function, by default {}
    kwargs_sw           : dict
        key word arguments of simulate_context function, by default {}
    kwargs_r            : dict
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
        static_context:NRV_simulable,
        context_modifier,
        cost_evaluation,
        simulation=None,
        kwargs_gw={},
        kwargs_sw={},
        kwargs_r={},
        t_sim=None,
        dt=None,
        filter=None,
        saver=None,
        file_name="cost_saver.csv",
    ):
        super().__init__()
        #
        self.static_context = static_context
        self.context_modifier = context_modifier
        self.cost_evaluation = cost_evaluation
        self.kwargs_gw = kwargs_gw
        self.simulation = simulation
        self.kwargs_sw = kwargs_sw
        self.kwargs_r = kwargs_r
        self.filter = filter
        self.saver = saver
        self.file_name = file_name
        
        if t_sim is not None:
            self.kwargs_gw['t_sim'] = t_sim
            self.kwargs_sw['t_sim'] = t_sim
            self.kwargs_r['t_sim'] = t_sim
        if dt is not None:
            self.kwargs_gw['dt'] = dt
            self.kwargs_sw['dt'] = dt
            self.kwargs_r['dt'] = dt

        self.simulation_context = None
        self.results = None
        self.cost = None

    def __clear_results(self):
        del self.simulation_context
        del self.results
        self.simulation_context = None
        self.results = None

    def simulate_context(self):
        if callable(self.simulation):
            results = self.simulation(self.simulation_context, **self.kwargs_sw)
        if self.simulation is None:
            results = self.simulation_context(**self.kwargs_sw)
        return results

    def __call__(self, X):
        # Filter
        if self.filter is not None:
            X_ = self.filter(X)
        else:
            X_ = X

        # Interpolation
        self.simulation_context = self.context_modifier(X_, self.static_context, **self.kwargs_gw)

        # Simulation
        self.results = self.simulate_context()

        # Cost calculation
        self.cost = self.cost_evaluation(self.results, **self.kwargs_r)

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
