"""
NRV-unmyelinated
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import math
import numpy as np
from .axons import *
from .log_interface import rise_error, rise_warning, pass_info

class unmyelinated(axon):
    """
    Unmyelineated axon class. Automatic refinition of all neuron sections and properties. User-friendly object including model definition
    Inherit from axon class. see axon for further detail.
    """
    def __init__(self, y, z, d, L, model='Rattay_Aberham', dt=0.001, Nrec=0, Nsec=1, \
        Nseg_per_sec=0, freq=100, freq_min=0, mesh_shape='plateau_sigmoid', alpha_max=0.3,\
         d_lambda=0.1, v_init=None, T=None, ID=0, threshold=-40):
        """
        initialisation of an unmyelinted axon

        Parameters
        ----------
        y               : float
            y coordinate for the axon, in um
        z               : float
            z coordinate for the axon, in um
        d               : float
            axon diameter, in um
        L               : float
            axon length along the x axins, in um
        model           : str
            choice of conductance based model, possibly:
                'HH'                : original squid giant axon model, warning - low temperature model, not adapted to mamalian modeling
                'Rattay_Aberham'    : Rattay Aberham model, see [1] for details
                'Sundt'             : Sundt model, see [1] for details
                'Tigerholm'         : Tigerholm model, see [1] for details
                'Schild_94'         : Schild 1994 model, see [1] for details
                'Schild_97'         : Schild 1997 model, see [1] for details
        dt              : float
            computation step for simulations, in ms. By default equal to 1 us
        Nrec            : int
            Number of points along the axon to record for simulation results. Between 0 and the number of segment, if set to 0, all segments are recorded
        Nsec            : int
            Number of sections in the axon, by default 1. Usefull to create umnyelinated axons with a variable segment density
        Nseg_per_sec    : int
            Number of segment per section in the axon. If set to 0, the number of segment is automatically computed using d-lambda rule and following paramters. If set by user, please use odd numbers
        freq            : float
            Frequency used for the d-lmbda rule, corresponding to the maximum membrane current frequency, by default set to 100 Hz
        freq_min        : float
            Minimal frequency fot the d-lambda rule when using an irregular number of segment along the axon, if set to 0, all sections have the same frequency determined by the previous parameter
        mesh_shape      : str
            Shape of the frequencial distribution for the dlmabda rule along the axon, pick between:
                'pyramidal'         -> min frequencies on both sides and linear increase up to the middle at the maximum frequency
                'sigmoid'           -> same a befor with sigmoid increase instead of linear
                'plateau'           -> sale as pyramidal except the max frequency is holded on a central plateau
                'plateau_sigmoid'   -> same as previous with sigmoid increase
        alpha_max       : float
            Proportion of the axon set to the maximum frequency for plateau shapes, by default set to 0.3
        d_lambda        : float
            value of d-lambda for the dlambda rule,
        v_init          : float
            Initial value of the membrane voltage in mV, set None to get an automatically model attributed value
        T               : float
            temperature in C, set None to get an automatically model attributed value
        ID              : int
            axon ID, by default set to 0,
        threshold       : float
            voltage threshold in mV for further spike detection in post-processing, by defautl set to -40mV, see post-processing files for further help

        Note
        ----
        reference [1] corresponds to:
            Pelot, N. A., Catherall, D. C., Thio, B. J., Titus, N. D., Liang, E. D., Henriquez, C. S., & Grill, W. M. (2021). Excitation properties of computational models of unmyelinated peripheral axons. Journal of neurophysiology, 125(1), 86-104.
        """
        super().__init__(y, z, d, L, dt=dt, Nseg_per_sec=Nseg_per_sec,\
            freq=freq, freq_min=freq_min, mesh_shape=mesh_shape, alpha_max=alpha_max, \
            d_lambda=d_lambda, v_init=v_init, T=T, ID=ID, threshold=threshold)
        self.Nsec = Nsec
        self.myelinated = False
        if model in unmyelinated_models:
            self.model = model
        else:
            self.model = 'Rattay_Aberham'
        ## Handling v_init
        if v_init is None:
            # model driven
            if self.model == 'HH':
                self.v_init = -67.5
            elif self.model == 'Rattay_Aberham':
                self.v_init = -70
            elif self.model == 'Sundt':
                self.v_init = -60
            elif self.model == 'Tigerholm':
                self.v_init = -62   # -55 in Pelot 2020, changed by FK 19/01/2021
            else:
                self.v_init = -70
        else:
            # user driven
            self.v_init = v_init
        ## Handling temperature
        if T is None:
            # model driven
            if self.model == 'HH':
                self.T = 32 # original HH model, cold model, maximal temperature at which spike propagation is not altered
            else:
                self.T = 37 # mamalian models
        else:
            # user driven
            self.T = T
        # create and connect (if more than 1) sections
        self.unmyelinated_sections = [neuron.h.Section(name='U_axon[%d]' % i) for i in \
            range(self.Nsec)]
        for sec in self.unmyelinated_sections:
            # morphologic parameters
            sec.L = self.L/self.Nsec
            sec.diam = self.d
        if self.Nsec > 1:
            for i in range(self.Nsec -1):
                self.unmyelinated_sections[i+1].connect(self.unmyelinated_sections[i], 1, 0)
        # implement neuron mechanisms
        self.__set_model(self.model)
        # define the geometry of the axon
        self._axon__define_shape()
        # define the number of segments
        self.__set_Nseg()
        # get nodes positions
        self.__get_seg_positions()
        self.__get_rec_positions(Nrec)

    def __set_Nseg(self):
        """
        sets the number of segment, either with the number chosen by user,
        or using the dlambda rule, or using the dlambda rule with a frequency array
        of different shapes (see create_Nseg_freq_shape() help for more details on shapes)
        """
        if self.freq_min == 0 or self.Nsec == 1: # uniform meshing
            # compute the correct number of segments if needed, or take the one given by user
            if self.Nseg_per_sec != 0:
                Nseg = self.Nseg_per_sec
            else:
                Nseg = d_lambda_rule(self.unmyelinated_sections[0].L, self.d_lambda, self.freq,\
                self.unmyelinated_sections[0])
            # set the number of segment for all declared sections
            for sec in self.unmyelinated_sections:
                sec.nseg = Nseg
                if self.model == 'Schild_94' or self.model == 'Schild_97':
                    sec.nseg_caintscale = Nseg
                    sec.nseg_caextscale = Nseg
                self.Nseg += Nseg
        else: # non uniform meshing
            freqs = create_Nseg_freq_shape(self.Nsec, self.mesh_shape, self.freq, self.freq_min,\
                self.alpha_max)
            for k in range(self.Nsec):
                Nseg = d_lambda_rule(self.unmyelinated_sections[k].L, self.d_lambda, freqs[k], \
                    self.unmyelinated_sections[k])
                self.unmyelinated_sections[k].nseg = Nseg
                if self.model == 'Schild_94' or self.model == 'Schild_97':
                    sec.nseg_caintscale = Nseg
                    sec.nseg_caextscale = Nseg
                self.Nseg += Nseg

    def __get_seg_positions(self):
        """
        get all the computation position of the axon. This corresponds to the positions of the segment
        without the duplicates of connected sections
        """
        x_offset = 0
        x = []
        for sec in self.unmyelinated_sections:
            for seg in sec.allseg():
                if x == []:
                    x.append(seg.x*(sec.L) + x_offset)
                else:
                    x_seg = seg.x*(sec.L) + x_offset
                    if x_seg != x[-1]:
                        x.append(x_seg)
            x_offset += sec.L
        self.x = np.asarray(x)

    def __get_rec_positions(self, Nrec):
        """
        get recording x-coordinates and relative positions, for internal use only

        Parameters
        ----------
        Nrec    : int
            number of points to record in the axon during the simulation, can be chosen between 3 and maximum the number of programmed segments + 2 (both sides)
            or will be by default set to the nearest value
        """
        self.rec_position_list = []
        for k in range(self.Nsec):
            self.rec_position_list.append([])
        if Nrec < 4 and Nrec != 0:
            self.Nrec = 3 # at least, 3 positions will be memorized along the axon (extrema and middle)
            self.rec_position_list[0].append(0)
            if (self.Nsec % 2) == 0:
                self.rec_position_list[self.Nsec/2].append(0)
            else:
                self.rec_position_list[math.floor(self.Nsec/2)].append(0.5)
            self.rec_position_list[-1].append(1)
            self.x_rec = np.array([0, self.L/2, self.L])
        elif Nrec == 0 or Nrec > self.Nsec + self.Nseg: # record on all nodes
            self.Nrec = self.Nsec + self.Nseg + 1
            for k in range(self.Nsec):
                for seg in self.unmyelinated_sections[k].allseg():
                    self.rec_position_list[k].append(seg.x)
                # delete last position as it will be a dupplicate with next section first seg
                del self.rec_position_list[k][-1]
            # for the last section only, add the max position
            self.rec_position_list[-1].append(1)
            self.x_rec = self.x
        else:
            self.Nrec = Nrec
            self.rec_position_list[0].append(0)
            remaining_recs = np.arange(1, self.Nrec-1)*(self.Nsec/(self.Nrec - 1))
            for rec in remaining_recs:
                self.rec_position_list[math.floor(rec)].append(rec - math.floor(rec))
            self.rec_position_list[-1].append(1)
            self.x_rec = np.linspace(0, self.L, num=self.Nrec, endpoint=True)

    def __set_model(self, model):
        """
        Adds the passive, Hodgking Huxley and extracellular mechanisms,
        set values to to one given by user at the initialisation or default ones. For internal use only.
        """
        for sec in self.unmyelinated_sections:
            # insert mechanisms
            if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
                sec.insert('pas')
            sec.insert('extracellular')
            sec.xg[0] = 1e10 # short circuit, no myelin
            sec.xc[0] = 0    # short circuit, no myelin
            ## Except for HH, the following code is directly take from modelDB: https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=266498#tabs-1
            ## Pelot N (2020) Excitation Properties of Computational Models of Unmyelinated Peripheral Axons J Neurophysiology
            if model == 'HH':
                sec.insert('hh')
                # explicit mechanisms settings
                sec.cm = 1.0
                sec.Ra = 200.0
                sec.gnabar_hh = 0.120
                sec.gkbar_hh = 0.036
                sec.gl_hh = 0.0003
                sec.ena = 50
                sec.ek = -77
                sec.el_hh = -54.3
            elif model == 'Rattay_Aberham':
                sec.insert('RattayAberham') # Model adjusted for a resting potential of -70mV instead of 0 (subtract Vrest from each reversal potential)
                sec.Ra = 100
                sec.cm = 1
                sec.v = -70
                sec.ena = 45
                sec.ek = -82
                sec.e_pas = -70
            elif model == 'Sundt':
                sec.insert('nahh')
                sec.gnabar_nahh = .04
                sec.mshift_nahh = -6            # NaV1.7/1.8 channelshift
                sec.hshift_nahh = 6             # NaV1.7/1.8 channelshift

                sec.insert('borgkdr')           # insert delayed rectifier K channels
                sec.gkdrbar_borgkdr = .04       # density of K channels
                sec.ek = -90                    # K equilibrium potential

                sec.g_pas = 1/10000             # set Rm = 10000 ohms-cm2
                sec.Ra = 100                    # intracellular resistance
                sec.v = -60
                sec.e_pas = sec.v + (sec.ina + sec.ik)/sec.g_pas    # calculate leak equilibrium potential
            elif self.model == 'Tigerholm':
                sec.insert('ks')
                sec.gbar_ks = 0.0069733
                sec.insert('kf')
                sec.gbar_kf = 0.012756
                sec.insert('h')
                sec.gbar_h = 0.0025377
                sec.insert('nattxs')
                sec.gbar_nattxs = 0.10664
                sec.insert('nav1p8')
                sec.gbar_nav1p8 = 0.24271
                sec.insert('nav1p9')
                sec.gbar_nav1p9 = 9.4779e-05
                sec.insert('nakpump')
                sec.smalla_nakpump = -0.0047891
                sec.insert('kdrTiger')
                sec.gbar_kdrTiger = 0.018002
                sec.insert('kna')
                sec.gbar_kna = 0.00042
                sec.insert('naoi')

                sec.insert('koi')
                sec.theta_naoi = 0.029
                sec.theta_koi = 0.029

                sec.insert('leak')
                sec.insert('extrapump')

                sec.Ra = 35.5
                sec.cm = 1.

                sec.celsiusT_ks = self.T
                sec.celsiusT_kf = self.T
                sec.celsiusT_h = self.T
                sec.celsiusT_nattxs = self.T
                sec.celsiusT_nav1p8 = self.T
                sec.celsiusT_nav1p9 = self.T
                sec.celsiusT_nakpump = self.T
                sec.celsiusT_kdrTiger = self.T
                sec.v = -55
            else: # Schild 94 or 97 models
                R = 8314
                F = 96500
                sec.insert('leakSchild')                        # All mechanisms from Schild 1994 inserted into model
                sec.insert('kd')
                sec.insert('ka')
                sec.insert('can')
                sec.insert('cat')
                sec.insert('kds')
                sec.insert('kca')
                sec.insert('caextscale')
                sec.insert('caintscale')
                sec.insert('CaPump')
                sec.insert('NaCaPump')
                sec.insert('NaKpumpSchild')
                if self.model == 'Schild_94':
                    sec.insert('naf')
                    sec.insert('nas')
                else:
                    sec.insert('naf97mean')
                    sec.insert('nas97mean')
                # Ionic concentrations
                #cao0_ca_ion = 2.0                                      # not in section, adapter considering: https://neuronsimulator.github.io/nrn/rxd-tutorials/initialization.html
                neuron.h.cao0_ca_ion = 2.0                              # [mM] Initial Cao Concentration
                #cai0_ca_ion = 0.000117                                 # same as cao_ca_ion
                neuron.h.cai0_ca_ion = 0.000117                         # [mM] Initial Cai Concentrations
                ko = 5.4                                                # [mM] External K Concentration
                ki = 145.0                                              # [mM] Internal K Concentration
                kstyle = neuron.h.ion_style("k_ion", 1, 2, 0, 0, 0)     # Allows ek to be calculated manually
                sec.ek = ((R*(self.T+273.15))/F)*math.log(ko/ki)        # Manual Calculation of ek in order to use Schild F and R values
                nao = 154.0                                             # [mM] External Na Concentration
                nai = 8.9                                               # [mM] Internal Na Concentration
                nastyle = neuron.h.ion_style("na_ion", 1, 2, 0, 0, 0)   # Allows ena to be calculated manually
                sec.ena = ((R*(self.T+273.15))/F)*math.log(nao/nai)     # Manual Calculation of ena in order to use Schild F and R values
                if self.model == 'Schild_97':
                    sec.gbar_naf97mean = 0.022434928                    # [S/cm^2] This block sets the conductance to the conductances in Schild 1997
                    sec.gbar_nas97mean = 0.022434928
                    sec.gbar_kd = 0.001956534
                    sec.gbar_ka = 0.001304356
                    sec.gbar_kds = 0.000782614
                    sec.gbar_kca = 0.000913049
                    sec.gbar_can = 0.000521743
                    sec.gbar_cat = 0.00018261
                    sec.gbna_leakSchild = 1.8261e-05
                    sec.gbca_leakSchild = 9.13049e-06
                sec.Ra = 100
                sec.cm = 1.326291192
                sec.v = -48
                sec.L_caintscale = self.L/self.Nsec
                sec.L_caextscale = self.L/self.Nsec

    ###############################
    ## Intracellular stimulation ##
    ###############################
    def insert_I_Clamp(self, position, t_start, duration, amplitude):
        """
        Insert a I clamp stimulation

        Parameters
        ----------
        position    : float
            relative position over the axon
        t_start     : float
            starting time, in ms
        duration    : float
            duration of the pulse, in ms
        amplitude   : float
            amplitude of the pulse (nA)
        """
        # adapt position to the number of sections
        portion_length = 1./self.Nsec
        stim_sec = int(math.floor(position/portion_length))
        stim_pos = (position/portion_length) - math.floor(position/portion_length)
        # add the stimulation to the axon
        self.intra_current_stim.append(neuron.h.IClamp(stim_pos, sec=self.unmyelinated_sections[stim_sec]))
        # modify the stimulation parameters
        self.intra_current_stim[-1].delay = t_start
        self.intra_current_stim[-1].dur = duration
        self.intra_current_stim[-1].amp = amplitude
        # save the stimulation parameter for results
        self.intra_current_stim_positions.append(position*self.L)
        self.intra_current_stim_starts.append(t_start)
        self.intra_current_stim_durations.append(duration)
        self.intra_current_stim_amplitudes.append(amplitude)

    def insert_V_Clamp(self, position, stimulus):
        """
        Insert a V clamp stimulation

        Parameters
        ----------
        position    : float
            relative position over the axon
        stimulus    : stimulus object
            stimulus for the clamp, see Stimulus.py for more information
        """
        # adapt position to the number of sections
        portion_length = 1./self.Nsec
        stim_sec = int(math.floor(position/portion_length))
        stim_pos = (position/portion_length) - math.floor(position/portion_length)
        # add the stimulation to the axon
        self.intra_voltage_stim = neuron.h.VClamp(stim_pos, sec=self.unmyelinated_sections[stim_sec])
        # save the stimulation parameter for results
        self.intra_current_stim_position = position*self.L
        # save the stimulus for later use
        self.intra_voltage_stim_stimulus = stimulus
        # set fake duration
        self.intra_voltage_stim.dur[0] = 1e9

    ##############################
    ## Result recording methods ##
    ##############################
    def set_membrane_voltage_recorders(self):
        """
        Prepare the membrane voltage recording. For internal use only.
        """
        self.vreclist = neuron.h.List()
        for k in range(self.Nsec):
            for pos in self.rec_position_list[k]:
                vrec = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_v,\
                    sec=self.unmyelinated_sections[k])
                self.vreclist.append(vrec)

    def get_membrane_voltage(self):
        """
        get the membrane voltage at the end of simulation. For internal use only.
        """
        vax = np.zeros((self.Nrec, self.t_len))
        for k in range(self.Nrec):
            vax[k, :] = np.asarray(self.vreclist[k])
        return vax

    def set_membrane_current_recorders(self):
        """
        Prepare the membrane current recording. For internal use only.
        """
        self.ireclist = neuron.h.List()
        for k in range(self.Nsec):
            for pos in self.rec_position_list[k]:
                i_mem_rec = neuron.h.Vector().record(\
                    self.unmyelinated_sections[k](pos)._ref_i_membrane,\
                    sec=self.unmyelinated_sections[k])
                self.ireclist.append(i_mem_rec)

    def get_membrane_current(self):
        """
        get the membrane current at the end of simulation. For internal use only.
        """
        iax = np.zeros((self.Nrec, self.t_len))
        for k in range(self.Nrec):
            iax[k, :] = np.asarray(self.ireclist[k])
        return iax

    def set_ionic_current_recorders(self):
        """
        Prepare the ionic currents recording. For internal use only.
        """
        if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
            self.i_na_reclist = neuron.h.List()
            self.i_k_reclist = neuron.h.List()
            self.i_l_reclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    i_na_rec = neuron.h.Vector().record(\
                        self.unmyelinated_sections[k](pos)._ref_nai,\
                         sec=self.unmyelinated_sections[k])
                    i_k_rec = neuron.h.Vector().record(\
                        self.unmyelinated_sections[k](pos)._ref_ki,\
                        sec=self.unmyelinated_sections[k])
                    i_l_rec = neuron.h.Vector().record(\
                        self.unmyelinated_sections[k](pos)._ref_i_pas,\
                        sec=self.unmyelinated_sections[k])
                    self.i_na_reclist.append(i_na_rec)
                    self.i_k_reclist.append(i_k_rec)
                    self.i_l_reclist.append(i_l_rec)
        else:
            self.i_na_reclist = neuron.h.List()
            self.i_k_reclist = neuron.h.List()
            self.i_ca_reclist = neuron.h.List()
            self.i_l_reclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    i_na_rec = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_nai, sec=self.unmyelinated_sections[k])
                    i_k_rec = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_ki, sec=self.unmyelinated_sections[k])
                    i_ca_rec = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_cai, sec=self.unmyelinated_sections[k])
                    self.i_na_reclist.append(i_na_rec)
                    self.i_k_reclist.append(i_k_rec)
                    self.i_ca_reclist.append(i_ca_rec)

    def get_ionic_current(self):
        """
        get the ionic currents at the end of simulation. For internal use only.
        """
        if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
            i_na_ax = np.zeros((self.Nrec, self.t_len))
            i_k_ax = np.zeros((self.Nrec, self.t_len))
            i_l_ax = np.zeros((self.Nrec, self.t_len))
            for k in range(self.Nrec):
                i_na_ax[k, :] = np.asarray(self.i_na_reclist[k])
                i_k_ax[k, :] = np.asarray(self.i_k_reclist[k])
                i_l_ax[k, :] = np.asarray(self.i_l_reclist[k])
            results = [i_na_ax, i_k_ax, i_l_ax]
        else:
            i_na_ax = np.zeros((self.Nrec, self.t_len))
            i_k_ax = np.zeros((self.Nrec, self.t_len))
            i_ca_ax = np.zeros((self.Nrec, self.t_len))
            for k in range(self.Nrec):
                i_na_ax[k, :] = np.asarray(self.i_na_reclist[k])
                i_k_ax[k, :] = np.asarray(self.i_k_reclist[k])
                i_ca_ax[k, :] = np.asarray(self.i_ca_reclist[k])
            results = [i_na_ax, i_k_ax, i_ca_ax]
        return results


    def set_particules_values_recorders(self):
        """
        Prepare the particule value recording. For internal use only.
        """
        if self.model == 'HH':
            self.hhmreclist = neuron.h.List()
            self.hhnreclist = neuron.h.List()
            self.hhhreclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    hhm = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_hh, sec=self.unmyelinated_sections[k])
                    hhn = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_n_hh, sec=self.unmyelinated_sections[k])
                    hhh = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_hh, sec=self.unmyelinated_sections[k])
                    self.hhmreclist.append(hhm)
                    self.hhnreclist.append(hhn)
                    self.hhhreclist.append(hhh)
        elif self.model == 'Rattay_Aberham':
            self.hhmreclist = neuron.h.List()
            self.hhnreclist = neuron.h.List()
            self.hhhreclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    hhm = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_RattayAberham, sec=self.unmyelinated_sections[k])
                    hhn = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_n_RattayAberham, sec=self.unmyelinated_sections[k])
                    hhh = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_RattayAberham, sec=self.unmyelinated_sections[k])
                    self.hhmreclist.append(hhm)
                    self.hhnreclist.append(hhn)
                    self.hhhreclist.append(hhh)
        elif self.model == 'Sundt':
            self.hhmreclist = neuron.h.List()
            self.hhnreclist = neuron.h.List()
            self.hhhreclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    hhm = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nahh, sec=self.unmyelinated_sections[k])
                    hhn = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_n_borgkdr, sec=self.unmyelinated_sections[k])
                    hhh = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nahh, sec=self.unmyelinated_sections[k])
                    self.hhmreclist.append(hhm)
                    self.hhnreclist.append(hhn)
                    self.hhhreclist.append(hhh)
        elif self.model == 'Tigerholm':
            # NAV 1.8
            self.m_nav18_reclist = neuron.h.List()
            self.h_nav18_reclist = neuron.h.List()
            self.s_nav18_reclist = neuron.h.List()
            self.u_nav18_reclist = neuron.h.List()
            # NAV 1.9
            self.m_nav19_reclist = neuron.h.List()
            self.h_nav19_reclist = neuron.h.List()
            self.s_nav19_reclist = neuron.h.List()
            # NATTX - sensitive
            self.m_nattxs_reclist = neuron.h.List()
            self.h_nattxs_reclist = neuron.h.List()
            self.s_nattxs_reclist = neuron.h.List()
            # K delayed rectifier
            self.n_kdr_reclist = neuron.h.List()
            # K fast channel
            self.m_kf_reclist = neuron.h.List()
            self.h_kf_reclist = neuron.h.List()
            # K slow channel
            self.ns_ks_reclist = neuron.h.List()
            self.nf_ks_reclist = neuron.h.List()
            # Sodium dependent K channel
            self.w_kna_reclist = neuron.h.List()
            # Hyperpolarization channel
            self.ns_h_reclist = neuron.h.List()
            self.nf_h_reclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    # NAV 1.8
                    m_nav18 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nav1p8, sec=self.unmyelinated_sections[k])
                    h_nav18 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nav1p8, sec=self.unmyelinated_sections[k])
                    s_nav18 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_s_nav1p8, sec=self.unmyelinated_sections[k])
                    u_nav18 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_u_nav1p8, sec=self.unmyelinated_sections[k])
                    self.m_nav18_reclist.append(m_nav18)
                    self.h_nav18_reclist.append(h_nav18)
                    self.s_nav18_reclist.append(s_nav18)
                    self.u_nav18_reclist.append(u_nav18)
                    # NAV 1.9
                    m_nav19 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nav1p9, sec=self.unmyelinated_sections[k])
                    h_nav19 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nav1p9, sec=self.unmyelinated_sections[k])
                    s_nav19 = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_s_nav1p9, sec=self.unmyelinated_sections[k])
                    self.m_nav19_reclist.append(m_nav19)
                    self.h_nav19_reclist.append(h_nav19)
                    self.s_nav19_reclist.append(s_nav19)
                    # NATTX - sensitive
                    m_nattxs = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nattxs, sec=self.unmyelinated_sections[k])
                    h_nattxs = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nattxs, sec=self.unmyelinated_sections[k])
                    s_nattxs = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_s_nattxs, sec=self.unmyelinated_sections[k])
                    self.m_nattxs_reclist.append(m_nattxs)
                    self.h_nattxs_reclist.append(h_nattxs)
                    self.s_nattxs_reclist.append(s_nattxs)
                    # K delayed rectifier
                    n_kdr = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_n_kdrTiger, sec=self.unmyelinated_sections[k])
                    self.n_kdr_reclist.append(n_kdr)
                    # K fast channel
                    m_kf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_kf, sec=self.unmyelinated_sections[k])
                    h_kf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_kf, sec=self.unmyelinated_sections[k])
                    self.m_kf_reclist.append(m_kf)
                    self.h_kf_reclist.append(h_kf)
                    # K slow channel
                    ns_ks = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_ns_ks, sec=self.unmyelinated_sections[k])
                    nf_ks = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_nf_ks, sec=self.unmyelinated_sections[k])
                    self.ns_ks_reclist.append(ns_ks)
                    self.nf_ks_reclist.append(nf_ks)
                    # Sodium dependent K channel
                    w_kna = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_w_kna, sec=self.unmyelinated_sections[k])
                    self.w_kna_reclist.append(w_kna)
                    # Hyperpolarization channel
                    ns_h = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_ns_h, sec=self.unmyelinated_sections[k])
                    nf_h = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_nf_h, sec=self.unmyelinated_sections[k])
                    self.ns_h_reclist.append(ns_h)
                    self.nf_h_reclist.append(nf_h)
        else: # should be both Schild_94 or Schild_97
            # High Threshold long lasting Ca
            self.d_can_reclist = neuron.h.List()
            self.f1_can_reclist = neuron.h.List()
            self.f2_can_reclist = neuron.h.List()
            # Low Threshold transient Ca
            self.d_cat_reclist = neuron.h.List()
            self.f_cat_reclist = neuron.h.List()
            # Early Transient Outward K
            self.p_ka_reclist = neuron.h.List()
            self.q_ka_reclist = neuron.h.List()
            # Ca activated K
            self.c_kca_reclist = neuron.h.List()
            # Delayed rectifier K
            self.n_kd_reclist = neuron.h.List()
            # Slowly inactivated K
            self.x_kds_reclist = neuron.h.List()
            self.y1_kds_reclist = neuron.h.List()
            for k in range(self.Nsec):
                for pos in self.rec_position_list[k]:
                    # High Threshold long lasting Ca
                    d_can = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_d_can, sec=self.unmyelinated_sections[k])
                    f1_can = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_f1_can, sec=self.unmyelinated_sections[k])
                    f2_can = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_f2_can, sec=self.unmyelinated_sections[k])
                    self.d_can_reclist.append(d_can)
                    self.f1_can_reclist.append(f1_can)
                    self.f2_can_reclist.append(f2_can)
                    # Low Threshold transient Ca
                    d_cat = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_d_cat, sec=self.unmyelinated_sections[k])
                    f_cat = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_f_cat, sec=self.unmyelinated_sections[k])
                    self.d_cat_reclist.append(d_cat)
                    self.f_cat_reclist.append(f_cat)
                    # Early Transient Outward K
                    p_ka = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_p_ka, sec=self.unmyelinated_sections[k])
                    q_ka = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_q_ka, sec=self.unmyelinated_sections[k])
                    self.p_ka_reclist.append(p_ka)
                    self.q_ka_reclist.append(q_ka)
                    # Ca activated K
                    c_kca = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_c_kca, sec=self.unmyelinated_sections[k])
                    self.c_kca_reclist.append(c_kca)
                    # Delayed rectifier K
                    n_kd = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_n_kd, sec=self.unmyelinated_sections[k])
                    self.n_kd_reclist.append(n_kd)
                    # Slowly inactivated K
                    x_kds = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_x_kds, sec=self.unmyelinated_sections[k])
                    y1_kds = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_y1_kds, sec=self.unmyelinated_sections[k])
                    self.x_kds_reclist.append(x_kds)
                    self.y1_kds_reclist.append(y1_kds)
            if self.model == 'Schild_94':
                # Fast Na
                self.m_naf_reclist = neuron.h.List()
                self.h_naf_reclist = neuron.h.List()
                self.l_naf_reclist = neuron.h.List()
                # Slow Na
                self.m_nas_reclist = neuron.h.List()
                self.h_nas_reclist = neuron.h.List()
                for k in range(self.Nsec):
                    for pos in self.rec_position_list[k]:
                        # Fast Na
                        m_naf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_naf, sec=self.unmyelinated_sections[k])
                        h_naf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_naf, sec=self.unmyelinated_sections[k])
                        l_naf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_l_naf, sec=self.unmyelinated_sections[k])
                        self.m_naf_reclist.append(m_naf)
                        self.h_naf_reclist.append(h_naf)
                        self.l_naf_reclist.append(l_naf)
                        # Slow Na
                        m_nas = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nas, sec=self.unmyelinated_sections[k])
                        h_nas = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nas, sec=self.unmyelinated_sections[k])
                        self.m_nas_reclist.append(m_nas)
                        self.h_nas_reclist.append(h_nas)
            else: # should be Schild_94
                # Fast Na
                self.m_naf_reclist = neuron.h.List()
                self.h_naf_reclist = neuron.h.List()
                # Slow Na
                self.m_nas_reclist = neuron.h.List()
                self.h_nas_reclist = neuron.h.List()
                for k in range(self.Nsec):
                    for pos in self.rec_position_list[k]:
                        # Fast Na
                        m_naf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_naf97mean, sec=self.unmyelinated_sections[k])
                        h_naf = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_naf97mean, sec=self.unmyelinated_sections[k])
                        self.m_naf_reclist.append(m_naf)
                        self.h_naf_reclist.append(h_naf)
                        # Slow Na
                        m_nas = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_m_nas97mean, sec=self.unmyelinated_sections[k])
                        h_nas = neuron.h.Vector().record(self.unmyelinated_sections[k](pos)._ref_h_nas97mean, sec=self.unmyelinated_sections[k])
                        self.m_nas_reclist.append(m_nas)
                        self.h_nas_reclist.append(h_nas)

    def get_particles_values(self):
        """
        get the particules values at the end of simulation. For internal use only.
        """
        if self.model in ['HH', 'Rattay_Aberham', 'Sundt']:
            m_ax = np.zeros((self.Nrec, self.t_len))
            n_ax = np.zeros((self.Nrec, self.t_len))
            h_ax = np.zeros((self.Nrec, self.t_len))
            for k in range(self.Nrec):
                m_ax[k, :] = np.asarray(self.hhmreclist[k])
                n_ax[k, :] = np.asarray(self.hhnreclist[k])
                h_ax[k, :] = np.asarray(self.hhhreclist[k])
            results = [m_ax, n_ax, h_ax]
        elif self.model in ['Tigerholm']:
            m_nav18_ax = np.zeros((self.Nrec, self.t_len))
            h_nav18_ax = np.zeros((self.Nrec, self.t_len))
            s_nav18_ax = np.zeros((self.Nrec, self.t_len))
            u_nav18_ax = np.zeros((self.Nrec, self.t_len))
            m_nav19_ax = np.zeros((self.Nrec, self.t_len))
            h_nav19_ax = np.zeros((self.Nrec, self.t_len))
            s_nav19_ax = np.zeros((self.Nrec, self.t_len))
            m_nattxs_ax = np.zeros((self.Nrec, self.t_len))
            h_nattxs_ax = np.zeros((self.Nrec, self.t_len))
            s_nattxs_ax = np.zeros((self.Nrec, self.t_len))
            n_kdr_ax = np.zeros((self.Nrec, self.t_len))
            m_kf_ax = np.zeros((self.Nrec, self.t_len))
            h_kf_ax = np.zeros((self.Nrec, self.t_len))
            ns_ks_ax = np.zeros((self.Nrec, self.t_len))
            nf_ks_ax = np.zeros((self.Nrec, self.t_len))
            w_kna_ax = np.zeros((self.Nrec, self.t_len))
            ns_h_ax = np.zeros((self.Nrec, self.t_len))
            nf_h_ax = np.zeros((self.Nrec, self.t_len))
            for k in range(self.Nrec):
                m_nav18_ax[k, :] = np.asarray(self.m_nav18_reclist[k])
                h_nav18_ax[k, :] = np.asarray(self.h_nav18_reclist[k])
                s_nav18_ax[k, :] = np.asarray(self.s_nav18_reclist[k])
                u_nav18_ax[k, :] = np.asarray(self.u_nav18_reclist[k])
                m_nav19_ax[k, :] = np.asarray(self.m_nav19_reclist[k])
                h_nav19_ax[k, :] = np.asarray(self.h_nav19_reclist[k])
                s_nav19_ax[k, :] = np.asarray(self.s_nav19_reclist[k])
                m_nattxs_ax[k, :] = np.asarray(self.m_nattxs_reclist[k])
                h_nattxs_ax[k, :] = np.asarray(self.h_nattxs_reclist[k])
                s_nattxs_ax[k, :] = np.asarray(self.s_nattxs_reclist[k])
                n_kdr_ax[k, :] = np.asarray(self.n_kdr_reclist[k])
                m_kf_ax[k, :] = np.asarray(self.m_kf_reclist[k])
                h_kf_ax[k, :] = np.asarray(self.h_kf_reclist[k])
                ns_ks_ax[k, :] = np.asarray(self.ns_ks_reclist[k])
                nf_ks_ax[k, :] = np.asarray(self.nf_ks_reclist[k])
                w_kna_ax[k, :] = np.asarray(self.w_kna_reclist[k])
                ns_h_ax[k, :] = np.asarray(self.ns_h_reclist[k])
                nf_h_ax[k, :] = np.asarray(self.nf_h_reclist[k])
            results = [m_nav18_ax, h_nav18_ax, s_nav18_ax, u_nav18_ax, m_nav19_ax, h_nav19_ax,\
                s_nav19_ax, m_nattxs_ax, h_nattxs_ax, s_nattxs_ax, n_kdr_ax, m_kf_ax, h_kf_ax,\
                ns_ks_ax, nf_ks_ax, w_kna_ax, ns_h_ax, nf_h_ax]
        else: # should be 'Schild_94' or 'Schild_97'
            d_can_ax = np.zeros((self.Nrec, self.t_len))
            f1_can_ax = np.zeros((self.Nrec, self.t_len))
            f2_can_ax = np.zeros((self.Nrec, self.t_len))
            d_cat_ax = np.zeros((self.Nrec, self.t_len))
            f_cat_ax = np.zeros((self.Nrec, self.t_len))
            p_ka_ax = np.zeros((self.Nrec, self.t_len))
            q_ka_ax = np.zeros((self.Nrec, self.t_len))
            c_kca_ax = np.zeros((self.Nrec, self.t_len))
            n_kd_ax = np.zeros((self.Nrec, self.t_len))
            x_kds_ax = np.zeros((self.Nrec, self.t_len))
            y1_kds_ax = np.zeros((self.Nrec, self.t_len))
            m_naf_ax = np.zeros((self.Nrec, self.t_len))
            h_naf_ax = np.zeros((self.Nrec, self.t_len))
            m_nas_ax = np.zeros((self.Nrec, self.t_len))
            h_nas_ax = np.zeros((self.Nrec, self.t_len))
            for k in range(self.Nrec):
                d_can_ax[k, :] = np.asarray(self.d_can_reclist[k])
                f1_can_ax[k, :] = np.asarray(self.f1_can_reclist[k])
                f2_can_ax[k, :] = np.asarray(self.f2_can_reclist[k])
                d_cat_ax[k, :] = np.asarray(self.d_cat_reclist[k])
                f_cat_ax[k, :] = np.asarray(self.f_cat_reclist[k])
                p_ka_ax[k, :] = np.asarray(self.p_ka_reclist[k])
                q_ka_ax[k, :] = np.asarray(self.q_ka_reclist[k])
                c_kca_ax[k, :] = np.asarray(self.c_kca_reclist[k])
                n_kd_ax[k, :] = np.asarray(self.n_kd_reclist[k])
                x_kds_ax[k, :] = np.asarray(self.x_kds_reclist[k])
                y1_kds_ax[k, :] = np.asarray(self.y1_kds_reclist[k])
                m_naf_ax[k, :] = np.asarray(self.m_naf_reclist[k])
                h_naf_ax[k, :] = np.asarray(self.h_naf_reclist[k])
                m_nas_ax[k, :] = np.asarray(self.m_nas_reclist[k])
                h_nas_ax[k, :] = np.asarray(self.h_nas_reclist[k])
            if self.model == 'Schild_97':
                results = [d_can_ax, f1_can_ax, f2_can_ax, d_cat_ax, f_cat_ax, p_ka_ax, q_ka_ax,\
                    c_kca_ax, n_kd_ax, x_kds_ax, y1_kds_ax, m_naf_ax, h_naf_ax, m_nas_ax, h_nas_ax]
            else: # should be 'Schild 94'
                l_naf_ax = np.zeros((self.Nrec, self.t_len))
                for k in range(self.Nrec):
                    l_naf_ax[k, :] = np.asarray(self.l_naf_reclist[k])
                results = [d_can_ax, f1_can_ax, f2_can_ax, d_cat_ax, f_cat_ax, p_ka_ax, q_ka_ax,\
                    c_kca_ax, n_kd_ax, x_kds_ax, y1_kds_ax, m_naf_ax, h_naf_ax, l_naf_ax,\
                    m_nas_ax, h_nas_ax]
        return results
