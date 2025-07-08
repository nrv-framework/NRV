"""
NRV-:class:`.unmyelinated` handling.
"""

import math

import numpy as np

from ._axons import (
    axon,
    neuron,
    unmyelinated_models,
    create_Nseg_freq_shape,
    d_lambda_rule,
)
from .results._unmyelinated_results import unmyelinated_results
from ..backend._NRV_Class import is_empty_iterable


class unmyelinated(axon):
    """
    Unmyelinated axon class. Automatic refinition of all neuron sections and properties. User-friendly object including model definition
    Inherit from axon class. see axon for further detail.

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
            "HH"                : original squid giant axon model, warning - low temperature model, not adapted to mamalian modeling
            "Rattay_Aberham"    : Rattay Aberham model, see [1] for details
            "Sundt"             : Sundt model, see [1] for details
            "Tigerholm"         : Tigerholm model, see [1] for details
            "Schild_94"         : Schild 1994 model, see [1] for details
            "Schild_97"         : Schild 1997 model, see [1] for details
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
            "pyramidal"         -> min frequencies on both sides and linear increase up to the middle at the maximum frequency
            "sigmoid"           -> same a befor with sigmoid increase instead of linear
            "plateau"           -> sale as pyramidal except the max frequency is holded on a central plateau
            "plateau_sigmoid"   -> same as previous with sigmoid increase
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

    def __init__(
        self,
        y=0,
        z=0,
        d=1,
        L=1000,
        model="Rattay_Aberham",
        dt=0.001,
        Nrec=0,
        Nsec=1,
        Nseg_per_sec=0,
        freq=100,
        freq_min=0,
        mesh_shape="plateau_sigmoid",
        alpha_max=0.3,
        d_lambda=0.1,
        v_init=None,
        T=None,
        ID=0,
        threshold=-40,
        **kwarks,
    ):
        """
        initialisation of an unmyelinted axon
        """
        super().__init__(
            y,
            z,
            d,
            L,
            dt=dt,
            Nseg_per_sec=Nseg_per_sec,
            freq=freq,
            freq_min=freq_min,
            mesh_shape=mesh_shape,
            alpha_max=alpha_max,
            d_lambda=d_lambda,
            v_init=v_init,
            T=T,
            ID=ID,
            threshold=threshold,
            **kwarks,
        )
        self.Nsec = Nsec
        self.Nrec = Nrec
        self.myelinated = False
        if model in unmyelinated_models:
            self.model = model
        else:
            self.model = "Rattay_Aberham"
        self.__compute_axon_parameters()

    def __compute_axon_parameters(self):
        """
        generate axon from parameters set by user
        """
        ## Handling v_init
        if self.v_init is None:
            # model driven
            if self.model == "HH":
                self.v_init = -67.5
            elif self.model == "Rattay_Aberham":
                self.v_init = -70
            elif self.model == "Sundt":
                self.v_init = -60
            elif self.model == "Tigerholm":
                self.v_init = -62  # -55 in Pelot 2020, changed by FK 19/01/2021
            else:
                self.v_init = -70
        else:
            # user driven
            self.v_init = self.v_init
        ## Handling temperature
        if self.T is None:
            # model driven
            if self.model == "HH":
                self.T = 32  # original HH model, cold model, maximal temperature at which spike propagation is not altered
            else:
                self.T = 37  # mamalian models

        # create and connect (if more than 1) sections
        self.unmyelinated_sections = [
            neuron.h.Section(name="U_axon[%d]" % i) for i in range(self.Nsec)
        ]
        for sec in self.unmyelinated_sections:
            # morphologic parameters
            sec.L = self.L / self.Nsec
            sec.diam = self.d
        if self.Nsec > 1:
            for i in range(self.Nsec - 1):
                self.unmyelinated_sections[i + 1].connect(
                    self.unmyelinated_sections[i], 1, 0
                )
        # implement neuron mechanisms
        self.__set_model(self.model)
        # define the geometry of the axon
        self._axon__define_shape()
        # define the number of segments
        self.__set_Nseg()
        # get nodes positions
        self.__get_seg_positions()
        self.__get_rec_positions(self.Nrec)

    def save(
        self,
        save=False,
        fname="axon.json",
        extracel_context=False,
        intracel_context=False,
        rec_context=False,
        blacklist=[],
    ):
        """
        Return axon as dictionary and eventually save it as json file

        Parameters
        ----------
        save    : bool
            if True, save in json files
        fname   : str
            Path and Name of the saving file, by default "axon.json"

        Returns
        -------
        ax_dic : dict
            dictionary containing all information
        """
        blacklist += ["unmyelinated_sections"]
        return super().save(
            save=save,
            fname=fname,
            extracel_context=extracel_context,
            intracel_context=intracel_context,
            rec_context=rec_context,
            blacklist=blacklist,
        )

    def __set_Nseg(self):
        """
        sets the number of segment, either with the number chosen by user,
        or using the dlambda rule, or using the dlambda rule with a frequency array
        of different shapes (see create_Nseg_freq_shape() help for more details on shapes)
        """
        if self.freq_min == 0 or self.Nsec == 1:  # uniform meshing
            # compute the correct number of segments if needed, or take the one given by user
            if self.Nseg_per_sec != 0:
                Nseg = self.Nseg_per_sec
            else:
                Nseg = d_lambda_rule(
                    self.unmyelinated_sections[0].L,
                    self.d_lambda,
                    self.freq,
                    self.unmyelinated_sections[0],
                )
            # set the number of segment for all declared sections
            for sec in self.unmyelinated_sections:
                sec.nseg = Nseg
                if self.model == "Schild_94" or self.model == "Schild_97":
                    sec.nseg_caintscale = Nseg
                    sec.nseg_caextscale = Nseg
                self.Nseg += Nseg
        else:  # non uniform meshing
            freqs = create_Nseg_freq_shape(
                self.Nsec, self.mesh_shape, self.freq, self.freq_min, self.alpha_max
            )
            for k in range(self.Nsec):
                Nseg = d_lambda_rule(
                    self.unmyelinated_sections[k].L,
                    self.d_lambda,
                    freqs[k],
                    self.unmyelinated_sections[k],
                )
                self.unmyelinated_sections[k].nseg = Nseg
                if self.model == "Schild_94" or self.model == "Schild_97":
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
                if is_empty_iterable(x):
                    x.append(seg.x * (sec.L) + x_offset)
                else:
                    x_seg = seg.x * (sec.L) + x_offset
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
            self.Nrec = 3  # at least, 3 positions will be memorized along the axon (extrema and middle)
            self.rec_position_list[0].append(0)
            if (self.Nsec % 2) == 0:
                self.rec_position_list[self.Nsec / 2].append(0)
            else:
                self.rec_position_list[math.floor(self.Nsec / 2)].append(0.5)
            self.rec_position_list[-1].append(1)
            self.x_rec = np.array([0, self.L / 2, self.L])
        elif Nrec == 0 or Nrec > self.Nsec + self.Nseg:  # record on all nodes
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
            remaining_recs = np.arange(1, self.Nrec - 1) * (self.Nsec / (self.Nrec - 1))
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
            if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
                sec.insert("pas")
            sec.insert("extracellular")
            sec.xg[0] = 1e10  # short circuit, no myelin
            sec.xc[0] = 0  # short circuit, no myelin
            ## Except for HH, the following code is directly take from modelDB: https://senselab.med.yale.edu/ModelDB/showmodel.cshtml?model=266498#tabs-1
            ## Pelot N (2020) Excitation Properties of Computational Models of Unmyelinated Peripheral Axons J Neurophysiology
            if model == "HH":
                sec.insert("hh")
                # explicit mechanisms settings
                sec.cm = 1.0
                sec.Ra = 200.0
                sec.gnabar_hh = 0.120
                sec.gkbar_hh = 0.036
                sec.gl_hh = 0.0003
                sec.ena = 50
                sec.ek = -77
                sec.el_hh = -54.3
            elif model == "Rattay_Aberham":
                sec.insert(
                    "RattayAberham"
                )  # Model adjusted for a resting potential of -70mV instead of 0 (subtract Vrest from each reversal potential)
                sec.Ra = 100
                sec.cm = 1
                sec.v = -70
                sec.ena = 45
                sec.ek = -82
                sec.e_pas = -70
            elif model == "Sundt":
                sec.insert("nahh")
                sec.gnabar_nahh = 0.04
                sec.mshift_nahh = -6  # NaV1.7/1.8 channelshift
                sec.hshift_nahh = 6  # NaV1.7/1.8 channelshift

                sec.insert("borgkdr")  # insert delayed rectifier K channels
                sec.gkdrbar_borgkdr = 0.04  # density of K channels
                sec.ek = -90  # K equilibrium potential

                sec.g_pas = 1 / 10000  # set Rm = 10000 ohms-cm2
                sec.Ra = 100  # intracellular resistance
                sec.v = -60
                sec.e_pas = (
                    sec.v + (sec.ina + sec.ik) / sec.g_pas
                )  # calculate leak equilibrium potential
            elif self.model == "Tigerholm":
                sec.insert("ks")
                sec.gbar_ks = 0.0069733
                sec.insert("kf")
                sec.gbar_kf = 0.012756
                sec.insert("h")
                sec.gbar_h = 0.0025377
                sec.insert("nattxs")
                sec.gbar_nattxs = 0.10664
                sec.insert("nav1p8")
                sec.gbar_nav1p8 = 0.24271
                sec.insert("nav1p9")
                sec.gbar_nav1p9 = 9.4779e-05
                sec.insert("nakpump")
                sec.smalla_nakpump = -0.0047891
                sec.insert("kdrTiger")
                sec.gbar_kdrTiger = 0.018002
                sec.insert("kna")
                sec.gbar_kna = 0.00042
                sec.insert("naoi")

                sec.insert("koi")
                sec.theta_naoi = 0.029
                sec.theta_koi = 0.029

                sec.insert("leak")
                sec.insert("extrapump")

                sec.Ra = 35.5
                sec.cm = 1.0

                sec.celsiusT_ks = self.T
                sec.celsiusT_kf = self.T
                sec.celsiusT_h = self.T
                sec.celsiusT_nattxs = self.T
                sec.celsiusT_nav1p8 = self.T
                sec.celsiusT_nav1p9 = self.T
                sec.celsiusT_nakpump = self.T
                sec.celsiusT_kdrTiger = self.T
                sec.v = -55
            else:  # Schild 94 or 97 models
                R = 8314
                F = 96500
                sec.insert(
                    "leakSchild"
                )  # All mechanisms from Schild 1994 inserted into model
                sec.insert("kd")
                sec.insert("ka")
                sec.insert("can")
                sec.insert("cat")
                sec.insert("kds")
                sec.insert("kca")
                sec.insert("caextscale")
                sec.insert("caintscale")
                sec.insert("CaPump")
                sec.insert("NaCaPump")
                sec.insert("NaKpumpSchild")
                if self.model == "Schild_94":
                    sec.insert("naf")
                    sec.insert("nas")
                else:
                    sec.insert("naf97mean")
                    sec.insert("nas97mean")
                # Ionic concentrations
                # cao0_ca_ion = 2.0                                      # not in section, adapter considering: https://neuronsimulator.github.io/nrn/rxd-tutorials/initialization.html
                neuron.h.cao0_ca_ion = 2.0  # [mM] Initial Cao Concentration
                # cai0_ca_ion = 0.000117                                 # same as cao_ca_ion
                neuron.h.cai0_ca_ion = 0.000117  # [mM] Initial Cai Concentrations
                ko = 5.4  # [mM] External K Concentration
                ki = 145.0  # [mM] Internal K Concentration
                kstyle = neuron.h.ion_style(
                    "k_ion", 1, 2, 0, 0, 0
                )  # Allows ek to be calculated manually
                sec.ek = ((R * (self.T + 273.15)) / F) * math.log(
                    ko / ki
                )  # Manual Calculation of ek in order to use Schild F and R values
                nao = 154.0  # [mM] External Na Concentration
                nai = 8.9  # [mM] Internal Na Concentration
                nastyle = neuron.h.ion_style(
                    "na_ion", 1, 2, 0, 0, 0
                )  # Allows ena to be calculated manually
                sec.ena = ((R * (self.T + 273.15)) / F) * math.log(
                    nao / nai
                )  # Manual Calculation of ena in order to use Schild F and R values
                if self.model == "Schild_97":
                    sec.gbar_naf97mean = 0.022434928  # [S/cm^2] This block sets the conductance to the conductances in Schild 1997
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
                sec.L_caintscale = self.L / self.Nsec
                sec.L_caextscale = self.L / self.Nsec

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
        portion_length = 1.0 / self.Nsec
        stim_sec = int(math.floor(position / portion_length))
        stim_pos = (position / portion_length) - math.floor(position / portion_length)
        # add the stimulation to the axon
        self.intra_current_stim.append(
            neuron.h.IClamp(stim_pos, sec=self.unmyelinated_sections[stim_sec])
        )
        # modify the stimulation parameters
        self.intra_current_stim[-1].delay = t_start
        self.intra_current_stim[-1].dur = duration
        self.intra_current_stim[-1].amp = amplitude
        # save the stimulation parameter for results
        self.intra_current_stim_positions.append(position * self.L)
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
        portion_length = 1.0 / self.Nsec
        stim_sec = int(math.floor(position / portion_length))
        stim_pos = (position / portion_length) - math.floor(position / portion_length)
        # add the stimulation to the axon
        self.intra_voltage_stim = neuron.h.VClamp(
            stim_pos, sec=self.unmyelinated_sections[stim_sec]
        )
        # save the stimulation parameter for results
        self.intra_current_stim_position = position * self.L
        # save the stimulus for later use
        self.intra_voltage_stim_stimulus = stimulus
        # set fake duration
        self.intra_voltage_stim.dur[0] = 1e9

    ##############################
    ## Result recording methods ##
    ##############################
    def __set_recorders_with_key(self, *args):
        """
        To automate the methods set_recorder. For internal use only.
        Parameters
        ----------
        *args    : list(tuple)
            list of tuple containing a rec list to set and the corresonding key to access
            NB: keys should be str such as "_ref_xxx_yyy" where xxx is the variable to access
            and yyy the .mod file suffix if the variable is in one
        """
        for k in range(self.Nsec):
            for pos in self.rec_position_list[k]:
                for t in args:
                    key = t[1]
                    # print(dir(self.unmyelinated_sections[k](pos)))
                    # print(key, getattr(self.unmyelinated_sections[k](pos),key))
                    rec = neuron.h.Vector().record(
                        getattr(self.unmyelinated_sections[k](pos), key),
                        sec=self.unmyelinated_sections[k],
                    )
                    t[0].append(rec)

    def __get_var_from_mod(self, key):
        """
        return a column with value in every recording point of a constant from a mod. For internal use only.
        """
        val = np.zeros((len(self.x_rec)))
        i = 0
        for k in range(self.Nsec):
            for pos in self.rec_position_list[k]:
                # print(getattr(self.unmyelinated_sections[k](pos), key)[0])
                val[i] = getattr(self.unmyelinated_sections[k](pos), key)[0]
                i += 1
        return val

    def __get_recorders_from_list(self, reclist):
        """
        Convert reclist in np.array To automate methods set_recorder. For internal use only.
        Parameters
        ----------
        reclist     : neuron.h.List
            List in witch the reccorders are saved

        Returns
        -------
        val         : np.array
            array of every recorded value for all rec point and time
        """
        dim = (self.Nrec, self.t_len)
        val = np.zeros(dim)
        for k in range(dim[0]):
            val[k, :] = np.asarray(reclist[k])
        return val

    def set_membrane_voltage_recorders(self):
        """
        setup the membrane voltage recording. For internal use only.
        """
        self.vreclist = neuron.h.List()
        self.__set_recorders_with_key((self.vreclist, "_ref_v"))

    def get_membrane_voltage(self):
        """
        get the membrane voltage at the end of simulation. For internal use only.
        """
        return self.__get_recorders_from_list(self.vreclist)

    def set_membrane_current_recorders(self):
        """
        setup the membrane current recording. For internal use only.
        """
        self.ireclist = neuron.h.List()
        self.__set_recorders_with_key((self.ireclist, "_ref_i_membrane"))

    def get_membrane_current(self):
        """
        get the membrane current at the end of simulation. For internal use only.
        """
        return self.__get_recorders_from_list(self.ireclist)

    def set_ionic_current_recorders(self):
        """
        setup the ionic currents recording. For internal use only.
        """
        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            self.i_na_reclist = neuron.h.List()
            self.i_k_reclist = neuron.h.List()
            self.i_l_reclist = neuron.h.List()
            self.__set_recorders_with_key(
                (self.i_na_reclist, "_ref_ina"),
                (self.i_k_reclist, "_ref_ik"),
                (self.i_l_reclist, "_ref_i_pas"),
            )
        else:
            self.i_na_reclist = neuron.h.List()
            self.i_k_reclist = neuron.h.List()
            self.i_ca_reclist = neuron.h.List()
            self.__set_recorders_with_key(
                (self.i_na_reclist, "_ref_ina"),
                (self.i_k_reclist, "_ref_ik"),
                (self.i_ca_reclist, "_ref_cai"),
            )

    def get_ionic_current(self):
        """
        get the ionic currents at the end of simulation. For internal use only.
        """
        results = []
        results += [self.__get_recorders_from_list(self.i_na_reclist)]
        results += [self.__get_recorders_from_list(self.i_k_reclist)]
        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            results += [self.__get_recorders_from_list(self.i_l_reclist)]
        else:
            results += [self.__get_recorders_from_list(self.i_ca_reclist)]
        return results

    def set_conductance_recorders(self):
        """
        setup the membrane conductance recording. For internal use only.
        """
        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            self.g_na_reclist = neuron.h.List()
            self.g_k_reclist = neuron.h.List()
            self.g_l_reclist = neuron.h.List()
            if self.model == "HH":
                self.__set_recorders_with_key(
                    (self.g_na_reclist, "_ref_gna_hh"),
                    (self.g_k_reclist, "_ref_gk_hh"),
                    (self.g_l_reclist, "_ref_gl_hh"),
                )
            elif self.model == "Rattay_Aberham":
                self.__set_recorders_with_key(
                    (self.g_na_reclist, "_ref_gna_RattayAberham"),
                    (self.g_k_reclist, "_ref_gk_RattayAberham"),
                    (self.g_l_reclist, "_ref_gl_RattayAberham"),
                )
            else:
                self.__set_recorders_with_key(
                    (self.g_na_reclist, "_ref_gna_nahh"),
                    (self.g_k_reclist, "_ref_gkdr_borgkdr"),
                    (self.g_l_reclist, "_ref_g_pas"),
                )
        elif self.model == "Tigerholm":
            self.g_nav17_reclist = neuron.h.List()
            self.g_nav18_reclist = neuron.h.List()
            self.g_nav19_reclist = neuron.h.List()
            self.g_kA_reclist = neuron.h.List()
            self.g_kM_reclist = neuron.h.List()
            self.g_kdr_reclist = neuron.h.List()
            self.g_kna_reclist = neuron.h.List()
            self.g_h_reclist = neuron.h.List()
            self.g_naleak_reclist = neuron.h.List()
            self.g_kleak_reclist = neuron.h.List()
            self.__set_recorders_with_key(
                (self.g_nav17_reclist, "_ref_g_nattxs"),
                (self.g_nav18_reclist, "_ref_g_nav1p8"),
                (self.g_nav19_reclist, "_ref_g_nav1p9"),
                (self.g_kA_reclist, "_ref_g_ks"),
                (self.g_kM_reclist, "_ref_g_kf"),
                (self.g_kdr_reclist, "_ref_g_kdrTiger"),
                (self.g_kna_reclist, "_ref_g_kna"),
                (self.g_h_reclist, "_ref_g_h"),
                (self.g_naleak_reclist, "_ref_gnaleak_leak"),
                (self.g_kleak_reclist, "_ref_gkleak_leak"),
            )
        else:
            self.g_naf_reclist = neuron.h.List()
            self.g_nas_reclist = neuron.h.List()
            self.g_kd_reclist = neuron.h.List()
            self.g_ka_reclist = neuron.h.List()
            self.g_kds_reclist = neuron.h.List()
            self.g_kca_reclist = neuron.h.List()
            self.g_can_reclist = neuron.h.List()
            self.g_cat_reclist = neuron.h.List()
            sup_key = ""
            if self.model == "Schild_97":
                sup_key = "97mean"
            self.__set_recorders_with_key(
                (self.g_naf_reclist, "_ref_g_naf" + sup_key),
                (self.g_nas_reclist, "_ref_g_nas" + sup_key),
                (self.g_kd_reclist, "_ref_g_kd"),
                (self.g_ka_reclist, "_ref_g_ka"),
                (self.g_kds_reclist, "_ref_g_kds"),
                (self.g_kca_reclist, "_ref_g_kca"),
                (self.g_can_reclist, "_ref_g_can"),
                (self.g_cat_reclist, "_ref_g_cat"),
            )

    def get_membrane_conductance(self):
        """
        get the membrane voltage at the end of simulation. For internal use only.
        NB: [S/cm^{2}] (see Neuron unit)
        """
        return sum(self.get_ionic_conductance())

    def get_ionic_conductance(self):
        """
        get the membrane conductance at the end of simulation. For internal use only.
        NB: [S/cm^{2}] (see Neuron unit)
        """
        results = []
        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            results += [self.__get_recorders_from_list(self.g_na_reclist)]
            results += [self.__get_recorders_from_list(self.g_k_reclist)]
            results += [self.__get_recorders_from_list(self.g_l_reclist)]
        elif self.model == "Tigerholm":
            results += [self.__get_recorders_from_list(self.g_nav17_reclist)]
            results += [self.__get_recorders_from_list(self.g_nav18_reclist)]
            results += [self.__get_recorders_from_list(self.g_nav19_reclist)]
            results += [self.__get_recorders_from_list(self.g_kA_reclist)]
            results += [self.__get_recorders_from_list(self.g_kM_reclist)]
            results += [self.__get_recorders_from_list(self.g_kdr_reclist)]
            results += [self.__get_recorders_from_list(self.g_kna_reclist)]
            results += [self.__get_recorders_from_list(self.g_h_reclist)]
            results += [self.__get_recorders_from_list(self.g_naleak_reclist)]
            results += [self.__get_recorders_from_list(self.g_kleak_reclist)]
        else:
            results += [self.__get_recorders_from_list(self.g_naf_reclist)]
            results += [self.__get_recorders_from_list(self.g_nas_reclist)]
            results += [self.__get_recorders_from_list(self.g_kd_reclist)]
            results += [self.__get_recorders_from_list(self.g_ka_reclist)]
            results += [self.__get_recorders_from_list(self.g_kds_reclist)]
            results += [self.__get_recorders_from_list(self.g_kca_reclist)]
            results += [self.__get_recorders_from_list(self.g_can_reclist)]
            results += [self.__get_recorders_from_list(self.g_cat_reclist)]
        return results

    def get_membrane_capacitance(self):
        """
        get the membrane capacitance
        NB: [uF/cm^{2}] (see Neuron unit)
        """
        return self.__get_var_from_mod("_ref_cm")

    def set_particules_values_recorders(self):
        """
        setup the particule value recording. For internal use only.
        """

        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            self.hhmreclist = neuron.h.List()
            self.hhnreclist = neuron.h.List()
            self.hhhreclist = neuron.h.List()
            if self.model == "HH":
                self.__set_recorders_with_key(
                    (self.hhmreclist, "_ref_m_hh"),
                    (self.hhnreclist, "_ref_n_hh"),
                    (self.hhhreclist, "_ref_h_hh"),
                )
            elif self.model == "Rattay_Aberham":
                self.__set_recorders_with_key(
                    (self.hhmreclist, "_ref_m_RattayAberham"),
                    (self.hhnreclist, "_ref_n_RattayAberham"),
                    (self.hhhreclist, "_ref_h_RattayAberham"),
                )
            else:
                self.__set_recorders_with_key(
                    (self.hhmreclist, "_ref_m_nahh"),
                    (self.hhnreclist, "_ref_n_borgkdr"),
                    (self.hhhreclist, "_ref_h_nahh"),
                )
        elif self.model == "Tigerholm":
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

            self.__set_recorders_with_key(
                (self.m_nav18_reclist, "_ref_m_nav1p8"),
                (self.h_nav18_reclist, "_ref_h_nav1p8"),
                (self.s_nav18_reclist, "_ref_s_nav1p8"),
                (self.u_nav18_reclist, "_ref_u_nav1p8"),
                (self.m_nav19_reclist, "_ref_m_nav1p9"),
                (self.h_nav19_reclist, "_ref_h_nav1p9"),
                (self.s_nav19_reclist, "_ref_s_nav1p9"),
                (self.m_nattxs_reclist, "_ref_m_nattxs"),
                (self.h_nattxs_reclist, "_ref_h_nattxs"),
                (self.s_nattxs_reclist, "_ref_s_nattxs"),
                (self.n_kdr_reclist, "_ref_n_kdrTiger"),
                (self.m_kf_reclist, "_ref_m_kf"),
                (self.h_kf_reclist, "_ref_h_kf"),
                (self.ns_ks_reclist, "_ref_ns_ks"),
                (self.nf_ks_reclist, "_ref_nf_ks"),
                (self.w_kna_reclist, "_ref_w_kna"),
                (self.ns_h_reclist, "_ref_ns_h"),
                (self.nf_h_reclist, "_ref_nf_h"),
            )
        else:  # should be both Schild_94 or Schild_97
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
            self.__set_recorders_with_key(
                (self.d_can_reclist, "_ref_d_can"),
                (self.f1_can_reclist, "_ref_f1_can"),
                (self.f2_can_reclist, "_ref_f2_can"),
                (self.d_cat_reclist, "_ref_d_cat"),
                (self.f_cat_reclist, "_ref_f_cat"),
                (self.p_ka_reclist, "_ref_p_ka"),
                (self.q_ka_reclist, "_ref_q_ka"),
                (self.c_kca_reclist, "_ref_c_kca"),
                (self.n_kd_reclist, "_ref_n_kd"),
                (self.x_kds_reclist, "_ref_x_kds"),
                (self.y1_kds_reclist, "_ref_y1_kds"),
            )
            if self.model == "Schild_94":
                # Fast Na
                self.m_naf_reclist = neuron.h.List()
                self.h_naf_reclist = neuron.h.List()
                self.l_naf_reclist = neuron.h.List()
                # Slow Na
                self.m_nas_reclist = neuron.h.List()
                self.h_nas_reclist = neuron.h.List()
                self.__set_recorders_with_key(
                    (self.m_naf_reclist, "_ref_m_naf"),
                    (self.h_naf_reclist, "_ref_h_naf"),
                    (self.l_naf_reclist, "_ref_l_naf"),
                    (self.m_nas_reclist, "_ref_m_nas"),
                    (self.h_nas_reclist, "_ref_h_nas"),
                )
            else:  # should be Schild_94
                # Fast Na
                self.m_naf_reclist = neuron.h.List()
                self.h_naf_reclist = neuron.h.List()
                # Slow Na
                self.m_nas_reclist = neuron.h.List()
                self.h_nas_reclist = neuron.h.List()
                self.__set_recorders_with_key(
                    (self.m_naf_reclist, "_ref_m_naf97mean"),
                    (self.h_naf_reclist, "_ref_h_naf97mean"),
                    (self.m_nas_reclist, "_ref_m_nas97mean"),
                    (self.h_nas_reclist, "_ref_h_nas97mean"),
                )

    def get_particles_values(self):
        """
        get the particules values at the end of simulation. For internal use only.
        """
        results = []
        if self.model in ["HH", "Rattay_Aberham", "Sundt"]:
            results += [self.__get_recorders_from_list(self.hhmreclist)]
            results += [self.__get_recorders_from_list(self.hhnreclist)]
            results += [self.__get_recorders_from_list(self.hhhreclist)]
        elif self.model in ["Tigerholm"]:
            results += [self.__get_recorders_from_list(self.m_nav18_reclist)]
            results += [self.__get_recorders_from_list(self.h_nav18_reclist)]
            results += [self.__get_recorders_from_list(self.s_nav18_reclist)]
            results += [self.__get_recorders_from_list(self.u_nav18_reclist)]
            results += [self.__get_recorders_from_list(self.m_nav19_reclist)]
            results += [self.__get_recorders_from_list(self.h_nav19_reclist)]
            results += [self.__get_recorders_from_list(self.s_nav19_reclist)]
            results += [self.__get_recorders_from_list(self.m_nattxs_reclist)]
            results += [self.__get_recorders_from_list(self.h_nattxs_reclist)]
            results += [self.__get_recorders_from_list(self.s_nattxs_reclist)]
            results += [self.__get_recorders_from_list(self.n_kdr_reclist)]
            results += [self.__get_recorders_from_list(self.m_kf_reclist)]
            results += [self.__get_recorders_from_list(self.h_kf_reclist)]
            results += [self.__get_recorders_from_list(self.ns_ks_reclist)]
            results += [self.__get_recorders_from_list(self.nf_ks_reclist)]
            results += [self.__get_recorders_from_list(self.w_kna_reclist)]
            results += [self.__get_recorders_from_list(self.ns_h_reclist)]
            results += [self.__get_recorders_from_list(self.nf_h_reclist)]

        else:  # should be "Schild_94" or "Schild_97"
            results += [self.__get_recorders_from_list(self.d_can_reclist)]
            results += [self.__get_recorders_from_list(self.f1_can_reclist)]
            results += [self.__get_recorders_from_list(self.f2_can_reclist)]
            results += [self.__get_recorders_from_list(self.d_cat_reclist)]
            results += [self.__get_recorders_from_list(self.f_cat_reclist)]
            results += [self.__get_recorders_from_list(self.p_ka_reclist)]
            results += [self.__get_recorders_from_list(self.q_ka_reclist)]
            results += [self.__get_recorders_from_list(self.c_kca_reclist)]
            results += [self.__get_recorders_from_list(self.n_kd_reclist)]
            results += [self.__get_recorders_from_list(self.x_kds_reclist)]
            results += [self.__get_recorders_from_list(self.y1_kds_reclist)]
            results += [self.__get_recorders_from_list(self.m_naf_reclist)]
            results += [self.__get_recorders_from_list(self.h_naf_reclist)]
            results += [self.__get_recorders_from_list(self.m_nas_reclist)]
            results += [self.__get_recorders_from_list(self.h_nas_reclist)]
            if self.model == "Schild_94":
                results += [self.__get_recorders_from_list(self.l_naf_reclist)]
        return results

    # Simulate method, for output type
    def simulate(self, **kwargs) -> unmyelinated_results:
        return super().simulate(**kwargs)
