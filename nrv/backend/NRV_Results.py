"""
NRV-:class:`.NRV_results` handling.
"""
import numpy as np
import matplotlib.pyplot as plt

from .NRV_Class import NRV_class, load_any, abstractmethod, is_NRV_class
from .log_interface import rise_warning
from ..fmod.stimulus import stimulus
from .file_handler import json_load



def generate_results(obj: str, **kwargs):
    """
    generate the proper results object depending of the obj simulated

    Parameters
    ----------
    obj      : any
    """
    nrv_obj = load_any(obj)
    if "nrv_type" in nrv_obj.__dict__():
        nrv_type = nrv_obj.nrv_type
        if "myelinated" in nrv_type:
            nrv_type = ""
        return eval('sys.modules["nrv"].' + nrv_type + "_results")(context=obj)


class NRV_results(NRV_class, dict):
    """
    Results class for NRV
    """

    @abstractmethod
    def __init__(self, context=None):
        super().__init__()
        if context is None:
            context = {}
        elif is_NRV_class(context):
            context.save(save=False)

        if "nrv_type" in context:
            context["result_type"] = context.pop("nrv_type")
        self.update(context)
        self.__sync()

    def save(self, save=False, fname="nrv_save.json", blacklist=[], **kwargs):
        self.__sync()
        return super().save(save, fname, blacklist, **kwargs)

    def load(self, data, blacklist=[], **kwargs):
        if isinstance(data, str):
            key_dic = json_load(data)
        else:
            key_dic = data
        for key, item in key_dic.items():
            if key not in self.__dict__:
                self.__dict__[key] = item

        super().load(data, blacklist, **kwargs)
        self.__sync()

    def __setitem__(self, key, value):
        if not key == "nrv_type":
            self.__dict__[key] = value
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if not key == "nrv_type":
            del self.__dict__[key]
        super().__delitem__(key)

    def update(self, __m, **kwargs) -> None:
        """
        overload of dict update method to update both attibute and items
        """
        self.__dict__.update(__m, **kwargs)
        super().update(__m, **kwargs)

    def __sync(self):
        self.update(self.__dict__)
        self.pop("__NRVObject__")


class sim_results(NRV_results):
    def __init__(self, context=None):
        super().__init__(context)

    def plot_stim(self, IDs=None, t_stop=None, N_pts=1000, ax=None, **fig_kwargs):
        """
        Plot one or several stimulis of the simulation extra-cellular context
        """
        if "extra_stim" not in self:
            rise_warning("No extracellular stimulation to be plotted")
        else:
            if IDs is None:
                IDs = [i for i in range(len(self["extra_stim"]["stimuli"]))]
            elif not np.iterable(IDs):
                IDs = [int(IDs)]
            for i in IDs:
                stim = load_any(self["extra_stim"]["stimuli"][i])
                if t_stop is None:
                    t_stop = stim.t[-1]
                stim2 = stimulus()
                stim2.s = np.zeros(N_pts)
                stim2.t = np.linspace(0, t_stop, N_pts)
                stim2 += stim
                if ax is None:
                    plt.plot(stim2.t, stim2.s, **fig_kwargs)
                else:
                    ax.plot(stim2.t, stim2.s, **fig_kwargs)