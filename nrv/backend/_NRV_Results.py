"""
NRV-:class:`.NRV_results` handling.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from collections.abc import Iterable
from scipy import signal

from ._NRV_Class import NRV_class, load_any, abstractmethod, is_NRV_class
from ._log_interface import rise_warning, pass_info
from ..utils._stimulus import stimulus
from ._file_handler import json_load


def generate_results(obj: any, **kwargs):
    """
    generate the proper results object depending of the obj simulated

    Parameters
    ----------
    obj      : any
    """
    nrv_obj = load_any(obj)
    if "nrv_type" in nrv_obj.__dict__:
        nrv_type = nrv_obj.nrv_type
        return eval('sys.modules["nrv"].' + nrv_type + "_results")(context=obj)


class NRV_results(NRV_class, dict):
    """
    Results class for NRV
    """

    @abstractmethod
    def __init__(self, context=None):
        super().__init__()
        # Not ideal but require to load method
        self.np_keys = {}
        if context is None:
            context = {}
        elif is_NRV_class(context):
            context.save(save=False)

        if "nrv_type" in context:
            context["result_type"] = context.pop("nrv_type")

        # Discard saving for empty results (mostly fo Mcore)
        self.update(context)
        self.__sync()

    @property
    def to_save(self):
        return "dummy_res" not in self

    @property
    def is_dummy(self):
        return "dummy_res" in self

    def save(self, save=False, fname="nrv_save.json", blacklist=[], **kwargs):
        save = save and self.to_save
        self.__update_np_keys()
        self.__sync()
        return super().save(save, fname, blacklist, **kwargs)

    def load(self, data, blacklist=[], **kwargs):
        if isinstance(data, str):
            key_dic = json_load(data)
        else:
            key_dic = data
        for key, item in key_dic.items():
            if key in key_dic["np_keys"]:
                self.__dict__[key] = np.array(
                    [], dtype=np.dtype(key_dic["np_keys"][key])
                )
            elif key not in self.__dict__:
                self.__dict__[key] = item

        super().load(data, blacklist, **kwargs)
        self.__sync()

    def __setitem__(self, key, value):
        if not key == "nrv_type":
            self.__dict__[key] = value
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if key not in self.__dict__:
            rise_warning(key, "not found cannot be deleted from results")
        else:
            if not key == "nrv_type":
                del self.__dict__[key]
            super().__delitem__(key)

    def remove_key(
        self,
        keys_to_remove: str | set[str] = [],
        keys_to_keep: set[str] | None = None,
        verbose: bool = False,
    ):
        """
        Remove a key or a list of keys from the results

        Parameters
        ----------
        keys_to_remove : str | list[str], optional
            key or set of key that should be removed, by default []
        keys_to_keep : str | list[str], optional
            If None only keys_to_remove are removed. Otherwise, all key exept those in this list are deleted, by default None
        verbose : bool, optional
            If True print a message informing the suppression, by default False
        """
        if keys_to_keep is not None:
            keys_to_remove = set(self.keys()) - set(keys_to_keep)
            self.remove_key(keys_to_remove=keys_to_remove, verbose=verbose)
        else:
            if isinstance(keys_to_remove, str):
                del self[keys_to_remove]
                # pass_info(
                #     "removed the following key from results: ",
                #     keys_to_remove,
                #     verbose=verbose,
                # )
            else:
                for key in keys_to_remove:
                    del self[key]
                    # pass_info(
                    #     "removed the following key from results: ", key, verbose=verbose
                    # )

    def update(self, __m, **kwargs) -> None:
        """
        overload of dict update method to update both attibute and items
        """
        self.__dict__.update(__m, **kwargs)
        super().update(__m, **kwargs)

    def __update_np_keys(self):
        """ """
        self.np_keys = {}
        for key in self:
            if isinstance(self[key], np.ndarray):
                self.np_keys[key] = self[key].dtype.name

    @property
    def is_empty(self):
        return "result_type" in self and not self["result_type"] is None

    def __sync(self):
        self.update(self.__dict__)
        self.pop("__NRVObject__")

    def __contains__(self, key: object) -> bool:
        if isinstance(key, list) or isinstance(key, set):
            missing_keys = set(key) - set(self.keys())
            return len(missing_keys) == 0
        return super().__contains__(key)


class sim_results(NRV_results):
    def __init__(self, context=None):
        super().__init__(context)

    def filter_freq(self, my_key, freq, Q=10):
        """
        Basic Filtering of quantities. This function design a notch filter (scipy IIR-notch).
        Adds an item to the specified dictionary, with the key termination '_filtered' concatenated to the original key.

        Parameters
        ----------
        key     : str|list[str]
            name of the key to filter
        freq    : float or array, list, np.array
            frequecy or list of frequencies to filter in kHz, as time is defined in ms in NRV2.
            If multiple frequencies, they are filtered sequencially, with as may filters as frequencies, in the specified order
        Q       : float
            quality factor of the filter, by default set to 10
        """
        if isinstance(freq, Iterable):
            f0 = np.asarray(freq)
        else:
            f0 = freq
        if self["dt"] == 0:
            rise_warning(
                "Warning: filtering aborted, variable time step used for differential equation solving"
            )
            return False
        else:
            fs = 1 / self["dt"]
            if isinstance(f0, Iterable):
                new_sig = np.zeros(self[my_key].shape)
                for k in range(len(self[my_key])):
                    new_sig[k, :] = self[my_key][k]
                    offset = self[my_key][k][0]
                    new_sig[k, :] = new_sig[k, :] - offset
                    for f in f0:
                        b_notch, a_notch = signal.iirnotch(f, Q, fs)
                        new_sig[k, :] = signal.lfilter(
                            b_notch, a_notch, new_sig[k, :][k]
                        )
                    new_sig[k, :] = new_sig[k, :] + offset
            else:
                ##  NOTCH at the stimulation frequency
                b_notch, a_notch = signal.iirnotch(f0, Q, fs)
                new_sig = np.zeros(self[my_key].shape)
                for k in range(len(self[my_key])):
                    offset = self[my_key][k][0]
                    new_sig[k, :] = (
                        signal.lfilter(b_notch, a_notch, self[my_key][k] - offset)
                        + offset
                    )
            self[my_key + "_filtered"] = new_sig

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
