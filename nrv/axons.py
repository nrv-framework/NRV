"""
NRV-axons
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import math
import os
import sys
import time
import traceback
from scipy import optimize
import numpy as np
from .extracellular import *
from .electrodes import *
from .log_interface import rise_error, rise_warning, pass_info
import neuron

# Handling verbosity
Verbose = True

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

# instructions for Neuron, find mod files and hide GUI
dir_path = os.path.dirname(os.path.realpath(__file__))
neuron.load_mechanisms(dir_path+'/mods')
neuron.h.load_file('stdrun.hoc')

# list of supported models
unmyelinated_models = ['HH', 'Rattay_Aberham', 'Sundt', 'Tigerholm', 'Schild_94', 'Schild_97']
myelinated_models = ['MRG', 'Gaines_motor', 'Gaines_sensory']
thin_myelinated_models = ['Extended_Gaines', 'RGK']

##############################
## Usefull Neuron functions ##
##############################
def purge_neuron():
    """
    This function clears all the sections declared in neuron.h
    """
    for section in neuron.h.allsec():
        section = None

def d_lambda_rule(L, d_lambda, f, sec):
    """
    computes the d_lambda rule for a sections and returns the number of segments.

    Attributes
    ----------
    L           : int
        length of the section (um)
    d_lambda    : float
        d_lambda value, usually between 0.1 and 0.3
    f           : float
        maximal ionic current frequency (Hz)
    sec         : neuron section
        current neuron section on which to compute dlambda rule

    Returns
    -------
    Nseg        : int
        number of segment recommended to the section
    """
    return int((L / (d_lambda*neuron.h.lambda_f(f, sec=sec)) + .999) / 2) * 2 + 1

def create_Nseg_freq_shape(N_sec, shape, freq, freq_min, alpha_max):
    """
    creates a vector with the size of N_sec, a number of section to create an axon,
    and creates a shape of frequency to use with the d-lambda rule along the axon.

    Attributes
    ----------
    Nsec        : int
        the number of sections that will be used to implement the axon
    shape       : str
        shape of the output vector, pick between:
            'pyramidal'         -> min frequencies on both sides and linear increase up to the middle at the maximum frequency
            'sigmoid'           -> same a befor with sigmoid increase instead of linear
            'plateau'           -> sale as pyramidal except the max frequency is holded on a central plateau
            'plateau_sigmoid'   -> same as previous with sigmoid increase
    freq        : float
        maximum value of the frequency for the d-lambda rule
    freq_min    : float
        minimum value of the frequency for the d-lambda rule
    alpha_max   : float
        proportion of the axon at the maximum frequency for plateau shapes

    Returns
    -------
    freqs   : np.array
        vector of frequency to apply to a multi-sections axon
    """
    if shape == 'pyramidal':
        if (N_sec%2) == 0:
            X = np.concatenate([np.linspace(0, 1, num=int(N_sec/2)), np.linspace(1, 0,\
                num=int(N_sec/2))])
        else:
            X = np.concatenate([np.linspace(0, 1, num=int(N_sec/2)), np.asarray([1]), \
                np.linspace(1, 0, num=int(N_sec/2))])
    elif shape == 'sigmoid':
        if (N_sec%2) == 0:
            x_1 = np.linspace(-6, 6, num=int(N_sec/2))
            x_2 = np.linspace(6, -6, num=int(N_sec/2))
            X = np.concatenate([(1/(1+np.exp(-x_1))), (1/(1+np.exp(-x_2)))])
        else:
            x_1 = np.linspace(-6, 6, num=int(N_sec/2))
            x_2 = np.linspace(6, -6, num=int(N_sec/2))
            X = np.concatenate([(1/(1+np.exp(-x_1))), np.asarray([1]), (1/(1+np.exp(-x_2)))])
    elif shape == 'plateau_sigmoid':
        length = int(N_sec*(1.0-alpha_max)/2)
        x_1 = np.linspace(-6, 6, num=length)
        x_2 = np.linspace(6, -6, num=length)
        X = np.concatenate([(1/(1+np.exp(-x_1))), np.ones(int(N_sec) - 2*length), \
            (1/(1+np.exp(-x_2)))])
    else:
        # pyramid with plateau shape
        length = int(N_sec*(1.0-alpha_max)/2)
        X = np.concatenate([np.linspace(0, 1, num=length), np.ones(N_sec - 2*length), \
            np.linspace(1, 0, num=length)])
    # applying the shape to the number of sections between the two specified frequencies
    freqs = X*(freq-freq_min) + freq_min
    return freqs

def rotate_list(l, n):
    """
    rotate a list with a defined number of indexes to shift

    Attributes
    ----------
    l   : list
        list to rotate
    n   : int
        number of indexes to r

    Returns
    -------
    l   : list
    """
    return l[-n:] + l[:-n]

#############################
## Generic class for axons ##
#############################
class axon():
    """Axon is a generic object to describe an axonal fiber,
    (soma and interconnection are not taken into account, all axons are independant from others)
    From user perspective, call myelinated, unmylinated or thin_myelinated classes for robust code. All axons
    are supposed to be along the x-axis, as Neuron would do when creatnig a basic longitudinal geometry.

    WARNING: do not create more than one axon at a time for one process, to prevent from parameters overlaps in Neuron
    """
    def __init__(self, y, z, d, L, dt=0.001, Nseg_per_sec=0, freq=100, freq_min=0, \
        mesh_shape='plateau_sigmoid', alpha_max=0.3, d_lambda=0.1, v_init=None, T=None, ID=0,\
        threshold=-40):
        """
        initialisation of the axon,

        Parameters
        ----------
        y               : float
            y-axis coordinate of the axon (um)
        z               : float
            z-axis coordinate of the axon (um)
        d               : float
            axon diameter (um)
        L               : float
            axon length (um)
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
        """
        ## Given by user
        self.x = []
        self.y = y
        self.z = z
        self.d = d
        self.L = L
        self.dt = dt
        self.Nseg_per_sec = Nseg_per_sec
        self.freq = freq
        self.freq_min = freq_min
        self.mesh_shape = mesh_shape
        self.alpha_max = alpha_max
        self.d_lambda = d_lambda
        self.v_init = v_init
        self.T = T
        self.ID = ID
        self.threshold = threshold
        self.model = None
        self.t_sim = 0
        self.sim_time = 0
        self.timeVector = None
        self.t_len = 0
        ## internal use
        self.created = False
        self.Nsec = 0
        self.Nseg = 0
        self.myelinated = ''
        ## stims
        self.intra_current_stim = []
        self.intra_current_stim_positions = []
        self.intra_current_stim_starts = []
        self.intra_current_stim_durations = []
        self.intra_current_stim_amplitudes = []
        self.intra_voltage_stim = None
        self.intra_voltage_stim_position = None
        self.intra_voltage_stim_stimulus = None
        self.extra_stim = None

    def __del__(self):
        for section in neuron.h.allsec():
            section = None

    def __define_shape(self):
        """
        Define the shape of the axon after all sections creation
        """
        neuron.h.define_shape()

    def topology(self):
        """
        call the neuron topology function to plot the current topology on prompt
        """
        neuron.h.topology()

    def __get_allseg_positions(self):
        """
        get the positions of all segments define by neuron using allsec()
        WARNING: for internal use only, this is used to get all  position for external field computation
        in extracellular stimulation methods. This methods ensures to take into accounts all segments in the
        simulation

        Returns
        -------
        x   : np.array
            array of x coordinates of the computation points, in um
        y   : float
            y coordinate of the axon, in um
        z   : float
            z coordinate of the axon, in um
        """
        y = self.y
        z = self.z
        x = []
        for sec in neuron.h.allsec():
            offset = sec.x3d(0)
            for seg in sec:
                x.append(offset + seg.x*sec.L)
        return np.asarray(x), y, z

    def __set_allseg_vext(self, vext):
        """
        set the external potential of all segments accordingly to a vector

        Parameters
        ----------
        vext    : list or array of values to give to all segments e_extracellular in all segment of all sections in the simulation, in mV
        """
        k = 0
        for sec in neuron.h.allsec():
            for seg in sec:
                seg.e_extracellular = vext[k]
                k += 1

    def attach_extracellular_stimulation(self, stim):
        """
        attach a extracellular context of simulation for an axon

        Parameters
        ----------
        stim     : stimulation object
            see Extracellular.stimulation help for more details
        """
        if is_extra_stim(stim):
            self.extra_stim = stim

    def simulate(self, t_sim=2e1, record_V_mem=True, record_I_mem=False, record_I_ions=False, \
        record_particles=False):
        """
        Simulates the axon using neuron framework

        Parameters
        ----------
        t_sim               : float
            total simulation time (ms), by default 20 ms
        record_V_mem        : bool
            if true, the membrane voltage is recorded, set to True by default
                see unmyelinated/myelinated to see where recording occur
                results stored with the key 'V_mem'
        record_I_mem        : bool
            if true, the membrane current is recorded, set to False by default
        record_I_ions       : bool
            if true, the ionic currents are recorded, set to False by default
        record_particules   : bool
            if true, the marticule states are recorded, set to False by default

        Returns
        -------
        axon_sim    : dictionnary
            all informations on neuron, segment position and all simulation results
        """
        self.t_sim = t_sim

        # dictionnary for results
        # general parameters
        axon_sim = {}
        axon_sim['x'] = self.x
        axon_sim['y'] = self.y
        axon_sim['z'] = self.z
        axon_sim['diameter'] = self.d
        axon_sim['L'] = self.L
        axon_sim['myelinated'] = self.myelinated
        axon_sim['model'] = self.model
        axon_sim['T'] = self.T
        axon_sim['ID'] = self.ID
        axon_sim['freq'] = self.freq
        axon_sim['freq_min'] = self.freq_min
        axon_sim['mesh_shape'] = self.mesh_shape
        axon_sim['alpha_max'] = self.alpha_max
        axon_sim['d_lambda'] = self.d_lambda
        axon_sim['v_init'] = self.v_init
        axon_sim['threshold'] = self.threshold
        axon_sim['Nsec'] = self.Nsec
        axon_sim['Nseg_per_sec'] = self.Nseg_per_sec
        axon_sim['dt'] = self.dt
        axon_sim['tstop'] = self.t_sim
        # myelinated specific parameters
        if self.myelinated == True:
            axon_sim['rec'] = self.rec
            axon_sim['x_nodes'] = self.x_nodes
            axon_sim['sequence'] = self.axon_path_type
        # saving intra-cellular stimulation parameters
        axon_sim['intra_stim_positions'] = self.intra_current_stim_positions
        axon_sim['intra_stim_starts'] = self.intra_current_stim_starts
        axon_sim['intra_stim_durations'] = self.intra_current_stim_durations
        axon_sim['intra_stim_amplitudes'] = self.intra_current_stim_amplitudes
        # saving extra-cellular stimulation
        if self.extra_stim != None:
            if is_analytical_extra_stim(self.extra_stim):
                # save material
                axon_sim['extracellular_context'] = 'analytical'
                axon_sim['extracellular_material'] = self.extra_stim.material.name
                # save electrode positions
                electrodes_x = []
                electrodes_y = []
                electrodes_z = []
                for elec in self.extra_stim.electrodes:
                    electrodes_x.append(elec.x)
                    electrodes_y.append(elec.y)
                    electrodes_z.append(elec.z)
                axon_sim['extracellular_electrode_x'] = electrodes_x
                axon_sim['extracellular_electrode_y'] = electrodes_y
                axon_sim['extracellular_electrode_z'] = electrodes_z
                # save stimuli
                stimuli_list = []
                stimuli_time_list = []
                for stim in self.extra_stim.stimuli:
                    stimuli_list.append(stim.s)
                    stimuli_time_list.append(stim.t)
                axon_sim['extracellular_stimuli'] = stimuli_list
                axon_sim['extracellular_stimuli_t'] = stimuli_time_list
            else:
                axon_sim['extracellular_context'] = 'FEM_COMSOL'
                axon_sim['model_name'] = self.extra_stim.model_fname
                axon_sim['endoneurium_material'] = self.extra_stim.endoneurium.name
                axon_sim['perineurium_material'] = self.extra_stim.perineurium.name
                axon_sim['epineurium_material'] = self.extra_stim.epineurium.name
                axon_sim['external_material'] = self.extra_stim.external_material.name
                # save electrode positions
                electrodes_x = []
                electrodes_type = []
                electrodes_y = []
                electrodes_z = []
                for electrode in self.extra_stim.electrodes:
                    if is_LIFE_electrode(electrode):
                        electrodes_x.append(electrode.x_shift+electrode.length/2)
                        electrodes_type.append('LIFE')
                    electrodes_y.append(electrode.y_c)
                    electrodes_z.append(electrode.z_c)
                axon_sim['extracellular_electrode_type'] = electrodes_type
                axon_sim['extracellular_electrode_x'] = electrodes_x
                axon_sim['extracellular_electrode_y'] = electrodes_y
                axon_sim['extracellular_electrode_z'] = electrodes_z
                # save stimuli
                stimuli_list = []
                stimuli_time_list = []
                for stimulus in self.extra_stim.stimuli:
                    stimuli_list.append(stimulus.s)
                    stimuli_time_list.append(stimulus.t)
                axon_sim['extracellular_stimuli'] = stimuli_list
                axon_sim['extracellular_stimuli_t'] = stimuli_time_list

        # set recorders arrays - KEEP THIS CODE BEFORE INITIALISATION
        self.__set_time_recorder()
        if record_V_mem:
            self.set_membrane_voltage_recorders()
        if record_I_mem:
            self.set_membrane_current_recorders()
        if record_I_ions:
            self.set_ionic_current_recorders()
        if record_particles:
            self.set_particules_values_recorders()
            if hasattr(self, 'Markov_Nav_modeled_NoR'):
                self.set_Nav_recorders()

        ## initialisation and parameters for neuron - KEEP THIS CODE JUST BEFORE SIMULATION
        neuron.h.tstop = t_sim
        neuron.h.celsius = self.T           # set temperature in celsius
        neuron.h.finitialize(self.v_init)   # initialize voltage state
        neuron.h.v_init = self.v_init
        if self.dt == 0:
            rise_warning('Warning: for Axon '+str(self.ID)+', the ODE resolution is with adaptive step, \
                atol set to 0.001 in Neuron')
            neuron.h('cvode_active(1)')
            neuron.h('cvode.atol(0.001)')
        else:
            neuron.h.dt = self.dt           # set time step (ms)

        try:
            start_time = time.time()
            neuron.h.frecord_init()
            ###########################################
            #### THIS IS WHERE SIMULATION IS HANDLED ##
            ###########################################
            if self.extra_stim is not None:
                # prepare extracellular stimulation
                x, y, z = self.__get_allseg_positions()
                self.extra_stim.synchronise_stimuli()
                self.extra_stim.compute_electrodes_footprints(x, y, z, self.ID)
                # compute the minimum time between stimuli changes, checks it's not smaller than the computation dt, if so, there should be a warning to the user
                Delta_T_min = np.amin(np.diff(self.extra_stim.global_time_serie))
                if Delta_T_min < self.dt:
                    ## WARNING: the stimulus is over sampled compared to the neuron dt:
                    if self.dt/Delta_T_min < 1:             #HERE!! FOr dt test only
                        # if the stimulus minimal change time is more than 10% of user specified dt, change it to avoid problem
                        # NOTE: print a warning as well as computation time will increase !
                        new_dt = self.dt/np.ceil(self.dt/Delta_T_min)
                        axon_sim['dt'] = new_dt
                        #logging.warning('Specified dt is too low')
                        rise_warning('Specified dt is too low')
                        #logging.warning('... automatically changing the user specified dt from '+\
                        #    str(self.dt)+' to '+str(new_dt)+' ms')
                        rise_warning('... automatically changing the user specified dt from '+\
                            str(self.dt)+' to '+str(new_dt)+' ms')
                        self.dt = new_dt
                        neuron.h.dt = self.dt
                    else:
                        #logging.warning('Neuron will undersample the stimulus... \
                        rise_warning('Neuron will undersample the stimulus... \
                            this may be unfortunate, consider to undersample your stimuli yourself,\
                            or chose a smaller dt')
                        #logging.warning('... dt is '+str(self.dt/Delta_T_min)+' times bigger \
                        rise_warning('... dt is '+str(self.dt/Delta_T_min)+' times bigger \
                            than the stimulus minimum time step difference')
                # loop on stimuli time serie
                for i in range(1, len(self.extra_stim.global_time_serie)):
                    t_step = min(self.extra_stim.global_time_serie[i], t_sim)
                    vext = self.extra_stim.compute_vext(i-1)
                    self.__set_allseg_vext(vext)
                    neuron.h.continuerun(t_step)
                # finish simulation if needed
                if neuron.h.t < t_sim:
                    vext = self.extra_stim.compute_vext(len(self.extra_stim.global_time_serie)-1)
                    self.__set_allseg_vext(vext)
                    neuron.h.continuerun(neuron.h.tstop)
            elif self.intra_voltage_stim is not None:
                # init if first point is at 0
                if self.intra_voltage_stim_stimulus.t[0] == 0:
                    self.intra_voltage_stim.amp[0] = self.intra_voltage_stim_stimulus.s[0]
                # run simulation with a loop on the voltage clamp times
                for i in range(1, len(self.intra_voltage_stim_stimulus.t)):
                    t_step = min(self.intra_voltage_stim_stimulus.t[i], t_sim)
                    # run simulation
                    neuron.h.continuerun(t_step)
                    # apply new voltage clamp value
                    self.intra_voltage_stim.amp[0] = self.intra_voltage_stim_stimulus.s[i]
                # finish simulation if needed
                if neuron.h.t < t_sim:
                    neuron.h.continuerun(neuron.h.tstop)
            else:
                neuron.h.continuerun(neuron.h.tstop)
            ###########################################
            ###########################################
            ###########################################
            self.sim_time = time.time() - start_time
            # simulation done, store results
            axon_sim['Simulation_state'] = 'Successful'
            axon_sim['sim_time'] = self.sim_time
            axon_sim['t'] = self.__get_time_vector()
            axon_sim['x_rec'] = self.x_rec
            if self.myelinated and self.rec != 'nodes':
                axon_sim['node_index'] = self.node_index
            if record_V_mem:
                axon_sim['V_mem'] = self.get_membrane_voltage()
            if record_I_mem:
                axon_sim['I_mem'] = self.get_membrane_current()
            if record_I_ions:
                if not self.myelinated:
                    if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
                        I_na_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim['I_na'] = I_na_ax
                        axon_sim['I_k'] = I_k_ax
                        axon_sim['I_l'] = I_l_ax
                    else:
                        I_na_ax, I_k_ax, I_ca_ax = self.get_ionic_current()
                        axon_sim['I_na'] = I_na_ax
                        axon_sim['I_k'] = I_k_ax
                        axon_sim['I_ca'] = I_ca_ax
                else:
                    if self.model == 'MRG':
                        I_na_ax, I_nap_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim['I_na'] = I_na_ax
                        axon_sim['I_nap'] = I_nap_ax
                        axon_sim['I_k'] = I_k_ax
                        axon_sim['I_l'] = I_l_ax
                    elif self.model in ['Gaines_motor', 'Gaines_sensory', 'Extended_Gaines']:
                        I_na_ax, I_nap_ax, I_k_ax, I_kf_ax, I_l_ax = self.get_ionic_current()
                        axon_sim['I_na'] = I_na_ax
                        axon_sim['I_nap'] = I_nap_ax
                        axon_sim['I_k'] = I_k_ax
                        axon_sim['I_kf'] = I_kf_ax
                        axon_sim['I_l'] = I_l_ax
                    else: # should be RGK
                        I_na_ax, I_k_ax, I_l_ax = self.get_ionic_current()
                        axon_sim['I_na'] = I_na_ax
                        axon_sim['I_k'] = I_k_ax
                        axon_sim['I_l'] = I_l_ax
            if record_particles:
                if not self.myelinated:
                    if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
                        m_ax, n_ax, h_ax = self.get_particles_values()
                        axon_sim['m'] = m_ax
                        axon_sim['n'] = n_ax
                        axon_sim['h'] = h_ax
                    elif self.model in ['Tigerholm']:
                        m_nav18_ax, h_nav18_ax, s_nav18_ax, u_nav18_ax, m_nav19_ax, h_nav19_ax, \
                            s_nav19_ax, m_nattxs_ax, h_nattxs_ax, s_nattxs_ax, n_kdr_ax, m_kf_ax, h_kf_ax, ns_ks_ax, nf_ks_ax, w_kna_ax, ns_h_ax, nf_h_ax = self.get_particles_values()
                        axon_sim['m_nav18'] = m_nav18_ax
                        axon_sim['h_nav18'] = h_nav18_ax
                        axon_sim['s_nav18'] = s_nav18_ax
                        axon_sim['u_nav18'] = u_nav18_ax
                        axon_sim['m_nav19'] = m_nav19_ax
                        axon_sim['h_nav19'] = h_nav19_ax
                        axon_sim['s_nav19'] = s_nav19_ax
                        axon_sim['m_nattxs'] = m_nattxs_ax
                        axon_sim['h_nattxs'] = h_nattxs_ax
                        axon_sim['s_nattxs'] = s_nattxs_ax
                        axon_sim['n_kdr'] = n_kdr_ax
                        axon_sim['m_kf'] = m_kf_ax
                        axon_sim['h_kf'] = h_kf_ax
                        axon_sim['ns_ks'] = ns_ks_ax
                        axon_sim['nf_ks'] = nf_ks_ax
                        axon_sim['w_kna'] = w_kna_ax
                        axon_sim['ns_h'] = ns_h_ax
                        axon_sim['nf_h'] = nf_h_ax
                    elif self.model in ['Schild_94']:
                        d_can_ax, f1_can_ax, f2_can_ax, d_cat_ax, f_cat_ax, p_ka_ax, q_ka_ax,\
                            c_kca_ax, n_kd_ax, x_kds_ax, y1_kds_ax, m_naf_ax, h_naf_ax, l_naf_ax,\
                            m_nas_ax, h_nas_ax = self.get_particles_values()
                        axon_sim['d_can'] = d_can_ax
                        axon_sim['f1_can'] = f1_can_ax
                        axon_sim['f2_can'] = f2_can_ax
                        axon_sim['d_cat'] = d_cat_ax
                        axon_sim['f_cat'] = f_cat_ax
                        axon_sim['p_ka'] = p_ka_ax
                        axon_sim['q_ka'] = q_ka_ax
                        axon_sim['c_ka'] = c_kca_ax
                        axon_sim['n_kd'] = n_kd_ax
                        axon_sim['x_kds'] = x_kds_ax
                        axon_sim['y1_kds'] = y1_kds_ax
                        axon_sim['m_naf'] = m_naf_ax
                        axon_sim['h_naf'] = h_naf_ax
                        axon_sim['l_naf'] = l_naf_ax
                        axon_sim['m_nas'] = m_nas_ax
                        axon_sim['h_nas'] = h_nas_ax
                    else: #should be 'Schild_97'
                        d_can_ax, f1_can_ax, f2_can_ax, d_cat_ax, f_cat_ax, p_ka_ax, q_ka_ax, \
                            c_kca_ax, n_kd_ax, x_kds_ax, y1_kds_ax, m_naf_ax, h_naf_ax, m_nas_ax,\
                            h_nas_ax = self.get_particles_values()
                        axon_sim['d_can'] = d_can_ax
                        axon_sim['f1_can'] = f1_can_ax
                        axon_sim['f2_can'] = f2_can_ax
                        axon_sim['d_cat'] = d_cat_ax
                        axon_sim['f_cat'] = f_cat_ax
                        axon_sim['p_ka'] = p_ka_ax
                        axon_sim['q_ka'] = q_ka_ax
                        axon_sim['c_ka'] = c_kca_ax
                        axon_sim['n_kd'] = n_kd_ax
                        axon_sim['x_kds'] = x_kds_ax
                        axon_sim['y1_kds'] = y1_kds_ax
                        axon_sim['m_naf'] = m_naf_ax
                        axon_sim['h_naf'] = h_naf_ax
                        axon_sim['m_nas'] = m_nas_ax
                        axon_sim['h_nas'] = h_nas_ax
                else:
                    if self.model == 'MRG':
                        m_ax, s_ax, h_ax, mp_ax = self.get_particles_values()
                        axon_sim['m'] = m_ax
                        axon_sim['s'] = s_ax
                        axon_sim['h'] = h_ax
                        axon_sim['mp'] = mp_ax
                    elif self.model in ['Gaines_motor', 'Gaines_sensory', 'Extended_Gaines']:
                        m_ax, mp_ax, s_ax, h_ax, n_ax = self.get_particles_values()
                        axon_sim['m'] = m_ax
                        axon_sim['mp'] = mp_ax
                        axon_sim['s'] = s_ax
                        axon_sim['h'] = h_ax
                        axon_sim['n'] = n_ax
                    else: # Should be RGK
                        RGK_m_nav1p9_ax, RGK_h_nav1p9_ax, RGK_s_nav1p9_ax, RGK_m_nax_ax, \
                            RGK_h_nax_ax, RGK_ns_ks_ax, RGK_nf_ks_ax = self.get_particles_values()
                        axon_sim['m_nav19'] = RGK_m_nav1p9_ax
                        axon_sim['h_nav19'] = RGK_h_nav1p9_ax
                        axon_sim['s_nav19'] = RGK_s_nav1p9_ax
                        axon_sim['m_nax'] = RGK_m_nax_ax
                        axon_sim['h_nax'] = RGK_h_nax_ax
                        axon_sim['ns_ks'] = RGK_ns_ks_ax
                        axon_sim['nf_ks'] = RGK_nf_ks_ax
                if hasattr(self, 'Markov_Nav_modeled_NoR'):
                    I_nav11_ax, C1_nav11_ax, C2_nav11_ax, O1_nav11_ax, O2_nav11_ax, I1_nav11_ax,\
                        I2_nav11_ax, I_nav16_ax, C1_nav16_ax, C2_nav16_ax, O1_nav16_ax, O2_nav16_ax, I1_nav16_ax, I2_nav16_ax = self.get_Nav_values()
                    axon_sim['I_Nav11'] = I_nav11_ax
                    axon_sim['C1_nav11'] = C1_nav11_ax
                    axon_sim['C2_nav11'] = C2_nav11_ax
                    axon_sim['O1_nav11'] = O1_nav11_ax
                    axon_sim['O2_nav11'] = O2_nav11_ax
                    axon_sim['I1_nav11'] = I1_nav11_ax
                    axon_sim['I2_nav11'] = I2_nav11_ax
                    axon_sim['I_Nav16'] = I_nav16_ax
                    axon_sim['C1_nav16'] = C1_nav16_ax
                    axon_sim['C2_nav16'] = C2_nav16_ax
                    axon_sim['O1_nav16'] = O1_nav16_ax
                    axon_sim['O2_nav16'] = O2_nav16_ax
                    axon_sim['I1_nav16'] = I1_nav16_ax
                    axon_sim['I2_nav16'] = I2_nav16_ax
        except KeyboardInterrupt:
            rise_error('\n Caught KeyboardInterrupt, simulation stoped by user, \
                stopping process...')
            raise KeyboardInterrupt
            sys.exit(1)
        except:
            axon_sim['Simulation_state'] = 'Unsuccessful'
            axon_sim['Error_from_prompt'] = traceback.format_exc()
            rise_warning('Simulation induced an error while using neuron: \n' + axon_sim['Error_from_prompt'])
            axon_sim['Neuron_t_max'] = neuron.h.t
        return axon_sim

    ##############################
    ## Result recording methods ##
    ##############################
    def __set_time_recorder(self):
        """
        internal use: set recorders in neuron for the time vector
        """
        self.timeVector = neuron.h.Vector().record(neuron.h._ref_t)

    def __get_time_vector(self):
        """
        internal use: get the time vector and stor its length for further use

        Returns
        -------
        t   : np.array
            time vector of the previous simulation, numpy array
        """
        t = np.array(self.timeVector)
        self.t_len = len(t)
        return t
