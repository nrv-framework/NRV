import numpy as np

from ...backend.NRV_Class import NRV_class, load_any
from ...backend.NRV_Simulable import NRV_simulable
from ...fmod.stimulus import stimulus

class ContextModifier(NRV_class):
    def __init__(self):
        super().__init__()

    def __call__(self, X, static_context:NRV_simulable, **kwargs) -> NRV_simulable:
        return static_context



class stimulus_CM(ContextModifier):
    def __init__(self, stim_ID=0, interpolator=None, intrep_kwargs={}, stim_gen=None, stim_gen_kwargs={}):
        """
        
        """
        super().__init__()
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
        local_sim = load_any(static_sim, extracel_context=True, intracel_context=True, rec_context=True)
        t_sim = local_sim.t_sim
        self.stim_gen_kwargs["t_sim"] = t_sim
        X_inter = self.interpolate(X)
        stim = self.stimulus_generator(X_inter)
        local_sim.extra_stim.change_stimulus_from_elecrode(self.stim_ID, stim)
        return local_sim
