from abc import ABCMeta, abstractmethod

class CostFunction(NRV_class):
    """
    A class to define cost from position input vector

    Parameters
    ----------
    generate_waveform   : funct
        function creating a waveform from a particle position, parameters:
            position        : particle position in each dimensions (array)
            t_sim           : simulation time (float)
            dt              : time step of the waveform (float)
            kwargs          : keys word arguments
        returns
            waveform        : values of a waveform (array)
    simulate_waveform   : funct
        function which perform the NEURONE simulation, parameters:
            waveform        : waveform to use for the simulation (array)
            t_sim           : simulation time (float)
            dt              : time step of the waveform (float)
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
        key word arguments of generate_waveform function, by default {}
    kwargs_sw           : dict
        key word arguments of simulate_waveform function, by default {}
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
    def __init__(self, generate_waveform, simulate_waveform, residual, kwargs_gw={},
        kwargs_sw={}, kwargs_r={}, t_sim=100, dt=0.005, filter=None, saver=None, 
        file_name='cost_saver.csv'):
        self.generate_waveform = generate_waveform
        self.simulate_waveform = simulate_waveform
        self.residual = residual
        self.kwargs_gw = kwargs_gw
        self.kwargs_sw = kwargs_sw
        self.kwargs_r = kwargs_r
        self.t_sim = t_sim
        self.dt = dt
        self.filter = filter
        self.saver = saver
        self.file_name = file_name

    def __call__(self, position):
        # Filter
        if self.filter is not None:
            position = self.filter(position)

        # Interpolation
        waveform = self.generate_waveform(position, t_sim=t_sim, dt=dt, **kwargs_gw)

        # Simulation
        results = simulate_waveform(waveform, t_sim=t_sim, dt=dt, **kwargs_sw)

        # Cost calculation
        cost = residual(results, **kwargs_r)

        # Savings
        if saver is not None:
            data = {'position':position, 'waveform':waveform, 'results':results, 'cost':cost}
            saver(data, file_name=file_name)
        return cost



        