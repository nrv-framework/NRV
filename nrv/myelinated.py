"""
NRV-myelinated
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import math
import numpy as np
from .axons import *
from .log_interface import rise_error, rise_warning, pass_info

MRG_fiberD = np.asarray([1, 2, 5.7, 7.3, 8.7, 10.0, 11.5, 12.8, 14.0, 15.0, 16.0])
MRG_g = np.asarray([0.565, 0.585, 0.605, 0.630, 0.661, 0.690, 0.700, 0.719, 0.739, 0.767, 0.791])
MRG_axonD = np.asarray([0.8, 1.6, 3.4, 4.6, 5.8, 6.9, 8.1, 9.2, 10.4, 11.5, 12.7])
MRG_nodeD = np.asarray([0.7, 1.4, 1.9, 2.4, 2.8, 3.3, 3.7, 4.2, 4.7, 5.0, 5.5])
MRG_paraD1 = np.asarray([0.7, 1.4, 1.9, 2.4, 2.8, 3.3, 3.7, 4.2, 4.7, 5.0, 5.5])
MRG_paraD2 = np.asarray([0.8, 1.6, 3.4, 4.6, 5.8, 6.9, 8.1, 9.2, 10.4, 11.5, 12.7])
MRG_deltax = np.asarray([100, 200, 500, 750, 1000, 1150, 1250, 1350, 1400, 1450, 1500])
MRG_paralength2 = np.asarray([5, 10, 35, 38, 40, 46, 50, 54, 56, 58, 60])
MRG_nl = np.asarray([15, 20, 80, 100, 110, 120, 130, 135, 140, 145, 150])

def get_MRG_parameters(diameter):
    """
    Compute the MRG parameters

    Original parameters are listed and used if the input diameter is in the list,
    parameters are interpolated if the diameter is not in the original list.

    Attributes
    ----------
    diameter    : float
        diameter of the unmylinated axon to implement, in um

    Returns
    -------
    g           : float
    axonD       : float
    nodeD       : float
    paraD1      : float
    paraD2      : float
    deltax      : float
    paralength2 : float
    nl          : float
    """

    if diameter in MRG_fiberD:
        index = np.where(MRG_fiberD == diameter)[0]
        g = MRG_g[index]
        axonD = MRG_axonD[index]
        nodeD = MRG_nodeD[index]
        paraD1 = MRG_paraD1[index]
        paraD2 = MRG_paraD2[index]
        deltax = MRG_deltax[index]
        paralength2 = MRG_paralength2[index]
        nl = MRG_nl[index]
    else:
        # create fiting polynomyals
        g_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_g, 3))
        axonD_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_axonD, 3))
        nodeD_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_nodeD, 3))
        paraD1_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paraD1, 3))
        paraD2_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paraD2, 3))
        deltax_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_deltax, 4))
        if diameter < 1. or diameter > 16.0:
            # outside of the MRG originla limit, take 1st order approx,
            paralength2_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paralength2, 1))
        else:
            # try to fit a bit better
            paralength2_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_paralength2, 5))
        nl_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_nl, 3))
        # evaluate for the requested diameter
        g = g_poly(diameter)
        axonD = axonD_poly(diameter)
        nodeD = nodeD_poly(diameter)
        paraD1 = paraD1_poly(diameter)
        paraD2 = paraD2_poly(diameter)
        deltax = deltax_poly(diameter)
        paralength2 = paralength2_poly(diameter)
        nl = nl_poly(diameter)
    return float(g), float(axonD), float(nodeD), float(paraD1), float(paraD2), float(deltax), \
        float(paralength2), float(nl)

def get_length_from_nodes(diameter, nodes):
    """
    Function to compute the length of a myelinated axon to get the correct number of Nodes of Ranvier
    For Myelinated models only (not compatible with A delta thin myelinated models)

    Attributes
    ----------
    diameter    : float
        diameter of the axon in um
    nodes       : int
        number of nodes in the axon

    Returns
    -------
    length      : float
        lenth of the axon with the correct number of nodes in um
    """
    if diameter in MRG_fiberD:
        index = np.where(MRG_fiberD == diameter)[0]
        deltax = MRG_deltax[index]
    else:
        deltax_poly = np.poly1d(np.polyfit(MRG_fiberD, MRG_deltax, 4))
        deltax = deltax_poly(diameter)
    return float(math.ceil(deltax*(nodes-1)))

class myelinated(axon):
    """
    Myelineated axon class. Automatic refinition of all neuron sections and properties. User-friendly object including model definition
    Inherit from axon class. see axon for further detail.
    """
    def __init__(self, y, z, d, L, model='MRG', dt=0.001, node_shift=0, Nseg_per_sec=0, freq=100,\
        freq_min=0, mesh_shape='plateau_sigmoid', alpha_max=0.3, d_lambda=0.1, rec='nodes',\
        v_init=None, T=None, ID=0, threshold=-40):
        """
        initialisation of a myelinted axon

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
            choice of conductance double-cable based model, possibly:
                'MRG'           : see [1] for details
                'Gaines_motor'  : Gaines motor model, see [2]
                'Gaines_sensory': Gaines sensory model, see [2]
        dt              : float
            computation step for simulations, in ms. By default equal to 1 us
        node_shift      : float
            shift of the first node of Ranvier to zeros, as a fraction of internode length (0<= node_shift < 1)
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
            value of d-lambda for the dlambda rule
        rec             : str
            recording zones for the membrane potential, eiter:
                'nodes' -> record only at the nodes of Ranvier
            or
                'all' -> all computation points in nodes of Ranvier and over myelin
        v_init          : float
            Initial value of the membrane voltage in mV, set None to get an automatically model attributed value
        T               : gloat
            temperature in C, set None to get an automatically model attributed value
        ID              : int
            axon ID, by default set to 0,
        threshold       : float
            voltage threshold in mV for further spike detection in post-processing, by defautl set to -40mV, see post-processing library for further help

        Note
        ----
        scientific sources for models:
        [1] McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle. Journal of Neurophysiology 87:995-1006, 2002.
        [2] Gaines, J. L., Finn, K. E., Slopsema, J. P., Heyboer, L. A.,  Polasek, K. H. (2018). A model of motor and sensory axon activation in the median nerve using surface electrical stimulation. Journal of computational neuroscience, 45(1), 29-43.
        """
        super().__init__(y, z, d, L, dt=dt, Nseg_per_sec=Nseg_per_sec,\
            freq=freq, freq_min=freq_min, mesh_shape=mesh_shape, alpha_max=alpha_max, \
            d_lambda=d_lambda, v_init=v_init, T=T, ID=ID, threshold=threshold)
        self.myelinated = True
        self.thin = False
        self.rec = rec
        if model in myelinated_models:
            self.model = model
        else:
            self.model = 'MRG'
        ## Handling v_init
        if v_init is None:
            # model driven
            if self.model == 'Gaines_sensory':
                self.v_init = -79.3565
            elif self.model == 'Gaines_motor':
                self.v_init = -85.9411
            else:
                self.v_init = -80
        else:
            # user driven
            self.v_init = v_init
        ## Handling temperature
        if T is None:
            # model driven
            self.T = 37
        else:
            # user driven
            self.T = T
        ############################################
        ## PARMETERS FOR THE COMPARTIMENTAL MODEL ##
        ############################################
        # compute variable MRG parameters, (usefull also if non MRG models)
        self.g, self.axonD, self.nodeD, self.paraD1, self.paraD2, self.deltax, self.paralength2,\
            self.nl = get_MRG_parameters(self.d)
        # Morphological parameters
        self.paralength1 = 3
        self.nodelength = 1.0
        self.space_p1 = 0.002
        self.space_p2 = 0.004
        self.space_i = 0.004
        self.interlength = (self.deltax-self.nodelength-(2*self.paralength1)-(2*self.paralength2))/6
        # electrical parameters
        self.rhoa = 0.7e6   # Ohm-um
        self.mycm = 0.1     # uF/cm2/lamella membrane
        self.mygm = 0.001   # S/cm2/lamella membrane
        self.Rpn0 = (self.rhoa*.01)/(math.pi*((((self.nodeD/2)+self.space_p1)**2)-\
            ((self.nodeD/2)**2)))
        self.Rpn1 = (self.rhoa*.01)/(math.pi*((((self.paraD1/2)+self.space_p1)**2)-\
            ((self.paraD1/2)**2)))
        self.Rpn2 = (self.rhoa*.01)/(math.pi*((((self.paraD2/2)+self.space_p2)**2)-\
            ((self.paraD2/2)**2)))
        self.Rpx = (self.rhoa*.01)/(math.pi*((((self.axonD/2)+self.space_i)**2)-\
            ((self.axonD/2)**2)))
        #########################
        ## morphology planning ##
        #########################
        # basic MRG sequence
        self.MRG_Sequence = ['node', 'MYSA', 'FLUT', 'STIN', 'STIN', 'STIN', 'STIN', 'STIN',\
            'STIN', 'FLUT', 'MYSA']
        # basic MRG starts with the node, if needed, adapt the sequence
        self.node_shift = node_shift

        if self.node_shift == 0 or self.node_shift == 1:
            # no Rotation
            self.this_ax_sequence = self.MRG_Sequence
            self.first_section_size = self.nodelength

        elif self.node_shift < (self.paralength1)/self.deltax:
            # rotation of less than 1 MYSA
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 1)
            self.first_section_size = (self.node_shift*self.deltax)

        elif self.node_shift < (self.paralength1 + self.paralength2)/self.deltax:
            # rotation of 1 MYSA and less than one FLUT
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 2)
            self.first_section_size = (self.node_shift*self.deltax - \
                self.paralength1)

        elif self.node_shift < (self.paralength1 + self.paralength2 + \
            self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 3)
            self.first_section_size = (self.node_shift*self.deltax -\
                self.paralength1 - self.paralength2)

        elif self.node_shift < (self.paralength1 + self.paralength2 +\
            2*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 1 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 4)
            self.first_section_size = (self.node_shift*self.deltax -\
                self.paralength1 - self.paralength2 - self.interlength)

        elif self.node_shift < (self.paralength1 + self.paralength2 + \
            3*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 2 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 5)
            self.first_section_size = (self.node_shift*self.deltax -\
                self.paralength1 - self.paralength2 - 2*self.interlength)

        elif self.node_shift < (self.paralength1 + self.paralength2 +\
            4*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 3 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 6)
            self.first_section_size = (self.node_shift*self.deltax -\
                self.paralength1 - self.paralength2 - 3*self.interlength)

        elif self.node_shift < (self.paralength1 + self.paralength2 + \
            5*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 4 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 7)
            self.first_section_size = (self.node_shift*self.deltax - \
                self.paralength1 - self.paralength2 - 4*self.interlength)

        elif self.node_shift < (self.paralength1 + self.paralength2 + \
            6*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 5 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 8)
            self.first_section_size = (self.node_shift*self.deltax -\
                self.paralength1 - self.paralength2 - 5*self.interlength)

        elif self.node_shift < (self.paralength1 + 2*self.paralength2 + \
            6*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 FLUT, 6 STIN and less than a FLUT
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 9)
            self.first_section_size =(self.node_shift*self.deltax - \
                self.paralength1 - self.paralength2 - 6*self.interlength)

        elif self.node_shift < (self.paralength1 + self.paralength2 + \
            6*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 2 FLUT, 6 STIN and less than a MYSA
            # WARNING FOR DEV : the unprobable case of a node cut in two halfs is not considered...
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 10)
            self.first_section_size = self.deltax*(1-self.node_shift)
        ################
        ## morphology ##
        ################
        self.axonnodes = 0      # number of nodes in the axon
        self.node = []          # list of nodes in the axon
        self.paranodes1 = 0     # number of MYSA in the axon
        self.MYSA = []          # list of MYSA in the axon
        self.paranodes2 = 0     # number of FLUT in the axon
        self.FLUT = []          # list of FLUT in the axon
        self.axoninter = 0      # number of STIN in the axon
        self.STIN = []          # list of STIN in the axon

        prov_length = 0
        self.Nsec = 0
        self.last_section_size = 0
        self.last_section_kind = None
        self.axon_path_type = []
        self.axon_path_index = []
        while prov_length < self.L:
            # axon is too short, create a section
            pos_in_sequence = (self.Nsec)%len(self.this_ax_sequence)    # find the current position in the node sequence
            if self.this_ax_sequence[pos_in_sequence] == 'node':
                # you need to create a node
                self.node.append(neuron.h.Section(name='node[%d]' % self.axonnodes))
                self.axon_path_type.append('node')
                self.axon_path_index.append(self.axonnodes)
                self.axonnodes += 1
                self.Nsec += 1
                # increment the prov length and check it is not to much
                if prov_length + self.nodelength >= self.L:
                    # it will be the last section to add to the axon
                    self.last_section_kind = 'node'
                    self.last_section_size = self.L - prov_length
                prov_length += self.nodelength
                # CONNECT THE NODE TO ITS PARENT: a node can only have a MYSA for parent, check it's not the start...
                if self.paranodes1 != 0:
                    self.node[-1].connect(self.MYSA[-1], 1, 0)

            elif self.this_ax_sequence[pos_in_sequence] == 'MYSA':
                # you need to create a MYSA
                self.MYSA.append(neuron.h.Section(name='MYSA[%d]' % self.paranodes1))
                self.axon_path_type.append('MYSA')
                self.axon_path_index.append(self.paranodes1)
                self.paranodes1 += 1
                self.Nsec += 1
                # increment the prov length and check it is not to much
                if prov_length + self.paralength1 >= self.L:
                    # it will be the last section to add to the axon
                    self.last_section_kind = 'MYSA'
                    self.last_section_size = self.L - prov_length
                prov_length += self.paralength1
                # CONNECT THE MYSA TO ITS PARENT: a MYSA can have for parent a node or a FLUT, check it's not the start...
                connect_to_type = self.this_ax_sequence[pos_in_sequence - 1] # get parent type
                if connect_to_type == 'node' and self.axonnodes != 0:
                    self.MYSA[-1].connect(self.node[-1], 1, 0)
                if connect_to_type == 'FLUT' and self.paranodes2 != 0:
                    self.MYSA[-1].connect(self.FLUT[-1], 1, 0)

            elif self.this_ax_sequence[pos_in_sequence] == 'FLUT':
                # you need to create a FLUT
                self.FLUT.append(neuron.h.Section(name='FLUT[%d]' % self.paranodes2))
                self.axon_path_type.append('FLUT')
                self.axon_path_index.append(self.paranodes2)
                self.paranodes2 += 1
                self.Nsec += 1
                # increment the prov length and check it is not to much
                if prov_length + self.paralength2 >= self.L:
                    # it will be the last section to add to the axon
                    self.last_section_kind = 'FLUT'
                    self.last_section_size = self.L - prov_length
                prov_length += self.paralength2
                # CONNECT THE FLUT TO ITS PARENT: a FLUT can have for parent a MYSA of a STIN, check it's not the start...
                connect_to_type = self.this_ax_sequence[pos_in_sequence - 1] # get parent type
                if connect_to_type == 'MYSA' and self.paranodes1 != 0:
                    self.FLUT[-1].connect(self.MYSA[-1], 1, 0)
                if connect_to_type == 'STIN' and self.axoninter != 0:
                    self.FLUT[-1].connect(self.STIN[-1], 1, 0)

            else:
                # you need to create a STIN
                self.STIN.append(neuron.h.Section(name='STIN[%d]' % self.axoninter))
                self.axon_path_type.append('STIN')
                self.axon_path_index.append(self.axoninter)
                self.axoninter += 1
                self.Nsec += 1
                # increment the prov length and check it is not to much
                if prov_length + self.interlength >= self.L:
                    # it will be the last section to add to the axon
                    self.last_section_kind = 'STIN'
                    self.last_section_size = self.L - prov_length
                prov_length += self.interlength
                # CONNECT THE STIN TO ITS PARENT: a STIN can have for parent a STIN od a FLUT, check it's not the start...
                connect_to_type = self.this_ax_sequence[pos_in_sequence - 1]
                if connect_to_type == 'STIN' and self.axoninter > 1:
                    self.STIN[-1].connect(self.STIN[-2], 1, 0)
                if connect_to_type == 'FLUT' and self.paranodes2 != 0:
                    self.STIN[-1].connect(self.FLUT[-1], 1, 0)

        if self.node == []:
            rise_warning('Warning, myelinated axon without node... this can cause latter errors and is maybe unwanted ?\n')
            #logging.warning('Warning, myelinated axon without node... this can cause latter errors and is maybe unwanted ?\n')

        ####################
        ## programm model ##
        ####################
        self.__set_model(self.model)
        # adjust the length of the first section
        if self.this_ax_sequence[0] == 'node':
            self.node[0].L = self.first_section_size
        elif self.this_ax_sequence[0] == 'MYSA':
            self.MYSA[0].L = self.first_section_size
        elif self.this_ax_sequence[0] == 'FLUT':
            self.FLUT[0].L = self.first_section_size
        else: # should be a STIN
            self.STIN[0].L = self.first_section_size
        # adjust the length if the last section
        if self.last_section_kind == 'node':
            self.node[-1].L = self.last_section_size
        elif self.last_section_kind == 'MYSA':
            self.MYSA[-1].L = self.last_section_size
        elif self.last_section_kind == 'FLUT':
            self.FLUT[-1].L = self.last_section_size
        else: # should be a STIN
            self.STIN[-1].L = self.last_section_size
        # define the geometry of the axon
        self._axon__define_shape()
        # define the number of segments
        self.__set_Nseg()
        # get nodes positions
        self.__get_seg_positions()
        self.__get_rec_positions()

    def __set_model(self, model):
        """
        Set the double cable model. For internal use only.

        Parameters
        ----------
        model           : str
            choice of conductance double-cable based model, possibly:
                'MRG'           : see [1] for details
                'Gaines_motor'  : Gaines motor model, see [2]
                'Gaines_sensory': Gaines sensory model, see [2]

        Note
        ----
        scientific sources for models:
        [1] McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle. Journal of Neurophysiology 87:995-1006, 2002.
        [2] Gaines, J. L., Finn, K. E., Slopsema, J. P., Heyboer, L. A.,  Polasek, K. H. (2018). A model of motor and sensory axon activation in the median nerve using surface electrical stimulation. Journal of computational neuroscience, 45(1), 29-43.
        """
        for n in self.node:
            n.nseg = 1
            n.diam = self.nodeD
            n.L = self.nodelength
            n.Ra = self.rhoa/10000
            n.cm = 2
            if model == 'Gaines_sensory':
                n.insert('node_sensory')
            elif model == 'Gaines_motor':
                n.insert('node_motor')
            else:
                n.insert('axnode')
            n.insert('extracellular')
            n.xraxial[0] = self.Rpn0
            n.xg[0] = 1e10
            n.xc[0] = 0
        for m in self.MYSA:
            m.nseg = 1
            m.diam = self.d
            m.L = self.paralength1
            m.Ra = self.rhoa*(1/(self.paraD1/self.d)**2)/10000
            m.cm = 2*self.paraD1/self.d
            if model == 'Gaines_sensory':
                m.insert('mysa_sensory')
            elif model == 'Gaines_motor':
                m.insert('mysa_motor')
            else:
                m.insert('pas')
                m.g_pas = 0.001*self.paraD1/self.d
                m.e_pas = -80
            m.insert('extracellular')
            m.xraxial[0] = self.Rpn1
            m.xg[0] = self.mygm/(self.nl*2)
            m.xc[0] = self.mycm/(self.nl*2)
        for f in self.FLUT:
            f.nseg = 1
            f.diam = self.d
            f.L = self.paralength2
            f.Ra = self.rhoa*(1/(self.paraD2/self.d)**2)/10000
            f.cm = 2*self.paraD2/self.d
            if model == 'Gaines_sensory':
                f.insert('flut_sensory')
            elif model == 'Gaines_motor':
                f.insert('flut_motor')
            else:
                f.insert('pas')
                f.g_pas = 0.0001*self.paraD2/self.d
                f.e_pas = -80
            f.insert('extracellular')
            f.xraxial[0] = self.Rpn2
            f.xg[0] = self.mygm/(self.nl*2)
            f.xc[0] = self.mycm/(self.nl*2)
        for s in self.STIN:
            s.nseg = 1
            s.diam = self.d
            s.L = self.interlength
            s.Ra = self.rhoa*(1/(self.axonD/self.d)**2)/10000
            s.cm = 2*self.axonD/self.d
            if model == 'Gaines_sensory':
                s.insert('stin_sensory')
            elif model == 'Gaines_motor':
                s.insert('stin_motor')
            else:
                s.insert('pas')
                s.g_pas = 0.0001*self.axonD/self.d
                s.e_pas = -80
            s.insert('extracellular')
            s.xraxial[0] = self.Rpx
            s.xg[0] = self.mygm/(self.nl*2)
            s.xc[0] = self.mycm/(self.nl*2)

    def set_Markov_Nav(self, list_of_nodes=[]):
        """
        Change typical particle-Na sodium in Hodgking-Huxley formalism to Markov-channel population model.

        Parameters
        ----------
        list_of_nodes   : list, array, np.array
            list of Nodes of Ranier to modify, if empty, all nodes sodium channels are changed

        Note
        ----
        based on:
        Yi, G., and Grill, W. M. (2020). Kilohertz waveforms optimized to produce closed-state Na+ channel inactivation eliminate onset response in nerve conduction block. PLoS computational biology, 16(6), e1007766.

        !!! TO USE WITH CAUTION !!!
        """
        if list_of_nodes == []:
            list_of_nodes = np.arange(self.axonnodes)
        if self.model == 'MRG':
            for NoR in list_of_nodes:
                self.node[NoR].gnapbar_axnode = 0
                self.node[NoR].gnabar_axnode = 0
        elif self.model == 'Gaines_motor':
            for NoR in list_of_nodes:
                self.node[NoR].gnapbar_node_motor = 0
                self.node[NoR].gnabar_node_motor = 0
        elif self.model == 'Gaines_sensory':
            for NoR in list_of_nodes:
                self.node[NoR].gnapbar_node_sensory = 0
                self.node[NoR].gnabar_node_sensory = 0
        # insert channel specific mechanisms
        # Nav1.1 models fast sodium
        # Nav1.6 models persistant sodium, to be confirmed, Warning gnabar is different than MRG and Gaines
        for NoR in list_of_nodes:
            # insert Nav1.1 model
            self.node[NoR].insert('na11a')
            self.node[NoR].gbar_na11a = 11.9
            # insert Nav1.6 model
            self.node[NoR].insert('na16a')
            self.node[NoR].gbar_na16a = 0.01
            ## WARINING -  Sodium Nernst potential is defined for axnode as ena_axnode, and is common
            ## for fast and persistant sodium channels (see lines 98 and 99 in AXNOE.mod)
            ## This is not the case for Nav1.x, which uses the NEURON instruction USEION na READ ena
            ## meaning the following line is tuning directly the na11a and na16a mechanisms
            self.node[NoR].ena = 50
        self.Markov_Nav_modeled_NoR = list_of_nodes

    def __set_Nseg(self):
        """
        Set the number of segments automatically acording initialization. For internal use only.
        """

        if type(self.Nseg_per_sec) is dict:
            for n in self.node:
                n.nseg = self.Nseg_per_sec['node']
            for m in self.MYSA:
                m.nseg = self.Nseg_per_sec['MYSA']
            for f in self.FLUT:
                f.nseg = self.Nseg_per_sec['FLUT']
            for s in self.STIN:
                s.nseg = self.Nseg_per_sec['STIN']
            self.node_Nseg = self.axonnodes * self.Nseg_per_sec['node']
            self.MYSA_Nseg = self.paranodes1 * self.Nseg_per_sec['MYSA']
            self.FLUT_Nseg = self.paranodes2 * self.Nseg_per_sec['FLUT']
            self.STIN_Nseg = self.axoninter * self.Nseg_per_sec['STIN']

        elif self.Nseg_per_sec != 0:
            # all sections will have a fixed number of segment chosen by user
            for n in self.node:
                n.nseg = self.Nseg_per_sec
            for m in self.MYSA:
                m.nseg = self.Nseg_per_sec
            for f in self.FLUT:
                f.nseg = self.Nseg_per_sec
            for s in self.STIN:
                s.nseg = self.Nseg_per_sec
            self.node_Nseg = self.axonnodes * self.Nseg_per_sec
            self.MYSA_Nseg = self.paranodes1 * self.Nseg_per_sec
            self.FLUT_Nseg = self.paranodes2 * self.Nseg_per_sec
            self.STIN_Nseg = self.axoninter * self.Nseg_per_sec
        else:
            # here comes the dlambda rule
            self.node_Nseg = 0
            self.MYSA_Nseg = 0
            self.FLUT_Nseg = 0
            self.STIN_Nseg = 0
            if self.freq_min == 0:
                # uniform meshing
                for n in self.node:
                    Nseg = d_lambda_rule(n.L, self.d_lambda, self.freq, n)
                    n.nseg = Nseg
                    self.node_Nseg += Nseg
                for m in self.MYSA:
                    Nseg = Nseg = d_lambda_rule(m.L, self.d_lambda, self.freq, m)
                    m.nseg = Nseg
                    self.MYSA_Nseg += Nseg
                for f in self.FLUT:
                    Nseg = Nseg = d_lambda_rule(f.L, self.d_lambda, self.freq, f)
                    f.nseg = Nseg
                    self.FLUT_Nseg += Nseg
                for s in self.STIN:
                    Nseg = Nseg = d_lambda_rule(s.L, self.d_lambda, self.freq, s)
                    s.nseg = Nseg
                    self.STIN_Nseg += Nseg
            else:
                # non-uniform meshing
                freqs = create_Nseg_freq_shape(self.Nsec, self.mesh_shape, self.freq, \
                    self.freq_min, self.alpha_max)
                for k in range(len(self.axon_path_type)):
                    sec_type = self.axon_path_type[k]
                    sec_index = self.axon_path_index[k]
                    if sec_type == 'node':
                        Nseg = d_lambda_rule(self.node[sec_index].L, self.d_lambda, freqs[k], \
                            self.node[sec_index])
                        self.node[sec_index].nseg = Nseg
                        self.node_Nseg += Nseg
                    elif sec_type == 'MYSA':
                        Nseg = d_lambda_rule(self.MYSA[sec_index].L, self.d_lambda, freqs[k], \
                            self.MYSA[sec_index])
                        self.MYSA[sec_index].nseg = Nseg
                        self.MYSA_Nseg += Nseg
                    elif sec_type == 'FLUT':
                        Nseg = d_lambda_rule(self.FLUT[sec_index].L, self.d_lambda, freqs[k], \
                            self.FLUT[sec_index])
                        self.FLUT[sec_index].nseg = Nseg
                        self.FLUT_Nseg += Nseg
                    else: # should be STIN
                        Nseg = d_lambda_rule(self.STIN[sec_index].L, self.d_lambda, freqs[k], \
                            self.STIN[sec_index])
                        self.STIN[sec_index].nseg = Nseg
                        self.STIN_Nseg += Nseg
        self.Nseg = self.node_Nseg + self.MYSA_Nseg + self.FLUT_Nseg + self.STIN_Nseg

    def __get_seg_positions(self):
        """
        Get segment positions, for internal use only.
        """
        x_offset = 0
        x = []
        x_nodes = []
        nodes_index = []
        self.rec_position_list = []
        for k in range(len(self.axon_path_type)):
            sec_type = self.axon_path_type[k]
            sec_index = self.axon_path_index[k]
            self.rec_position_list.append([])
            if sec_type == 'node':
                x_nodes.append(x_offset + self.node[sec_index].L/2)
                for seg in self.node[sec_index].allseg():
                    if x == []:
                        x.append(seg.x*(self.node[sec_index].L) + x_offset)
                        nodes_index.append(0)
                        self.rec_position_list[-1].append(seg.x)
                    else:
                        x_seg = seg.x*(self.node[sec_index].L) + x_offset
                        if x_seg != x[-1]:
                            x.append(x_seg)
                            nodes_index.append(len(x)-1)
                            self.rec_position_list[-1].append(seg.x)
                x_offset += self.node[sec_index].L
            elif sec_type == 'MYSA':
                for seg in self.MYSA[sec_index].allseg():
                    if x == []:
                        x.append(seg.x*(self.MYSA[sec_index].L) + x_offset)
                        self.rec_position_list[-1].append(seg.x)
                    else:
                        x_seg = seg.x*(self.MYSA[sec_index].L) + x_offset
                        if x_seg != x[-1]:
                            x.append(x_seg)
                            self.rec_position_list[-1].append(seg.x)
                x_offset += self.MYSA[sec_index].L
            elif sec_type == 'FLUT':
                for seg in self.FLUT[sec_index].allseg():
                    if x == []:
                        x.append(seg.x*(self.FLUT[sec_index].L) + x_offset)
                        self.rec_position_list[-1].append(seg.x)
                    else:
                        x_seg = seg.x*(self.FLUT[sec_index].L) + x_offset
                        if x_seg != x[-1]:
                            x.append(x_seg)
                            self.rec_position_list[-1].append(seg.x)
                x_offset += self.FLUT[sec_index].L
            else: # should be STIN
                for seg in self.STIN[sec_index].allseg():
                    if x == []:
                        x.append(seg.x*(self.STIN[sec_index].L) + x_offset)
                        self.rec_position_list[-1].append(seg.x)
                    else:
                        x_seg = seg.x*(self.STIN[sec_index].L) + x_offset
                        if x_seg != x[-1]:
                            x.append(x_seg)
                            self.rec_position_list[-1].append(seg.x)
                x_offset += self.STIN[sec_index].L
        self.x = np.asarray(x)
        self.x_nodes = np.asarray(x_nodes)
        self.node_index = np.asarray(nodes_index)

    def __get_rec_positions(self):
        """
        Get the position of points with voltage recording. For internal use only.
        """
        if self.rec == 'nodes':
            self.x_rec = self.x_nodes
        else:
            self.x_rec = self.x

    ###############################
    ## Intracellular stimulation ##
    ###############################
    def insert_I_Clamp_node(self, index, t_start, duration, amplitude):
        """
        Insert a IC clamp stimulation on a Ranvier node at its midd point position

        Parameters
        ----------
        index       : int
            node number of the node to stimulate
        t_start     : float
            starting time (ms)
        duration    : float
            duration of the pulse(ms)
        amplitude   : float
            amplitude of the pulse (nA)
        """
        # add the stimulation to the axon
        self.intra_current_stim.append(neuron.h.IClamp(0.5, sec=self.node[index]))
        # modify the stimulation parameters
        self.intra_current_stim[-1].delay = t_start
        self.intra_current_stim[-1].dur = duration
        self.intra_current_stim[-1].amp = amplitude
        # save the stimulation parameter for results
        self.intra_current_stim_positions.append(self.x_nodes[index])
        self.intra_current_stim_starts.append(t_start)
        self.intra_current_stim_durations.append(duration)
        self.intra_current_stim_amplitudes.append(amplitude)

    def insert_I_Clamp(self, position, t_start, duration, amplitude):
        """
        Insert a IC clamp stimulation at the midd point of the nearest node to the specified position

        Parameters
        ----------
        position    : float
            relative position over the axon
        t_start     : float
            starting time (ms)
        duration    :
            duration of the pulse(ms)
        amplitude   :
            amplitude of the pulse (nA)
        """
        # adapt position to the number of sections
        index = round(position * (self.axonnodes - 1))
        self.insert_I_Clamp_node(index, t_start, duration, amplitude)

    def insert_V_Clamp_node(self, index, stimulus):
        """
        Insert a V clamp stimulation

        Parameters
        ----------
        index       : int
            node number of the node to stimulate
        stimulus    : stimulus object
            stimulus for the clamp, see Stimulus.py for more information
        """
        # add the stimulation to the axon
        self.intra_voltage_stim = neuron.h.VClamp(0.5, sec=self.node[index])
        # save the stimulation parameter for results
        self.intra_current_stim_position = self.x_nodes[index]
        # save the stimulus for later use
        self.intra_voltage_stim_stimulus = stimulus
        # set fake duration
        self.intra_voltage_stim.dur[0] = 1e9

    def insert_V_Clamp(self, position, stimulus):
        """
        Insert a V clamp stimulation at the midd point of the nearest node to the specified position

        Parameters
        ----------
        position    : float
            relative position over the axon
        stimulus    : stimulus object
            stimulus for the clamp, see Stimulus.py for more information
        """
        # adapt position to the number of sections
        index = round(position * (self.axonnodes - 1))
        self.insert_I_Clamp_node(index, stimulus)

    ##############################
    ## Result recording methods ##
    ##############################
    def set_membrane_voltage_recorders(self):
        """
        Prepare the membrane voltage recording. For internal use only.
        """
        self.vreclist = neuron.h.List()
        if self.rec == 'nodes':
            # recording only on middle of all nodes
            for n in self.node:
                vrec = neuron.h.Vector().record(n(0.5)._ref_v, sec=n)
                self.vreclist.append(vrec)
        else:
            # recording on all segments
            for k in range(len(self.axon_path_type)):
                sec_type = self.axon_path_type[k]
                sec_index = self.axon_path_index[k]
                for position in self.rec_position_list[k]:
                    if sec_type == 'node':
                        vrec = neuron.h.Vector().record(self.node[sec_index](position)._ref_v, \
                            sec=self.node[sec_index])
                        self.vreclist.append(vrec)
                    elif sec_type == 'MYSA':
                        vrec = neuron.h.Vector().record(self.MYSA[sec_index](position)._ref_v, \
                            sec=self.MYSA[sec_index])
                        self.vreclist.append(vrec)
                    elif sec_type == 'FLUT':
                        vrec = neuron.h.Vector().record(self.FLUT[sec_index](position)._ref_v, \
                            sec=self.FLUT[sec_index])
                        self.vreclist.append(vrec)
                    else: # should be STIN
                        vrec = neuron.h.Vector().record(self.STIN[sec_index](position)._ref_v, \
                            sec=self.STIN[sec_index])
                        self.vreclist.append(vrec)

    def get_membrane_voltage(self):
        """
        get the membrane voltage at the end of simulation. For internal use only.
        """
        if self.rec == 'nodes':
            vax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                vax[k, :] = np.asarray(self.vreclist[k])
        else:
            vax = np.zeros((len(self.x_rec), self.t_len))
            for k in range(len(self.x_rec)):
                vax[k, :] = np.asarray(self.vreclist[k])
        return vax

    def set_membrane_current_recorders(self):
        """
        Prepare the membrane current recording. For internal use only.
        """
        self.ireclist = neuron.h.List()
        if self.rec == 'nodes':
            # recording only on middle of all nodes
            for n in self.node:
                irec = neuron.h.Vector().record(n(0.5)._ref_i_membrane, sec=n)
                self.ireclist.append(irec)
        else:
            # recording on all segments
            for k in range(len(self.axon_path_type)):
                sec_type = self.axon_path_type[k]
                sec_index = self.axon_path_index[k]
                for position in self.rec_position_list[k]:
                    if sec_type == 'node':
                        irec = neuron.h.Vector().record(\
                            self.node[sec_index](position)._ref_i_membrane,\
                             sec=self.node[sec_index])
                        self.ireclist.append(irec)
                    elif sec_type == 'MYSA':
                        irec = neuron.h.Vector().record(\
                            self.MYSA[sec_index](position)._ref_i_membrane,\
                            sec=self.MYSA[sec_index])
                        self.ireclist.append(irec)
                    elif sec_type == 'FLUT':
                        irec = neuron.h.Vector().record(\
                            self.FLUT[sec_index](position)._ref_i_membrane,\
                            sec=self.FLUT[sec_index])
                        self.ireclist.append(irec)
                    else: # should be STIN
                        irec = neuron.h.Vector().record(\
                            self.STIN[sec_index](position)._ref_i_membrane,\
                            sec=self.STIN[sec_index])
                        self.ireclist.append(irec)

    def get_membrane_current(self):
        """
        get the membrane current at the end of simulation. For internal use only.
        """
        if self.rec == 'nodes':
            iax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                iax[k, :] = np.asarray(self.ireclist[k])
        else:
            iax = np.zeros((len(self.x_rec), self.t_len))
            for k in range(len(self.x_rec)):
                iax[k, :] = np.asarray(self.ireclist[k])
        return iax

    def set_ionic_current_recorders(self):
        """
        Prepare the ionic channels current recording. For internal use only.
        """
        if self.model == 'MRG':
            self.axnode_ina_reclist = neuron.h.List()
            self.axnode_inap_reclist = neuron.h.List()
            self.axnode_ik_reclist = neuron.h.List()
            self.axnode_il_reclist = neuron.h.List()
            for n in self.node:
                axnode_ina = neuron.h.Vector().record(n(0.5)._ref_ina_axnode, sec=n)
                axnode_inap = neuron.h.Vector().record(n(0.5)._ref_inap_axnode, sec=n)
                axnode_ik = neuron.h.Vector().record(n(0.5)._ref_ik_axnode, sec=n)
                axnode_il = neuron.h.Vector().record(n(0.5)._ref_il_axnode, sec=n)
                self.axnode_ina_reclist.append(axnode_ina)
                self.axnode_inap_reclist.append(axnode_inap)
                self.axnode_ik_reclist.append(axnode_ik)
                self.axnode_il_reclist.append(axnode_il)
        else: #should be Gaines, motor or sensory
            self.gaines_ina_reclist = neuron.h.List()
            self.gaines_inap_reclist = neuron.h.List()
            self.gaines_ik_reclist = neuron.h.List()
            self.gaines_ikf_reclist = neuron.h.List()
            self.gaines_il_reclist = neuron.h.List()
            for n in self.node:
                if self. model == 'Gaines_motor':
                    gaines_ina = neuron.h.Vector().record(n(0.5)._ref_ina_node_motor, sec=n)
                    gaines_inap = neuron.h.Vector().record(n(0.5)._ref_inap_node_motor, sec=n)
                    gaines_ik = neuron.h.Vector().record(n(0.5)._ref_ik_node_motor, sec=n)
                    gaines_ikf = neuron.h.Vector().record(n(0.5)._ref_ikf_node_motor, sec=n)
                    gaines_il = neuron.h.Vector().record(n(0.5)._ref_il_node_motor, sec=n)
                else: # should be Gaines_sensory
                    gaines_ina = neuron.h.Vector().record(n(0.5)._ref_ina_node_sensory, sec=n)
                    gaines_inap = neuron.h.Vector().record(n(0.5)._ref_inap_node_sensory, sec=n)
                    gaines_ik = neuron.h.Vector().record(n(0.5)._ref_ik_node_sensory, sec=n)
                    gaines_ikf = neuron.h.Vector().record(n(0.5)._ref_ikf_node_sensory, sec=n)
                    gaines_il = neuron.h.Vector().record(n(0.5)._ref_il_node_sensory, sec=n)
                self.gaines_ina_reclist.append(gaines_ina)
                self.gaines_inap_reclist.append(gaines_inap)
                self.gaines_ik_reclist.append(gaines_ik)
                self.gaines_ikf_reclist.append(gaines_ikf)
                self.gaines_il_reclist.append(gaines_il)

    def get_ionic_current(self):
        """
        get the ionic channels currents at the end of simulation. For internal use only.
        """
        if self.model == 'MRG':
            axnode_ina_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_inap_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_ik_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_il_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                axnode_ina_ax[k, :] = np.asarray(self.axnode_ina_reclist[k])
                axnode_inap_ax[k, :] = np.asarray(self.axnode_inap_reclist[k])
                axnode_ik_ax[k, :] = np.asarray(self.axnode_ik_reclist[k])
                axnode_il_ax[k, :] = np.asarray(self.axnode_il_reclist[k])
            results = [axnode_ina_ax, axnode_inap_ax, axnode_ik_ax, axnode_il_ax]
        else:
            gaines_ina_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_inap_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_ik_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_ikf_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_il_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                gaines_ina_ax[k, :] = np.asarray(self.gaines_ina_reclist[k])
                gaines_inap_ax[k, :] = np.asarray(self.gaines_inap_reclist[k])
                gaines_ik_ax[k, :] = np.asarray(self.gaines_ik_reclist[k])
                gaines_ikf_ax[k, :] = np.asarray(self.gaines_ikf_reclist[k])
                gaines_il_ax[k, :] = np.asarray(self.gaines_il_reclist[k])
            results = [gaines_ina_ax, gaines_inap_ax, gaines_ik_ax, gaines_ikf_ax, gaines_il_ax]
        return results

    def set_particules_values_recorders(self):
        """
        Prepare the particules current recording. For internal use only.
        """
        if self.model == 'MRG':
            self.axnode_mreclist = neuron.h.List()
            self.axnode_sreclist = neuron.h.List()
            self.axnode_hreclist = neuron.h.List()
            self.axnode_mpreclist = neuron.h.List()
            for n in self.node:
                axonde_m = neuron.h.Vector().record(n(0.5)._ref_m_axnode, sec=n)
                axonde_s = neuron.h.Vector().record(n(0.5)._ref_s_axnode, sec=n)
                axonde_h = neuron.h.Vector().record(n(0.5)._ref_h_axnode, sec=n)
                axonde_mp = neuron.h.Vector().record(n(0.5)._ref_mp_axnode, sec=n)
                self.axnode_mreclist.append(axonde_m)
                self.axnode_sreclist.append(axonde_s)
                self.axnode_hreclist.append(axonde_h)
                self.axnode_mpreclist.append(axonde_mp)
        else:
            self.gaines_mreclist = neuron.h.List()
            self.gaines_mpreclist = neuron.h.List()
            self.gaines_sreclist = neuron.h.List()
            self.gaines_hreclist = neuron.h.List()
            self.gaines_nreclist = neuron.h.List()
            for n in self.node:
                if self.model == 'Gaines_motor':
                    gaines_m = neuron.h.Vector().record(n(0.5)._ref_m_node_motor, sec=n)
                    gaines_mp = neuron.h.Vector().record(n(0.5)._ref_mp_node_motor, sec=n)
                    gaines_s = neuron.h.Vector().record(n(0.5)._ref_s_node_motor, sec=n)
                    gaines_h = neuron.h.Vector().record(n(0.5)._ref_h_node_motor, sec=n)
                    gaines_n = neuron.h.Vector().record(n(0.5)._ref_n_node_motor, sec=n)
                else:
                    gaines_m = neuron.h.Vector().record(n(0.5)._ref_m_node_sensory, sec=n)
                    gaines_mp = neuron.h.Vector().record(n(0.5)._ref_mp_node_sensory, sec=n)
                    gaines_s = neuron.h.Vector().record(n(0.5)._ref_s_node_sensory, sec=n)
                    gaines_h = neuron.h.Vector().record(n(0.5)._ref_h_node_sensory, sec=n)
                    gaines_n = neuron.h.Vector().record(n(0.5)._ref_n_node_sensory, sec=n)
                self.gaines_mreclist.append(gaines_m)
                self.gaines_mpreclist.append(gaines_mp)
                self.gaines_sreclist.append(gaines_s)
                self.gaines_hreclist.append(gaines_h)
                self.gaines_nreclist.append(gaines_n)

    def get_particles_values(self):
        """
        get the particules values at the end of simulation. For internal use only.
        """
        if self.model == 'MRG':
            axnode_m_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_s_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_h_ax = np.zeros((self.axonnodes, self.t_len))
            axnode_mp_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                axnode_m_ax[k, :] = np.asarray(self.axnode_mreclist[k])
                axnode_s_ax[k, :] = np.asarray(self.axnode_sreclist[k])
                axnode_h_ax[k, :] = np.asarray(self.axnode_hreclist[k])
                axnode_mp_ax[k, :] = np.asarray(self.axnode_mpreclist[k])
            results = [axnode_m_ax, axnode_s_ax, axnode_h_ax, axnode_mp_ax]
        else:
            gaines_m_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_mp_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_s_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_h_ax = np.zeros((self.axonnodes, self.t_len))
            gaines_n_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                gaines_m_ax[k, :] = np.asarray(self.gaines_mreclist[k])
                gaines_mp_ax[k, :] = np.asarray(self.gaines_mpreclist[k])
                gaines_s_ax[k, :] = np.asarray(self.gaines_sreclist[k])
                gaines_h_ax[k, :] = np.asarray(self.gaines_hreclist[k])
                gaines_n_ax[k, :] = np.asarray(self.gaines_nreclist[k])
            results = [gaines_m_ax, gaines_mp_ax, gaines_s_ax, gaines_h_ax, gaines_n_ax]
        return results


    def set_Nav_recorders(self):
        """
        Prepare the markov model recording. For internal use only.
        """
        # Nav1.1 variables
        self.I_nav11_reclist = neuron.h.List()
        self.C1_nav11_reclist = neuron.h.List()
        self.C2_nav11_reclist = neuron.h.List()
        self.O1_nav11_reclist = neuron.h.List()
        self.O2_nav11_reclist = neuron.h.List()
        self.I1_nav11_reclist = neuron.h.List()
        self.I2_nav11_reclist = neuron.h.List()
        # Nav1.6 variables
        self.I_nav16_reclist = neuron.h.List()
        self.C1_nav16_reclist = neuron.h.List()
        self.C2_nav16_reclist = neuron.h.List()
        self.O1_nav16_reclist = neuron.h.List()
        self.O2_nav16_reclist = neuron.h.List()
        self.I1_nav16_reclist = neuron.h.List()
        self.I2_nav16_reclist = neuron.h.List()
        for k in self.Markov_Nav_modeled_NoR:
            # Nav1.1
            I_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_ina_na11a,\
                sec=self.node[k])
            C1_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_C1_na11a,\
                sec=self.node[k])
            C2_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_C2_na11a,\
                sec=self.node[k])
            O1_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_O1_na11a,\
                sec=self.node[k])
            O2_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_O2_na11a,\
                sec=self.node[k])
            I1_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_I1_na11a,\
                sec=self.node[k])
            I2_nav11 = neuron.h.Vector().record(self.node[k](0.5)._ref_I2_na11a,\
                sec=self.node[k])
            self.I_nav11_reclist.append(I_nav11)
            self.C1_nav11_reclist.append(C1_nav11)
            self.C2_nav11_reclist.append(C2_nav11)
            self.O1_nav11_reclist.append(O1_nav11)
            self.O2_nav11_reclist.append(O2_nav11)
            self.I1_nav11_reclist.append(I1_nav11)
            self.I2_nav11_reclist.append(I2_nav11)
            # Nav1.6
            I_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_ina_na16a,\
                sec=self.node[k])
            C1_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_C1_na16a,\
                sec=self.node[k])
            C2_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_C2_na16a,\
                sec=self.node[k])
            O1_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_O1_na16a,\
                sec=self.node[k])
            O2_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_O2_na16a,\
                sec=self.node[k])
            I1_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_I1_na16a,\
                sec=self.node[k])
            I2_nav16 = neuron.h.Vector().record(self.node[k](0.5)._ref_I2_na16a,\
                sec=self.node[k])
            self.I_nav16_reclist.append(I_nav16)
            self.C1_nav16_reclist.append(C1_nav16)
            self.C2_nav16_reclist.append(C2_nav16)
            self.O1_nav16_reclist.append(O1_nav16)
            self.O2_nav16_reclist.append(O2_nav16)
            self.I1_nav16_reclist.append(I1_nav16)
            self.I2_nav16_reclist.append(I2_nav16)

    def get_Nav_values(self):
        """
        get the markov model at the end of simulation. For internal use only.
        """
        # Nav1.1 values
        I_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        C1_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        C2_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        O1_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        O2_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        I1_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        I2_nav11_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        for k in range(len(self.I_nav11_reclist)):
            I_nav11_ax[k, :] = np.asarray(self.I_nav11_reclist[k])
            C1_nav11_ax[k, :] = np.asarray(self.C1_nav11_reclist[k])
            C2_nav11_ax[k, :] = np.asarray(self.C2_nav11_reclist[k])
            O1_nav11_ax[k, :] = np.asarray(self.O1_nav11_reclist[k])
            O2_nav11_ax[k, :] = np.asarray(self.O2_nav11_reclist[k])
            I1_nav11_ax[k, :] = np.asarray(self.I1_nav11_reclist[k])
            I2_nav11_ax[k, :] = np.asarray(self.I2_nav11_reclist[k])
        # Nav1.6 values
        I_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        C1_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        C2_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        O1_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        O2_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        I1_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        I2_nav16_ax = np.zeros((len(self.Markov_Nav_modeled_NoR), self.t_len))
        for k in range(len(self.I_nav11_reclist)):
            I_nav16_ax[k, :] = np.asarray(self.I_nav16_reclist[k])
            C1_nav16_ax[k, :] = np.asarray(self.C1_nav16_reclist[k])
            C2_nav16_ax[k, :] = np.asarray(self.C2_nav16_reclist[k])
            O1_nav16_ax[k, :] = np.asarray(self.O1_nav16_reclist[k])
            O2_nav16_ax[k, :] = np.asarray(self.O2_nav16_reclist[k])
            I1_nav16_ax[k, :] = np.asarray(self.I1_nav16_reclist[k])
            I2_nav16_ax[k, :] = np.asarray(self.I2_nav16_reclist[k])
        return I_nav11_ax, C1_nav11_ax, C2_nav11_ax, O1_nav11_ax, O2_nav11_ax, I1_nav11_ax, I2_nav11_ax, I_nav16_ax, C1_nav16_ax, C2_nav16_ax, O1_nav16_ax, O2_nav16_ax, I1_nav16_ax, I2_nav16_ax
