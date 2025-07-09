import numpy as np
from ...backend._NRV_Class import NRV_class, load_any
from ...backend._NRV_Simulable import NRV_simulable
from ...utils._stimulus import stimulus


class context_modifier(NRV_class):
    """
    Instantiate a context modifier: Callable object which modify a static context, regarding a vector of tunning parameters, to generate a new local context

    Notes
    -----
    `context_modifier` is an abstract class used to inherit new context modifier.

    Parameters
    ----------
    extracel_context        : bool
        specifies whether to load extracel_context with the static context
    intracel_context        : bool
        specifies whether to load intracel_context with the static context
    rec_context     : bool
        specifies whether to load rec_context with the static context
    """

    def __init__(
        self, extracel_context=True, intracel_context=False, rec_context=False
    ):
        super().__init__()
        self.extracel_context = extracel_context
        self.intracel_context = intracel_context
        self.rec_context = rec_context

    def __call__(
        self, X: np.ndarray, static_context: NRV_simulable, **kwargs
    ) -> NRV_simulable:
        """
        Modify ``static_context`` tunning paramters vector ``X``.

        Parameters
        ----------
        X               : np.array (X,)
            Vector of that will lead to the modification of the static context
        static_context  : NRV_simulable
            Static context which should be modify to optain th local context

        Returns
        -------
        local_context  : NRV_simulable
            simulable object generated from the vector X and the static_context

        """
        self.set_parameters(**kwargs)
        return load_any(
            static_context,
            extracel_context=self.extracel_context,
            intracel_context=self.intracel_context,
            rec_context=self.rec_context,
        )


class stimulus_CM(context_modifier):
    """
    Generic context modifier which generate a stimulus from the input tuning parameters.

    Note
    ----
    When an instance of this class is called the three following steps are done:
        1. The input vector is interpolated with the `interpolator`. If not set, the interpolated vector will be the equal to the input vector.
        2. The stimulus is generated from interpolated values with  `stim_gen` function. If not set, interpolated values are set for the stimulus amplitude at constant sample rate (from zero to an argument ``t_sim``)
        3. The generated stimulus is added to an electrode of a static context.

    Parameters
    ----------
    stim_ID                 : int, optional
        ID of the electrode which should be adapted, by default 0
    interpolator            : callable, optional
        if not None function use to interpolate the input vector, by default None
    intrep_kwargs           : dict, optional
        key arguments to use with the `interpolator`, by default {}
    stim_gen                : callable, optional
        function use to generate the stimulus from the interpolated values, by default None
    stim_gen_kwargs         : dict, optional
        key arguments used for the , by default {}
    extracel_context        : bool
        specifies whether to load extracel_context with the static context
    intracel_context        : bool
        specifies whether to load intracel_context with the static context
    rec_context             : bool
        specifies whether to load rec_context with the static context
    """

    def __init__(
        self,
        stim_ID: int = 0,
        interpolator: callable = None,
        intrep_kwargs: dict = {},
        stim_gen: callable = None,
        stim_gen_kwargs: dict = {},
        extracel_context: bool = True,
        intracel_context: bool = False,
        rec_context: bool = False,
        **kwargs,
    ):
        super().__init__(
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )
        self.stim_ID = stim_ID
        self.interpolator = interpolator
        self.intrep_kwargs = intrep_kwargs
        self.stim_gen = stim_gen
        self.stim_gen_kwargs = stim_gen_kwargs
        for key in kwargs:
            self.intrep_kwargs[key] = kwargs[key]
            self.stim_gen_kwargs[key] = kwargs[key]

    def interpolate(self, X: np.ndarray) -> np.ndarray:
        """
        interpolate the input vector with the `interpolator`. If not set, the interpolated vector will be the equal to the input vector.
        Parameters
        ----------
        X : np.ndarray
            Input vector to interpolate.

        Returns
        -------
        np.ndarray
            Interpolated vector.
        """
        if self.interpolator is not None:
            X_interp = self.interpolator(X, **self.intrep_kwargs)
        else:
            X_interp = X
        return X_interp

    def stimulus_generator(self, X_interp: np.ndarray) -> stimulus:
        """
        generated from interpolated values with  `stim_gen` function. If not set, interpolated values are set for the stimulus amplitude at constant sample rate (from zero to an argument ``t_sim``)

        Parameters
        ----------
        X_interp : np.ndarray
            Interpolated values.

        Returns
        -------
        stimulus
            stimulus generated from the values
        """
        if self.stim_gen is not None:
            stim = self.stim_gen(X_interp, **self.stim_gen_kwargs)
        else:
            t_sim = self.stim_gen_kwargs["t_sim"]
            stim = stimulus()
            N = len(X_interp)
            stim.s = X_interp
            stim.t = np.linspace(0, t_sim, N)
        return stim

    def __update_t_sim(self, local_sim):
        if "t_sim" not in self.stim_gen_kwargs:
            if "t_sim" in self.intrep_kwargs:
                self.stim_gen_kwargs["t_sim"] = self.intrep_kwargs["t_sim"]
            else:
                self.stim_gen_kwargs["t_sim"] = local_sim.t_sim

    def __call__(
        self, X: np.ndarray, static_sim: NRV_simulable, **kwargs
    ) -> NRV_simulable:
        """
        Modify ``static_context`` tunning paramters vector ``X``.

        Note
        ----
        The ``t_sim`` argument need can be added for `stimulus_generator`. If the instance is called from :class:`~nrv.optim.CostFunctions.cost_function` it will be automatically added from the simulation parameter.

        Parameters
        ----------
        X               : np.array (X,)
            Vector of that will lead to the modification of the static context
        static_context  : NRV_simulable
            Static context which should be modify to optain th local context

        Returns
        -------
        local_context  : NRV_simulable
            simulable object generated from the vector X and the static_context
        """
        local_sim = super().__call__(X, static_sim, **kwargs)
        self.__update_t_sim(local_sim)
        X_inter = self.interpolate(X)
        stim = self.stimulus_generator(X_inter)
        local_sim.extra_stim.change_stimulus_from_electrode(self.stim_ID, stim)
        return local_sim


class biphasic_stimulus_CM(stimulus_CM):
    r"""
    Context modifier which generate a stimulus biphasic stimulus from the input tuning parameters.

    Parameters
    ----------
    stim_ID                 : int, optional
        ID of the electrode which should be adapted, by default 0
    start       : float or str
        starting time of the waveform, in ms
    s_cathod    : float or str
        cathodic (negative stimulation value) current, in uA
    s_anod      : float or str
        anodic (positive stimulation value) current and, in uA
    t_inter     : float or str
        inter pulse timing, in ms
    s_ratio     : float or str
        if s_cathod set to None, s_cathod is set as: :math:`s_{anod}*s_{ratio}`. by default 0.2
    stim_gen                : callable, optional
        function use to generate the stimulus from the interpolated values, by default None
    stim_gen_kwargs         : dict, optional
        key arguments used for the , by default {}
    extracel_context        : bool
        specifies whether to load extracel_context with the static context
    intracel_context        : bool
        specifies whether to load intracel_context with the static context
    rec_context             : bool
        specifies whether to load rec_context with the static context

    Warning
    -------
    ``s_cathod`` must always positive, the user give here the absolute value

    Note
    ----
    Note that `start`, `s_cathod`, `s_anod` and `t_inter` are the paramters used to generate a :meth:`~nrv.fmod.stimulus.stimulus.harmonic_pulse` stimulus. They can either be:
         - set as ``float``, to a constant value (wich will not be changed by the )
         - set as ``str`` ("1", "2", ..) of the index of the value in the input vector.

    See Also
    --------
    :doc:`tutorials 5</tutorials/5_first_optimization>`: First optimization problem using NRV

    """

    def __init__(
        self,
        stim_ID: int = 0,
        start: float = 1,
        s_cathod: float | str = 100,
        t_cathod: float | str = 60e-3,
        t_inter: float | str = 40e-3,
        s_anod: float | str = None,
        s_ratio: float | str = 0.2,
        stim_gen: callable = None,
        stim_gen_kwargs: dict = {},
        extracel_context: bool = True,
        intracel_context: bool = False,
        rec_context: bool = False,
    ):
        super().__init__(
            stim_ID=stim_ID,
            stim_gen=stim_gen,
            stim_gen_kwargs=stim_gen_kwargs,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )
        self.start = start
        self.s_cathod = s_cathod
        self.t_cathod = t_cathod
        self.t_inter = t_inter
        self.s_anod = s_anod
        self.s_ratio = s_ratio

    def __set_values(self, X: np.ndarray):
        start = self.start
        s_cathod = self.s_cathod
        t_cathod = self.t_cathod
        t_inter = self.t_inter
        if isinstance(self.start, str):
            start = X[int(self.start)]
        if isinstance(self.s_cathod, str):
            s_cathod = X[int(self.s_cathod)]
        if isinstance(self.t_cathod, str):
            t_cathod = X[int(self.t_cathod)]
        if isinstance(self.t_inter, str):
            t_inter = X[int(self.t_inter)]
        s_anod = self.s_anod
        if s_anod is not None:
            if isinstance(self.s_anod, str):
                s_anod = X[int(self.s_anod)]
        else:
            s_ratio = self.s_ratio
            if isinstance(self.s_ratio, str):
                s_ratio = X[int(self.s_ratio)]
            s_anod = s_cathod * s_ratio
        return start, s_cathod, t_cathod, t_inter, s_anod

    def stimulus_generator(self, X_interp) -> stimulus:
        if self.stim_gen is not None:
            stim = self.stim_gen(X_interp, **self.stim_gen_kwargs)
        else:
            stim = stimulus()
            start, s_cathod, t_cathod, t_inter, s_anod = self.__set_values(X_interp)
            stim.biphasic_pulse(start, s_cathod, t_cathod, s_anod, t_inter)
            return stim


class harmonic_stimulus_CM(stimulus_CM):
    """
    Context modifier which generate a stimulus harmonic stimulus from the input tuning parameters.

    Parameters
    ----------
    stim_ID : int, optional
        ID of the electrode which should be adapted, by default 0
    start : float or str
        starting time of the waveform, in ms
    amplitude : float, optional
        _description_, by default 100
    t_pulse : float, optional
        _description_, by default 60e-3
    dt : float, optional
        _description_, by default 0
    stim_gen : callable, optional
        _description_, by default None
    stim_gen_kwargs : dict, optional
        _description_, by default {}
    extracel_context        : bool
        specifies whether to load extracel_context with the static context
    intracel_context        : bool
        specifies whether to load intracel_context with the static context
    rec_context             : bool
        specifies whether to load rec_context with the static context
    """

    def __init__(
        self,
        stim_ID: int = 0,
        start: float = 1,
        amplitude: float = 100,
        t_pulse: float = 60e-3,
        dt: float = 0,
        stim_gen: callable = None,
        stim_gen_kwargs: dict = {},
        extracel_context: bool = True,
        intracel_context: bool = False,
        rec_context: bool = False,
    ):
        super().__init__(
            stim_ID=stim_ID,
            stim_gen=stim_gen,
            stim_gen_kwargs=stim_gen_kwargs,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )
        self.start = start
        self.amplitude = amplitude
        self.t_pulse = t_pulse
        self.dt = dt

    def stimulus_generator(self, X_interp) -> stimulus:
        self.amplitude = X_interp[0]
        N = (len(X_interp) - 1) // 2
        self.amp_list = []
        self.phase_list = []

        for k in range(N):
            self.amp_list.append(X_interp[2 * k + 1])
            self.phase_list.append(X_interp[2 * k + 2])
        stim = stimulus()
        stim.harmonic_pulse(
            start=self.start,
            t_pulse=self.t_pulse,
            amplitude=self.amplitude,
            amp_list=self.amp_list,
            phase_list=self.phase_list,
            dt=self.dt,
        )
        return stim


class harmonic_stimulus_with_pw_CM(stimulus_CM):
    def __init__(
        self,
        stim_ID: int = 0,
        start: float = 1,
        amplitude: float = 100,
        t_pulse: float = 60e-3,
        dt: float = 0,
        stim_gen: callable = None,
        stim_gen_kwargs: dict = {},
        extracel_context: bool = True,
        intracel_context: bool = False,
        rec_context: bool = False,
    ):
        super().__init__(
            stim_ID=stim_ID,
            stim_gen=stim_gen,
            stim_gen_kwargs=stim_gen_kwargs,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
        )
        self.start = start
        self.amplitude = amplitude
        self.t_pulse = t_pulse
        self.dt = dt

    def stimulus_generator(self, X_interp) -> stimulus:
        self.amplitude = X_interp[0]
        self.t_pulse = X_interp[1]
        N = (len(X_interp) - 2) // 2
        self.amp_list = []
        self.phase_list = []

        for k in range(N):
            self.amp_list.append(X_interp[2 * k + 2])
            self.phase_list.append(X_interp[2 * k + 3])
        stim = stimulus()
        stim.harmonic_pulse(
            start=self.start,
            t_pulse=self.t_pulse,
            amplitude=self.amplitude,
            amp_list=self.amp_list,
            phase_list=self.phase_list,
            dt=self.dt,
        )
        return stim
