import numpy as np

from ...backend.NRV_Class import NRV_class, load_any
from ...backend.NRV_Simulable import NRV_simulable
from ...fmod.stimulus import stimulus

class ContextModifier(NRV_class):
    """
        Instanciate a context modifier: Callable object which modify a static context,
        regarding a vector of values, to generate a new local context

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
    def __init__(self, extracel_context=True, intracel_context=False, rec_context=False):
        super().__init__()
        self.extracel_context = extracel_context
        self.intracel_context = intracel_context
        self.rec_context = rec_context

    def __call__(self, X, static_context:NRV_simulable, **kwargs) -> NRV_simulable:
        self.set_parameters(**kwargs)
        return load_any(
            static_context,
            extracel_context = self.extracel_context,
            intracel_context = self.intracel_context,
            rec_context = self.rec_context,
        )



class stimulus_CM(ContextModifier):
    """
        Context modifier which:
        interpolate the input vector,
        generate a stimulus from interplotated values and
        set the stimulus to an electrode of a static context
    """
    def __init__(
            self, 
            stim_ID=0,
            interpolator=None,
            intrep_kwargs={},
            stim_gen=None,
            stim_gen_kwargs={},
            extracel_context=True,
            intracel_context=False,
            rec_context=False,
        ):
        """
            i
        """
        super().__init__(
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context
        )
        self.stim_ID = stim_ID
        self.interpolator = interpolator
        self.intrep_kwargs = intrep_kwargs
        self.stim_gen = stim_gen
        self.stim_gen_kwargs = stim_gen_kwargs

    def interpolate(self, X):
        if self.interpolator is not None:
            X_interp = self.interpolator(X, **self.intrep_kwargs)
        else:
            X_interp = X
        return X_interp

    def stimulus_generator(self, X_interp)->stimulus:
        if self.stim_gen is not None:
            stim = self.stim_gen(X_interp, **self.stim_gen_kwargs)
        else:
            t_sim = self.stim_gen_kwargs["t_sim"]
            stim = stimulus()
            N = len(X_interp)
            stim.s = X_interp
            stim.t = np.linspace(0, t_sim, N)
        return stim

    def __call__(self, X, static_sim:NRV_simulable, **kwargs) -> NRV_simulable:
        local_sim = super().__call__(X, static_sim, **kwargs)
        t_sim = local_sim.t_sim
        self.stim_gen_kwargs["t_sim"] = t_sim
        X_inter = self.interpolate(X)
        stim = self.stimulus_generator(X_inter)
        local_sim.extra_stim.change_stimulus_from_elecrode(self.stim_ID, stim)
        return local_sim


class cathodic_stimulus_CM(stimulus_CM):
    def __init__(
            self,
            stim_ID=0,
            start = 1,
            I_cathod = 100,
            T_cathod = 60e-3,
            T_inter = 40e-3,
            stim_gen=None,
            stim_gen_kwargs={},
            extracel_context=True,
            intracel_context=False,
            rec_context=False,
        ):
        """
        
        """
        super().__init__(
            stim_ID = stim_ID,
            stim_gen = stim_gen,
            stim_gen_kwargs = stim_gen_kwargs,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context
        )
        self.start = start
        self.I_cathod = I_cathod
        self.T_cathod = T_cathod
        self.T_inter = T_inter

    def __set_values(self, X):
        N_X = len(X)
        start = self.start
        I_cathod = self.I_cathod
        T_cathod = self.T_cathod
        T_inter = self.T_inter
        if isinstance(self.start, str):
            for i in range(N_X):
                if str(i) in self.start:
                    start = X[i]
        if isinstance(self.I_cathod, str):
            for i in range(N_X):
                if str(i) in self.I_cathod:
                    I_cathod = X[i]
        if isinstance(self.T_cathod, str):
            for i in range(N_X):
                if str(i) in self.T_cathod:
                    T_cathod = X[i]
        if isinstance(self.T_inter, str):
            for i in range(N_X):
                if str(i) in self.T_inter:
                    T_inter = X[i]
        return start, I_cathod, T_cathod, T_inter


    def stimulus_generator(self, X_interp)->stimulus:
        if self.stim_gen is not None:
            stim = self.stim_gen(X_interp, **self.stim_gen_kwargs)
        else:
            stim = stimulus()
            start, I_cathod, T_cathod, T_inter = self.__set_values(X_interp)
            I_anod = I_cathod/5
            stim.biphasic_pulse(start,  I_cathod, T_cathod, I_anod, T_inter)
            return stim
