"""
NRV-:class:`.extracellular_context` handling.
"""

import faulthandler

import numpy as np
import matplotlib.pyplot as plt
from typing import Literal

from ...backend._file_handler import json_load
from ...backend._log_interface import rise_error, rise_warning
from ...backend._NRV_Class import NRV_class, load_any
from ...utils._misc import get_perineurial_thickness
from ...utils._stimulus import stimulus


def is_intracellular_context(obj):
    """
    Check whether an object is an intracellular-stimulation context.

    Parameters
    ----------
    obj : Any
        Object to test.

    Returns
    -------
    bool
        ``True`` when ``obj`` is an :class:`intracellular_context`.
    """
    return isinstance(obj, intracellular_context)


class intracellular_context(NRV_class):
    """
    Intracellular stimulation context container.

    This class collects and manages point (intracellular) stimuli applied to an axon.
    It stores the spatial location of each stimulus, the stimulus object itself,
    and a small tag describing whether the stimulus is delivered as a current clamp
    ("i") or a voltage clamp ("v"). The object provides sequence-like access and
    simple convenience methods for inserting and clearing stimuli.

    Attributes
    position : list[float | tuple]
        List of stimulus positions. Each entry is typically a float giving the
        absolute position along the axon, or a tuple (section, relative_pos)
        describing a location within a named section and a relative coordinate.
    stimuli : list[stimulus]
        List of stimulus objects (user-defined `stimulus` type expected by the
        simulator). The i-th element corresponds to the stimulus applied at
        position[i].
    stim_type : list[Literal["i", "v"]]
        List of lowercase single-character tags indicating the type of each
        stimulus: "i" for current clamp, "v" for voltage clamp. Case-insensitive
        values passed to insertion methods will be normalized to lowercase.
    """

    def __init__(self, data=None):
        """
        Instrantiation an intracellular_context object, empty shell to store electrodes and stimuli
        """
        super().__init__()
        self.position: list[float] = []
        self.stimuli: list[stimulus] = []
        self.stim_type: list[Literal["i", "v"]] = []

        if data is not None:
            self.append(data=data)

    def __len__(self):
        """
        Return the number of stored stimuli (length of the context).
        """
        return len(self.stimuli)

    def __iter__(self):
        """
        Iterate over stored entries, yielding tuples (position, stimulus, stim_type)
        for each stimulus.
        """
        for s in zip(self.position, self.stimuli, self.stim_type):
            yield s

    def __getitem__(self, i):
        """
        Return the i-th stored entry as (position[i], stimuli[i], stim_type[i]).
        """
        return self.position[i], self.stimuli[i], self.stim_type[i]

    ##
    def is_empty(self):
        """
        check if a stimulation object is empty (No electrodes and stimuli, no external field can be computed).
        Returns True if empty, else False.

        Returns
        -------
        bool
            True if a simulation is empty, else False
        """
        return not bool(len(self))

    def insert_intra_stim(
        self,
        position: float | str,
        stim: stimulus,
        stype: Literal["I", "i", "V", "v"] = "i",
    ):
        """
        Insert a IC clamp stimulation on a Ranvier node at its midd point position

        Parameters
        ----------
        position       : float|str
            relative x_posision along the axon or tuple containing an str of the targeted section and the relative position along this section
        t_start     : float
            starting time (ms)
        duration    : float
            duration of the pulse(ms)
        amplitude   : float
            amplitude of the pulse (nA)

        Note
        ----
        For positions specified as targeted sections, tupple must be converted to str to avoid conflict between save/load and neuron Sections. This str is evaluated during the simulation by self.__activate_intra_stim
        """
        self.stim_type.append(stype.lower())
        self.stimuli.append(stim)
        self.position.append(position)

    def append(self, data: str | dict | tuple):
        """
        Append intracellular stimulus data to this context.

        Parameters
        ----------
        data : str | dict | intracellular_context
            Input object that load_any can parse describing one or more intracellular stimuli. Accepted forms:
              - a string (a filepath),
              - a dict that load_any can parse,
              - an already-loaded intracellular_context object.
            After normalization via load_any, the method expects either:
              - an object for which is_intracellular_context(...) returns True, or
              - an iterable (for example, a tuple/list) of 3-element tuples/lists,
                where each element corresponds to the positional arguments accepted
                by self.insert_intra_stim (typically start, duration, amplitude or
                similar stimulus parameters).

        Raises
        ------
        Any exception raised by load_any or by self.insert_intra_stim will propagate.
        If individual stim items cannot be unpacked into the expected three positional
        arguments, a corresponding TypeError will be raised by the call to
        insert_intra_stim.

        Examples
        --------
        >>> # Append from an other intracellular_context:
        >>> intra_stim = intracellular_context()
        >>> intra_stim.insert_intra_stim(...)
        >>> self.append(intra_stim)
        >>> # Append from a file:
        >>> self.append("path/to/stims.json")
        >>> # Append from a dict that load_any recognizes:
        >>> self.append({"stimuli": [...]})
        >>> # Append from an iterable of (start, duration, amplitude) tuples:
        >>> self.append([(0.0, 1.0, 0.5), (2.0, 0.5, 0.2)])
        """
        intra_context = load_any(data)
        _ok_data = is_intracellular_context(intra_context) or (
            isinstance(intra_context, tuple) and len(isinstance == 3)
        )
        if _ok_data:
            for intra_stim in intra_context:
                self.insert_intra_stim(*intra_stim)

    def generate_from_deprected_fascicle(self, key_dic: dict):
        """
        Rebuild intracellular stimuli from deprecated fascicle serialization fields.

        Parameters
        ----------
        key_dic : dict
            Raw serialized fascicle dictionary.
        """
        if "intra_current_stim_positions" in key_dic:
            for i in range(len(key_dic["intra_current_stim_positions"])):
                position = key_dic["intra_current_stim_positions"][i]
                stim_start = key_dic["intra_current_stim_starts"][i]
                duration = key_dic["intra_current_stim_durations"][i]
                amplitude = key_dic["intra_current_stim_amplitudes"][i]
                s = stimulus()
                s.pulse(value=amplitude, start=stim_start, duration=duration)
                self.insert_intra_stim(position=position, stim=s, stype="i")

        if "intra_voltage_stim_stimulus" in key_dic:
            if key_dic["intra_voltage_stim_stimulus"] is not None:
                for i in range(len(key_dic["intra_voltage_stim_position"])):
                    position = key_dic["intra_voltage_stim_position"][i]
                    self.insert_intra_stim(
                        position=position,
                        stim=key_dic["intra_voltage_stim_stimulus"][i],
                        stype="v",
                    )

    def clear_i_clamp(self):
        """
        Clear any I-clamp attached to the axon
        """
        _k_i = [k for _st, k in enumerate(self.stim_type) if _st == "i"]
        self.position = [self.position[k] for k in _k_i]
        self.stimuli = [self.stimuli[k] for k in _k_i]
        self.stim_type = [self.stim_type[k] for k in _k_i]

    def clear_v_clamp(self):
        """
        Clear any V-clamp attached to the axon
        """
        _k_i = [k for _st, k in enumerate(self.stim_type) if _st == "v"]
        self.position = [self.position[k] for k in _k_i]
        self.stimuli = [self.stimuli[k] for k in _k_i]
        self.stim_type = [self.stim_type[k] for k in _k_i]
