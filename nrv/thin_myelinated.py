"""
NRV-thin_myelinated
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import math
import numpy as np
from .axons import *
from .log_interface import rise_error, rise_warning, pass_info

def get_Adelta_parameters(diameter):
    """
    Compute the A delta parameters, see on code for exact scientific references.

    Attributes
    ----------
    diameter    : float
        diameter of the axon (or fiber) to create um. Note that for mathematical reason, this should be > 2

    Returns
    -------
    axonD   : float
        internal axon diameter under the myeline, in um
    nodeD   : float
        length of the nodes of Ranvier, in um
    paraD   : float
        length of the paranodes, in um
    deltax  : float
        internode length, in um
    nl      : float
        number of myelin sheaths in average
    """
    # taken from Berthold, Nilsson and Rydmark, to get the number of layer of myelin layers from axonD
    # from 6 months dorsal root cat
    # Berthold, C. H., Nilsson, I., & Rydmark, M. (1983). Axon diameter and myelin sheath thickness in nerve fibres of the
    # ventral spinal root of the seventh lumbar nerve of the adult and developing cat. Journal of anatomy, 136(Pt 3), 483.
    C0 = 24.72
    C1 = -5.73
    C2 = 155.44
    # thickness of a myelin layer, in um , from Berthold, Nilsson and Rydmark 1983
    k = 0.018
    # node diameter and corresponding number of myelin layer taken from Rydmark and Berthold
    # Berthold, C. H., & Rydmark, M. (1983). Electron microscopic serial section analysis of nodes of Ranvier in lumbosacral
    # spinal roots of the cat: ultrastructural organization of nodal compartments in fibres of different sizes. Journal of Neurocytology, 12(3), 475-505.
    nodeD_Rydmark = [0.8, 1.5, 2.6, 3.3, 4.3]
    nl_Rydmark = [27, 46, 88, 105, 123]
    nodeD_vs_nl_poly = np.poly1d(np.polyfit(nl_Rydmark, nodeD_Rydmark, 3))

    # step 1: get axonD
    def solver(D, C0, C1, C2, k):
        def fiber_axon_diameter_equation(axonD):
            return (2*k*C0 - D) + axonD*(1+2*k*C1) + 2*k*C2*np.log10(axonD)
        return fiber_axon_diameter_equation

    root = optimize.fsolve(solver(diameter, C0, C1, C2, k), 1)
    axonD = root[0]
    # step 2: get nl
    nl = C0 + C1*axonD + C2*np.log10(axonD)
    # step 3: get nodeD
    nodeD = nodeD_vs_nl_poly(nl)
    # step 4: get deltax
    # interpolation from Jacobs, J. M., & Love, S. (1985). Qualitative and quantitative morphology of human sural nerve at different ages. Brain, 108(4), 897-924.
    deltax = 80*(diameter-1)
    # step 5: paraD
    # arbitrary conical structure not possible in neuron, therefore, an average of axonD and nodeD to ensure transition
    # matter of choice, could also be changed to paraD = nodeD as in MRG model
    paraD = (nodeD + axonD)/2

    return float(axonD), float(nodeD), float(paraD), float(deltax), float(nl)

def get_length_from_nodes_thin(diameter, nodes):
    """
    Function to compute the length of a myelinated axon to get the correct number of Nodes of Ranvier
    for A delta thin myelinated models only. Not compatible with myelinated models.

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
    deltax = 80*(diameter-1)
    return float(math.ceil(deltax*(nodes-1)))

###############################################
## Thin myelinated axons:                    ##
##         specific class for A-delta fibers ##
###############################################
class thin_myelinated(axon):
    """
    Thin Mylineated, A-delta specific, axon class. Automatic refinition of all neuron sections and properties. User-friendly object including model definition
    Inherits from axon class. see axon for further detail.
    """
    def __init__(self, y, z, d, L, model='Extended_Gaines', dt=0.001, node_shift=0,\
        Nseg_per_sec=0, freq=100, freq_min=0, mesh_shape='plateau_sigmoid', alpha_max=0.3,\
        d_lambda=0.1, rec='nodes', v_init=None, md_based_v_init=True, T=None, ID=0, threshold=-40):
        """
        initialisation of a thinnmyelinted (A-delta) axon

        Parameters
        ----------
        y               : float
            y coordinate for the axon, in um
        z               : float
            z coordinate for the axon, in um
        d               : float
            axon diameter, in um. This value has to be greater than 2 for physiological reasons (positive internode length). This object has been designed to be functionnal below 6 um.
        L               : float
            axon length along the x axins, in um
        model           : str
            choice of conductance double-cable based model, possibly:
            'RGK'               : by default, model developped based on ion channels detailed in [1]
            'Extended_Gaines'   : extention of the Gaines sensory model with same doble cable parameters as RGK, see [2] for details on channels
                                        note: the Gaines motor has not been extented as A-delta are supposed to be sensory fibers only
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
        md_based_v_init : bool
            If true, the init voltage is decided by the model choice
        T               : gloat
            temperature in C, set None to get an automatically model attributed value
        ID              : int
            axon ID, by default set to 0,
        threshold       : float
            voltage threshold in mV for further spike detection in post-processing, by defautl set to -40mV, see post-processing library for further help

        Note
        ----
        scientific sources for models:
        [1] Tigerholm, J., Poulsen, A. H., Andersen, O. K., and Morch, C. D. (2019). from perception threshold to ion channels—a computational study. Biophysical journal, 117(2), 281-295.
        [2] Gaines, J. L., Finn, K. E., Slopsema, J. P., Heyboer, L. A.,  Polasek, K. H. (2018). A model of motor and sensory axon activation in the median nerve using surface electrical stimulation. Journal of computational neuroscience, 45(1), 29-43.
        """
        super().__init__(y, z, d, L, dt=dt, Nseg_per_sec=Nseg_per_sec,\
            freq=freq, freq_min=freq_min, mesh_shape=mesh_shape, alpha_max=alpha_max, \
            d_lambda=d_lambda, v_init=v_init, T=T, ID=ID, threshold=threshold)
        self.myelinated = True
        self.thin = True
        self.rec = rec
        self.model = model
        ## Handling v_init
        if v_init is None:
            # model driven
            if self.model == 'RGK':
                self.v_init = -64.2
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
        self.axonD, self.nodeD, self.paraD, self.deltax, self.nl = get_Adelta_parameters(self.d)
        # Morphological parameters
        self.nodelength = 2
        self.paralength = 10 # Tigerholm used 5
        self.space_p = 0.002
        self.space_i = 0.004
        self.interlength = (self.deltax-self.nodelength-(2*self.paralength))/6
        # electrical parameters
        self.rhoa = 0.7e6   # Ohm-um
        self.mycm = 0.1     # uF/cm2/lamella membrane
        self.mygm = 0.001   # S/cm2/lamella membrane
        self.Rpn0 = (self.rhoa*.01)/(math.pi*((((self.nodeD/2)+self.space_p)**2)-\
            ((self.nodeD/2)**2)))
        self.Rpn1 = (self.rhoa*.01)/(math.pi*((((self.paraD/2)+self.space_p)**2)-\
            ((self.paraD/2)**2)))
        self.Rpx = (self.rhoa*.01)/(math.pi*((((self.axonD/2)+self.space_i)**2)-\
            ((self.axonD/2)**2)))

        #########################
        ## morphology planning ##
        #########################
        # thin myelinated double cable sequence sequence
        self.MRG_Sequence = ['node', 'MYSA', 'STIN', 'STIN', 'STIN', 'STIN', 'STIN', 'STIN', 'MYSA']
        # basic MRG starts with the node, if needed, adapt the sequence
        self.node_shift = node_shift
        if self.node_shift == 0:
            # no Rotation
            self.this_ax_sequence = self.MRG_Sequence
            self.first_section_size = self.nodelength

        elif self.node_shift < (self.paralength)/self.deltax:
            # rotation of less than 1 MYSA
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 1)
            self.first_section_size = self.paralength - (self.node_shift*self.deltax)

        elif self.node_shift < (self.paralength + self.interlength)/self.deltax:
            # rotation of 1 MYSA and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 2)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength)

        elif self.node_shift < (self.paralength + 2*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 1 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 3)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength - self.interlength)

        elif self.node_shift < (self.paralength+ 3*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 2 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 4)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength - 2*self.interlength)

        elif self.node_shift < (self.paralength + 4*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 3 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 5)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength - 3*self.interlength)

        elif self.node_shift < (self.paralength + 5*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 4 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 6)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength - 4*self.interlength)

        elif self.node_shift < (self.paralength + 6*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 5 STIN and less than a STIN
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 7)
            self.first_section_size = self.interlength - (self.node_shift*self.deltax - \
                self.paralength - 5*self.interlength)

        elif self.node_shift < (2*self.paralength + 6*self.interlength)/self.deltax:
            # rotation of 1 MYSA, 6 STIN and less than a MYSA
            # WARNING FOR DEV : the unprobable case of a node cut in two halfs is not considered...
            self.this_ax_sequence = rotate_list(self.MRG_Sequence, 8)
            self.first_section_size = self.deltax*(1-self.node_shift)

        ################
        ## morphology ##
        ################
        self.axonnodes = 0      # number of nodes in the axon
        self.node = []          # list of nodes in the axon
        self.paranodes = 0      # number of MYSA in the axon
        self.MYSA = []          # list of MYSA in the axon
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
                if self.paranodes != 0:
                    self.node[-1].connect(self.MYSA[-1], 1, 0)

            elif self.this_ax_sequence[pos_in_sequence] == 'MYSA':
                # you need to create a MYSA
                self.MYSA.append(neuron.h.Section(name='MYSA[%d]' % self.paranodes))
                self.axon_path_type.append('MYSA')
                self.axon_path_index.append(self.paranodes)
                self.paranodes += 1
                self.Nsec += 1
                # increment the prov length and check it is not to much
                if prov_length + self.paralength >= self.L:
                    # it will be the last section to add to the axon
                    self.last_section_kind = 'MYSA'
                    self.last_section_size = self.L - prov_length
                prov_length += self.paralength
                # CONNECT THE MYSA TO ITS PARENT: a MYSA can have for parent a node or a TIN, check it's not the start...
                connect_to_type = self.this_ax_sequence[pos_in_sequence - 1] # get parent type
                if connect_to_type == 'node' and self.axonnodes != 0:
                    self.MYSA[-1].connect(self.node[-1], 1, 0)
                if connect_to_type == 'STIN' and self.axoninter != 0:
                    self.MYSA[-1].connect(self.STIN[-1], 1, 0)

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
                # CONNECT THE STIN TO ITS PARENT: a STIN can have for parent a STIN od a MYSA, check it's not the start...
                connect_to_type = self.this_ax_sequence[pos_in_sequence - 1]
                if connect_to_type == 'STIN' and self.axoninter > 1:
                    self.STIN[-1].connect(self.STIN[-2], 1, 0)
                if connect_to_type == 'MYSA' and self.paranodes != 0:
                    self.STIN[-1].connect(self.MYSA[-1], 1, 0)

        if self.node == []:
            #logging.warning(
            rise_warning('Warning, thin myelinated axon without node... this can cause latter \
                errors and is maybe unwanted ?\n')

        ####################
        ## programm model ##
        ####################
        self.__set_model(self.model)
        # adjust the length of the first section
        if self.this_ax_sequence[0] == 'node':
            self.node[0].L = self.first_section_size
        elif self.this_ax_sequence[0] == 'MYSA':
            self.MYSA[0].L = self.first_section_size
        else: # should be a STIN
            self.STIN[0].L = self.first_section_size
        # adjust the length if the last section
        if self.last_section_kind == 'node':
            self.node[-1].L = self.last_section_size
        elif self.last_section_kind == 'MYSA':
            self.MYSA[-1].L = self.last_section_size
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
                'RGK'               : specific A-delta model
                'Extended_Gaines'   : extension of the Gaines sensory model to lower diameter values
        """
        # NB: the remaining commented values correspond to an attempt of MRG extension
        # This does not work... stimulation causes a double spike, probabely caused by lack of Potassium channel on paranodes
        # comment to keep for demos only...
        for n in self.node:
            n.nseg = 1
            n.diam = self.nodeD
            n.L = self.nodelength
            if model == 'Extended_Gaines':
                #n.insert('axnode')
                n.Ra = self.rhoa/10000
                n.cm = 2
                n.insert('node_sensory')
            else: #RGK
                n.Ra = 130
                n.cm = 1
                n.insert('nav1p9')
                n.gbar_nav1p9 = 1.1e-3
                n.celsiusT_nav1p9 = self.T
                n.insert('nax')
                n.gbar_nax = 1.45e-1
                n.insert('ks')
                n.gbar_ks = 2.10e-3
                n.v = self.v_init
                n.insert('pas')
                n.g_pas = 1e-7
                n.e_pas = -60
            n.insert('extracellular')
            n.xraxial[0] = self.Rpn0
            n.xg[0] = 1e10
            n.xc[0] = 0
        for m in self.MYSA:
            m.nseg = 1
            m.diam = self.d
            m.L = self.paralength
            m.cm = 2*self.paraD/self.d
            if model == 'Extended_Gaines':
                m.Ra = self.rhoa*(1/(self.paraD/self.d)**2)/10000
                #m.insert('pas')
                #m.g_pas = 0.001*self.paraD/self.d
                #m.e_pas = -80
                m.insert('mysa_sensory')
            else:
                m.Ra = 130
                m.insert('kdrTiger')
                m.celsiusT_kdrTiger = self.T
                m.gbar_kdrTiger = 4.80e-3
                m.insert('h')
                m.gbar_h = 1.52e-4
                m.celsiusT_h = self.T
                m.insert('kaslow')
                m.gbar_kaslow = 3.0e-3
                m.v = self.v_init
                m.insert('pas')
                m.g_pas = 1e-7
                m.e_pas = -60
            m.insert('extracellular')
            m.xraxial[0] = self.Rpn1
            m.xg[0] = self.mygm/(self.nl*2)
            m.xc[0] = self.mycm/(self.nl*2)
        for s in self.STIN:
            s.nseg = 1
            s.diam = self.d
            s.L = self.interlength
            s.cm = 2*self.axonD/self.d
            if self.model == 'Extended_Gaines':
                s.Ra = self.rhoa*(1/(self.axonD/self.d)**2)/10000
                s.insert('stin_sensory')
            else:
                s.Ra = 130
                s.insert('pas')
                s.g_pas = 1e-7#0.0001*self.axonD/self.d
                s.e_pas = -60
            s.insert('extracellular')
            s.xraxial[0] = self.Rpx
            s.xg[0] = self.mygm/(self.nl*2)
            s.xc[0] = self.mycm/(self.nl*2)

    def __set_Nseg(self):
        """
        Set the number of segments automatically acording initialization. For internal use only.
        """
        if self.Nseg_per_sec != 0:
            # all sections will have a fixed number of segment chosen by user
            for n in self.node:
                n.nseg = self.Nseg_per_sec
            for m in self.MYSA:
                m.nseg = self.Nseg_per_sec
            for s in self.STIN:
                s.nseg = self.Nseg_per_sec
            self.node_Nseg = self.axonnodes * self.Nseg_per_sec
            self.MYSA_Nseg = self.paranodes * self.Nseg_per_sec
            self.STIN_Nseg = self.axoninter * self.Nseg_per_sec
        else:
            # here comes the dlambda rule
            self.node_Nseg = 0
            self.MYSA_Nseg = 0
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
                        Nseg = d_lambda_rule(self.node[sec_index].L, self.d_lambda, self.freq, \
                            self.node[sec_index])
                        self.node[sec_index].nseg = Nseg
                        self.node_Nseg += Nseg
                    elif sec_type == 'MYSA':
                        Nseg = d_lambda_rule(self.MYSA[sec_index].L, self.d_lambda, self.freq, \
                            self.MYSA[sec_index])
                        self.MYSA[sec_index].nseg = Nseg
                        self.MYSA_Nseg += Nseg
                    else: # should be STIN
                        Nseg = d_lambda_rule(self.STIN[sec_index].L, self.d_lambda, self.freq, \
                            self.STIN[sec_index])
                        self.STIN[sec_index].nseg = Nseg
                        self.STIN_Nseg += Nseg
        self.Nseg = self.node_Nseg + self.MYSA_Nseg + self.STIN_Nseg

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
        Prepare the membrane voltage recording
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
                    else: # should be STIN
                        vrec = neuron.h.Vector().record(self.STIN[sec_index](position)._ref_v, \
                            sec=self.STIN[sec_index])
                        self.vreclist.append(vrec)

    def get_membrane_voltage(self):
        """
        get the membrane voltage at the end of simulation
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
                            self.node[sec_index](position)._ref_i_membrane, \
                            sec=self.node[sec_index])
                        self.ireclist.append(irec)
                    elif sec_type == 'MYSA':
                        irec = neuron.h.Vector().record(\
                            self.MYSA[sec_index](position)._ref_i_membrane, \
                            sec=self.MYSA[sec_index])
                        self.ireclist.append(irec)
                    else: # should be STIN
                        irec = neuron.h.Vector().record(\
                            self.STIN[sec_index](position)._ref_i_membrane, \
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
        Prepare the ionic current recording. For internal use only.
        """
        if self.model == 'Extended_Gaines':
            self.gaines_ina_reclist = neuron.h.List()
            self.gaines_inap_reclist = neuron.h.List()
            self.gaines_ik_reclist = neuron.h.List()
            self.gaines_ikf_reclist = neuron.h.List()
            self.gaines_il_reclist = neuron.h.List()
            for n in self.node:
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
        else:
            self.RGK_ina_reclist = neuron.h.List()
            self.RGK_ik_reclist = neuron.h.List()
            self.RGK_ipas_reclist = neuron.h.List()
            for n in self.node:
                RGK_ina = neuron.h.Vector().record(n(0.5)._ref_nai, sec=n)
                RGK_ik = neuron.h.Vector().record(n(0.5)._ref_ki, sec=n)
                RGK_ipas = neuron.h.Vector().record(n(0.5)._ref_i_pas, sec=n)
                self.RGK_ina_reclist.append(RGK_ina)
                self.RGK_ik_reclist.append(RGK_ik)
                self.RGK_ipas_reclist.append(RGK_ipas)

    def get_ionic_current(self):
        """
        get the ionic currents at the end of simulation. For internal use only.
        """
        if self.model == 'Extended_Gaines':
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
        else:
            RGK_ina_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_ik_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_ipas_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                RGK_ina_ax[k, :] = np.asarray(self.RGK_ina_reclist[k])
                RGK_ik_ax[k, :] = np.asarray(self.RGK_ik_reclist[k])
                RGK_ipas_ax[k, :] = np.asarray(self.RGK_ipas_reclist[k])
            results = [RGK_ina_ax, RGK_ik_ax, RGK_ipas_ax]
        return results

    def set_particules_values_recorders(self):
        """
        Prepare the particules values recording. For internal use only.
        """
        if self.model == 'Extended_Gaines':
            self.gaines_mreclist = neuron.h.List()
            self.gaines_mpreclist = neuron.h.List()
            self.gaines_sreclist = neuron.h.List()
            self.gaines_hreclist = neuron.h.List()
            self.gaines_nreclist = neuron.h.List()
            for n in self.node:
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
        else:
            self.RGK_m_nav1p9_reclist = neuron.h.List()
            self.RGK_h_nav1p9_reclist = neuron.h.List()
            self.RGK_s_nav1p9_reclist = neuron.h.List()
            self.RGK_m_nax_reclist = neuron.h.List()
            self.RGK_h_nax_reclist = neuron.h.List()
            self.RGK_ns_ks_reclist = neuron.h.List()
            self.RGK_nf_ks_reclist = neuron.h.List()
            for n in self.node:
                # Nav1p9
                m_nav1p9 = neuron.h.Vector().record(n(0.5)._ref_m_nav1p9, sec=n)
                h_nav1p9 = neuron.h.Vector().record(n(0.5)._ref_h_nav1p9, sec=n)
                s_nav1p9 = neuron.h.Vector().record(n(0.5)._ref_s_nav1p9, sec=n)
                # Nax
                m_nax = neuron.h.Vector().record(n(0.5)._ref_m_nax, sec=n)
                h_nax = neuron.h.Vector().record(n(0.5)._ref_h_nax, sec=n)
                # Ks
                ns_ks = neuron.h.Vector().record(n(0.5)._ref_ns_ks, sec=n)
                nf_ks = neuron.h.Vector().record(n(0.5)._ref_nf_ks, sec=n)
                self.RGK_m_nav1p9_reclist.append(m_nav1p9)
                self.RGK_h_nav1p9_reclist.append(h_nav1p9)
                self.RGK_s_nav1p9_reclist.append(s_nav1p9)
                self.RGK_m_nax_reclist.append(m_nax)
                self.RGK_h_nax_reclist.append(h_nax)
                self.RGK_ns_ks_reclist.append(ns_ks)
                self.RGK_nf_ks_reclist.append(nf_ks)

    def get_particles_values(self):
        """
        get the particules values at the end of simulation. For internal use only.
        """
        if self.model == 'Extended_Gaines':
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
        else:
            RGK_m_nav1p9_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_h_nav1p9_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_s_nav1p9_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_m_nax_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_h_nax_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_ns_ks_ax = np.zeros((self.axonnodes, self.t_len))
            RGK_nf_ks_ax = np.zeros((self.axonnodes, self.t_len))
            for k in range(self.axonnodes):
                RGK_m_nav1p9_ax[k, :] = np.asarray(self.RGK_m_nav1p9_reclist[k])
                RGK_h_nav1p9_ax[k, :] = np.asarray(self.RGK_h_nav1p9_reclist[k])
                RGK_s_nav1p9_ax[k, :] = np.asarray(self.RGK_s_nav1p9_reclist[k])
                RGK_m_nax_ax[k, :] = np.asarray(self.RGK_m_nax_reclist[k])
                RGK_h_nax_ax[k, :] = np.asarray(self.RGK_h_nax_reclist[k])
                RGK_ns_ks_ax[k, :] = np.asarray(self.RGK_ns_ks_reclist[k])
                RGK_nf_ks_ax[k, :] = np.asarray(self.RGK_nf_ks_reclist[k])
            results = [RGK_m_nav1p9_ax, RGK_h_nav1p9_ax, RGK_s_nav1p9_ax, RGK_m_nax_ax,\
                RGK_h_nax_ax, RGK_ns_ks_ax, RGK_nf_ks_ax]
        return results
