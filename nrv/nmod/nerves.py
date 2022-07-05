"""
NRV-Nerves
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import numpy as np
import matplotlib.pyplot as plt
from ..backend.log_interface import rise_error, rise_warning, pass_info

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
    def __init__(self, outershape, simulation_box, materials
        dt=0.001, Nseg_per_sec=0, freq=100, freq_min=0,\
        mesh_shape='plateau_sigmoid', alpha_max=0.3, d_lambda=0.1, T=None, ID=0, threshold=-40,\
        Adelta_limit=1**kwargs):
        """
        Instanciates an empty nerve.

        Parameters
        ----------
        dt              : float
            simulation time stem for Neuron (ms), by default 1us
        Nseg_per_sec    : float
            number of segment per section in Neuron. If set to 0, the number of segment per section is calculated with the d-lambda rule
        freq            : float
            frequency of the d-lambda rule (Hz), by default 100Hz
        freq_min        : float
            minimum frequency for the d-lambda rule when meshing is irregular, 0 for regular meshing
        v_init          : float
            initial value for the membrane voltage (mV), specify None for automatic model choice of v_init
        T               : float
            temperature (C), specify None for automatic model choice of temperature
        ID              : int
            axon ID, by default set to 0
        threshold       : int
            membrane voltage threshold for spike detection (mV), by default -40mV
        Adelta_limit    : float
            limit diameter between A-delta models (thin myelinated) and myelinated models for axons
        """
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
        # step 1: create FEM geometry, mesh and compute
        
        # step 2: simulate all fascicles
        for fascicle in self.fascicles:
            fascicle.simulate()
