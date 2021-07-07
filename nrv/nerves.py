"""
NRV-Nerves
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import numpy as np
import matplotlib.pyplot as plt
from .log_interface import rise_error, rise_warning, pass_info

#################
## Nerve class ##
#################
class nerve:
    """A nerve in NRV2 is defined as:
        - a list of fascicles
        - a list of materials
        - a kind of extracellular context (analytical or FEM based)

    a nerve can be instrumented by adding couples of electrodes+stimulus
    """
    def __init__(self, L, FEM=False):
        """
        Instanciates an empty nerve.

        Parameters
        ----------
        L : float
            length of the nerve
        FEM : bool
            desccription of the extracellular physics with Finite Element Method if True, with analytical method if False.
            Has consequences on electrodes type through possible instantiations of extracellular contexts, see extracellular.py for more details.

        """
        super().__init__()
        self.L = L
        self.FEM = FEM
        ### empty attributes for later use
        self.fascicles = []
        self.electrodes = []
        self.stimuli = []
        self.materials = {}
        self.extracellular_context = None

    def add_fascicle(self, fascicle):
        """
        Add a fascicle to the list of fascicles

        Parameters
        ----------
        fascicle : object
            fascicle to add to the nerve struture
        """
        raise NotImplementedError

    def add_stimulation(self, electrode, stimulus):
        """
        Add a stimulation to the current nerve

        Parameters
        ----------
        electrode   : object

        stimulus    : object
        """
        raise NotImplementedError

    def __build_extracellular_context(self):
        """
        Private method to create the correct extracellular context
        """
        raise NotImplementedError

    def simulate(self, *args):
        """
        Simulate the nerve with the proposed extracellular context. Top level method for large scale neural simulation.

        Parameters
        ----------


        Warning
        -------
        calling this method can result in long processing time, even with large computational ressources.
        Keep aware of what is really implemented, ensure configuration and simulation protocol is correctly designed.
        """
        raise NotImplementedError
