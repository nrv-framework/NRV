from ..backend.log_interface import rise_error, rise_warning, pass_info
from ..backend.file_handler import json_dump
from ..backend.NRV_Class import NRV_class, load_any

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
    residual            : funct
        function calculating a residual from a axon simulation results, parameters:
            results        : axon simulaiton results (dictionary)
            kwargs          : keys word arguments
        returns
            cost              : residual value (float)
    kwargs_gw           : dict
        key word arguments of context_modifier function, by default {}
    kwargs_sw           : dict
        key word arguments of simulate_context function, by default {}
    kwargs_r            : dict
        key word arguments of residual function, by default {}
    t_sim           : float
        time of the simulation on wich the residual will be calculated in ms (ms), by default 100ms
    dt              : float
        simulation time stem for neuron (ms), by default 1us
    part_filter         : funct or None
        function wich return a filtered postition from a position, if None, position is unfiltered,
        by default None
    saver         : funct or None
        function added at the end after calculating the cost for personalized savings, if None,
        nothing will be saved,  by default None

    """
    def __init__(self, static_context, context_modifier, residual, kwargs_gw={}, simulate_context = None,
        kwargs_sw={}, kwargs_r={}, t_sim=100, dt=0.005, filter=None, saver=None, 
        file_name='cost_saver.csv'):
        self.static_context = static_context
        self.context_modifier = context_modifier
        #self.simulate_context = simulate_context
        self.residual = residual
        self.kwargs_gw = kwargs_gw
        self.kwargs_sw = kwargs_sw
        self.kwargs_r = kwargs_r
        self.t_sim = t_sim
        self.dt = dt
        self.filter = filter
        self.saver = saver
        self.file_name = file_name

    def simulate_context(self, context):
        print('pioup')
        results = context.simulate(t_sim = self.t_sim, loaded_footprints=True)
        return results

    def __call__(self, X):
        # Filter
        if self.filter is not None:
            X_ = self.filter(X)
        else:
            X_ = X

        # Interpolation
        simulation_context = self.context_modifier(X_, self.static_context)

        # Simulation
        results = self.simulate_context(simulation_context)

        # Cost calculation
        cost = self.residual(results, **self.kwargs_r)

        # Savings
        if self.saver is not None:
            data = {'position':X, 'context':simulation_context, 'results':results, 'cost':cost}
            self.saver(data, file_name=self.file_name)
        return cost

