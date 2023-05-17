"""
NRV-Nerves
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import numpy as np
import matplotlib.pyplot as plt
from ..backend.log_interface import rise_error, rise_warning, pass_info

from .fascicles import *
from ..backend.NRV_Class import NRV_class

#################
## Nerve class ##
#################
class nerve(NRV_class):
    """A nerve in NRV2 is defined as:
        - a list of fascicles
        - a list of materials
        - a kind of extracellular context (analytical or FEM based)

    a nerve can be instrumented by adding couples of electrodes+stimulus
    """
    def __init__(self, Length=10000, Outer_D=5,  Nerve_D=4000, y_c=0, z_c=0,\
            dt=0.001, mesh_shape='plateau_sigmoid', alpha_max=0.3, d_lambda=0.1, T=None, ID=0, threshold=-40,\
            Adelta_limit=1,**kwargs):
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
        super().__init__()
        self.type = "nerve"
        self.L = Length
        self.y_c = y_c
        self.z_c = z_c

        self.Outer_D = (Outer_D*mm)

        self.L = L
        self.FEM = FEM
        ### empty attributes for later use
        self.N_ax = 0
        self.fascicles_IDs = []
        self.fascicles = []
        self.electrodes_IDs = []
        self.electrodes = []
        self.stimuli_IDs = []
        self.stimuli = []
        self.materials = {}
        self.extracellular_context = None

    ## save/load methods
    def save(self, fname, extracel_context=False, intracel_context=False, rec_context=False):
        """
        Save a nerve in a json file

        Parameters
        ----------
        fname : str
            name of the file to save the nerve
        extracel_context: bool
            if True, add the extracellular context to the saving
        intracel_context: bool
            if True, add the intracellular context to the saving
        """
        if MCH.do_master_only_work():
            # copy everything into a dictionnary
            nerve_config = {}
            nerve_config['ID'] = self.ID

            if intracel_context:
                nerve_config['L'] = self.L

            if extracel_context:
                nerve_config['L'] = self.L

            if rec_context:
                nerve_config['record'] = self.record

            # save the dictionnary as a json file
            json_dump(nerve_config, fname)

    def load(self, fname, extracel_context=False, intracel_context=False, rec_context=False):
        """
        Load a nerve configuration from a json file

        Parameters
        ----------
        fname           : str
            path to the json file describing a nerve
        extracel_context: bool
            if True, load the extracellular context as well
        intracel_context: bool
            if True, load the intracellular context as well
        """
        if type(fname) == str:
            results = json_load(fname)
        else: 
            results = fname
        self.ID = results['ID']

        if intracel_context:
            self.L = results['L']
        if extracel_context:
            self.L = results['L']
            
        if rec_context:
            self.record = results['record']

    def add_fascicle(self, fascicle):
        """
        Add a fascicle to the list of fascicles

        Parameters
        ----------
        fascicle : object
            fascicle to add to the nerve struture
        """
        if not is_fascicle(fascicle):
            rise_warning('Only fascile object can be added with add fascicle method: nothing added')
        else:
            if fascicle.ID in self.fascicles_IDs:
                pass_info('Fascicle ' +str(fascicle.ID)+' already in the nerve: will be replace')
                i_fasc = np.index(fascicle.ID)
                self.fascicles[i_fasc]
            else:
                self.fascicles_IDs += [fascicle.ID]
                i_fasc = len(self.fascicles_IDs) + 1
                self.fascicles += [fascicle]
            self.fascicles[i_fasc].L = self.L
            
        
    def __build_extracellular_context(self):
        """
        Private method to create the correct extracellular context
        """
        extracellular_context_list = []
        for fasc in self.fascicles:
            if fasc.extra_stim is not None:
                extracellular_context_list += fasc.extra_stim
                fasc.extra_stim = None

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
        self.__build_extracellular_context()
        # step 2: simulate all fascicles
        for fascicle in self.fascicles:
            fascicle.simulate()
