"""
NRV-fascicule generator
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
import faulthandler
import os
import math
import numpy as np
from scipy import stats
from scipy.stats import rv_continuous
from scipy.optimize import curve_fit
from scipy import spatial
import matplotlib.pyplot as plt
import numba
from .log_interface import rise_error, rise_warning, pass_info, progression_popup

# WARNING:
# no prompt message for numpy division by zeros: handled in the code !!!
np.seterr(divide='ignore', invalid='ignore')

# verbosity level
fg_verbose = True

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

# get the built-in material librairy
dir_path = os.path.dirname(os.path.realpath(__file__))
stat_library = os.listdir(dir_path+'/stats/')

#################################################
## Nerve composition statistics and generators ##
#################################################
myelinated_stats = ['Schellens_1', 'Schellens_2', 'Ochoa_M', 'Jacobs_9_A', 'Jacobs_9_B',\
    'Jacobs_9_C', 'Jacobs_9_D']
unmyelinated_stats = ['Ochoa_U', 'Jacobs_11_A', 'Jacobs_11_B', 'Jacobs_11_C', 'Jacobs_11_D']

def load_stat(stat_name):
    """
    Load a statistic stored in the included librairy or specified by the user in a csv file (first corlumn: axon diameter bin start - second corlumn: proportion)

    Parameters
    ----------
    stat_name : str
        name of the statistic in the librairy or path to a new librairy in csv

    Returns
    -------
    diameters   : list
        diameters as start of bins of the histogram
    presence    : list
        quantities of presence of each bin in the histogram
    """
    f_in_librairy = str(stat_name)+'.csv'
    if f_in_librairy in stat_library:
        stat_file = np.genfromtxt(dir_path+'/stats/'+f_in_librairy, delimiter=',')
    else:
        stat_file = np.genfromtxt(dir_path+'/stats/'+f_in_librairy, delimiter=',')
    diameters = stat_file[:, 0]
    presence = stat_file[:, 1]
    return diameters, presence

def one_Gamma(x, a1, beta1, c1):
    """
    Gamma function, mono-modal, to interpolate unmyelinated statistics.

    Parameters
    ----------
    x       : float
        variable of the Gamma function, will correspond to diameter
    a1      : float
        shape parameter
    beta1   : float
        scale parameter
    c1      : float
        gain applied to the gamma function

    Note
    ----
    location of the gamma pdf function is fixed to 0.2, diameters will be interpolated above this minimal value.
    """
    return c1*(stats.gamma.pdf(x, a1, scale=1/beta1, loc=0.2))

def two_Gamma(x, a1, beta1, c1, a2, beta2, c2, transition):
    """
    Gamma function, bi-modal, to interpolate myelinated statistics.

    Parameters
    ----------
    x           : float
        variable of the Gamma function, will correspond to diameter
    a1          : float
        shape parameter on the first (lowest) lobe
    beta1       : float
        scale parameter on the first (lowest) lobe
    c1          : float
        gain applied to the gamma function on the first (lowest) lobe
    a2          : float
        shape parameter on the second (highest) lobe
    beta2       : float
        scale parameter on the second (highest) lobe
    c2          : float
        gain applied to the gamma function on the second (highest) lobe
    transition  :float
        diameter value at the transition between the two lobes

    Note
    ----
    location of the gamma pdf first function is fixed to 2, diameters will be interpolated above this minimal value. This corresponds to the minimal A-delta diamter tolerated value.
    """
    return c1*(stats.gamma.pdf(x, a1, scale=1/beta1, loc=2)) + c2*(stats.gamma.pdf(x, a2, \
        scale=1/beta2, loc=transition))

class nerve_gen_one_gamma(rv_continuous):
    """
    Class to create specific repartition law generator for unmyelinated axons. Inherits from scipy rv_continuous class. Some methods are overwritten
    """
    def set_bounds(self, v_min, v_max):
        """
        Set bounds to the generator.

        Parameters
        ----------
        v_min   : float
            minimum value
        v_max   : float
            maximum value
        """
        self.a = v_min
        self.b = v_max

    def configure(self, a1, beta1, c1):
        """
        Set the value from interpolated data

        Parameters
        ----------
        a1      : float
            shape parameter
        beta1   : float
            scale parameter
        c1      : float
            gain applied to the gamma function

        """
        self.a1 = a1
        self.beta1 = beta1
        self.c1 = c1

    def _pdf(self, x):
        """
        overwritting the pdf to custom law, same definition as one_Gamma described upper.
        """
        return self.c1*(stats.gamma.pdf(x, self.a1, scale=1/self.beta1, loc=0.2))

class nerve_gen_two_gamma(rv_continuous):
    """
    Class to create specific repartition law generator for myelinated axons. Inherits from scipy rv_continuous class. Some methods are overwritten
    """
    def set_bounds(self, v_min, v_max):
        """
        Set bounds to the generator.

        Parameters
        ----------
        v_min   : float
            minimum value
        v_max   : float
            maximum value
        """
        self.a = v_min
        self.b = v_max

    def configure(self, a1, beta1, c1, a2, beta2, c2, transition):
        """
        Set the value from interpolated data

        Parameters
        ----------
        a1          : float
            shape parameter on the first (lowest) lobe
        beta1       : float
            scale parameter on the first (lowest) lobe
        c1          : float
            gain applied to the gamma function on the first (lowest) lobe
        a2          : float
            shape parameter on the second (highest) lobe
        beta2       : float
            scale parameter on the second (highest) lobe
        c2          : float
            gain applied to the gamma function on the second (highest) lobe
        transition  :float
            diameter value at the transition between the two lobes

        """
        self.a1 = a1
        self.a2 = a2
        self.beta1 = beta1
        self.beta2 = beta2
        self.c1 = c1
        self.c2 = c2
        self.transition = transition

    def _pdf(self, x):
        """
        overwritting the pdf to custom law, same definition as two_Gamma described upper.
        """
        return self.c1*(stats.gamma.pdf(x, self.a1, scale=1/self.beta1, loc=2)) +\
            self.c2*(stats.gamma.pdf(x, self.a2, scale=1/self.beta2, loc=self.transition))

def create_generator_from_stat(stat, myelinated=True, dmin=None, dmax=None):
    """
    Create a statistical generator (type rv_continuous) for a given statistic.

    Parameters
    ----------
    stat        : str
        name of the statistic in the librairy or path to a new librairy in csv
    myelinated  : bool
        True if the statistic is describing myelinated diameters, esle False. If the statisticis in the librairy, this will be automatically chosen.
    dmin        : float
        minimal diameter to consider, in um. If None, the minimal value of the statistic is taken
    dmax        : float
        minimal diameter to consider, in um. If None, the maximal value of the statistic plus bin size is taken

    Returns
    -------
    generator   : rv_continuous
        Generator object corresponding to the statistic.
    """
    # Check if myelinated or not for standard stats
    if stat in myelinated_stats:
        myelinated = True
    elif stat in unmyelinated_stats:
        myelinated = False
    # load the stat
    diameters, presence = load_stat(stat)
    # chose min max values for the axon diameters
    if dmin is None:
        dmin = min(diameters)
    if dmax is None:
        bin_size = diameters[1] - diameters[0]
        dmax = max(diameters) + bin_size
    # perform stat fitting and create generator
    if myelinated:
        popt1, pcov1 = curve_fit(two_Gamma, xdata=diameters, ydata=presence, \
            bounds=([1, 0, 0, 1, 0, 0, 2], [np.inf, 15, np.inf, np.inf, 15, np.inf, 14]))
        generator = nerve_gen_two_gamma()
        generator.set_bounds(dmin, dmax)
        generator.configure(*popt1)
    else:
        popt1, pcov1 = curve_fit(one_Gamma, xdata=diameters, ydata=presence, \
            bounds=([1, 0, 0], [np.inf, 10, np.inf]))
        generator = nerve_gen_one_gamma()
        generator.set_bounds(dmin, dmax)
        generator.configure(*popt1)
    return generator, popt1, pcov1


def create_axon_population(N, percent_unmyel=0.7, M_stat='Schellens_1', U_stat='Ochoa_U'):
    """
    Create a virtual population of axons (no Neuron implementation, axon class not called) of a controled number, with controlled statistics.

    Parameters
    ----------
    N               : int
        Number of axon to generate for the population (Unmyelinated and myelinated)
    percent_unmyel  : float
        ratio of unmyelinated axons in the population. Should be between 0 and 1.
    M_stat          : str
        name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
    U_stat          : str
        name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition

    Returns
    -------
    axons_diameters     : np.array
        Array of length N, containing all the diameters of the generated axon population
    axons_type          : np.array
        Array of length N, containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
    M_diam_list         : np.array
        list of myelinated only diameters
    U_diam_list         : np.array
        list of unmyelinated only diamters
    """
    # create generators
    M_gen, M_popt, M_pcov = create_generator_from_stat(M_stat)
    U_gen, U_popt, U_pcov = create_generator_from_stat(U_stat)
    # number of myelinated and unmyelinated axons to create
    U = int(N*percent_unmyel)
    M = N - U
    pass_info('On '+str(N)+' axons to generate, there are '+str(M)+' Myelinated and '+\
        str(U)+' Unmyelinated')
    # generate the myelinated axons
    pass_info('... generating the myelinated axons diameters, this may take a while')
    #M_diam_list = M_gen.rvs(1,size = M)
    M_diam_list = []
    max_diam_value = M_gen.b - 0.01*(M_gen.b - M_gen.a)
    for k in range(M):
        progression_popup(k, M, begin_message='\t axon ', endl="\r")
        prov_diam = M_gen.rvs(1, size=1)[0]
        while prov_diam > max_diam_value:
            # definitely non ideal, but rv_continuous has a tendency of generating diameters
            # at the max value, this while prevent from such accumulation
            prov_diam = M_gen.rvs(1, size=1)[0]
        M_diam_list.append(prov_diam)
    M_type = np.ones(M)
    # generate the unmyelinated axons
    pass_info('... generating the unmyelinated axons diameters, this may take a while')
    U_diam_list = []
    max_diam_value = U_gen.b - 0.01*(U_gen.b - U_gen.a)
    for k in range(U):
        print('\t axon ' + f"{k+1}" + '/' + str(U), end="\r")
        prov_diam = U_gen.rvs(1, size=1)[0]
        while prov_diam > max_diam_value:               # same as for myelinated...
            prov_diam = U_gen.rvs(1, size=1)[0]
        U_diam_list.append(prov_diam)
    U_type = np.zeros(U)
    # final shuffle between unmyelinated and myelinated
    pass_info('... performing a shuffle on myelinated and unmyelinated axons')
    shuffle_mask = np.random.permutation(N)
    axons_diameters = np.concatenate((M_diam_list, U_diam_list))
    axons_type = np.concatenate((M_type, U_type))
    axons_diameters = axons_diameters[shuffle_mask]
    axons_type = axons_type[shuffle_mask]
    return axons_diameters, axons_type, M_diam_list, U_diam_list

def fill_area_with_axons(A, percent_unmyel=0.7, FVF=0.55, M_stat='Schellens_1', U_stat='Ochoa_U'):
    """
    Create a virtual population of axons (no Neuron implementation, axon class not called) to fill a specified area, with controlled statistics.

    Parameters
    ----------
    A               : float
        surface area to fill, in um**2
    percent_unmyel  : float
        ratio of unmyelinated axons in the population. Should be between 0 and 1.
    FVF             :
        Fiber Volume Fraction estimated for the area. By default set to 0.55
    M_stat          : str
        name of the statistic in the librairy or path to a new librairy in csv for myelinated diameters repartition
    U_stat          : str
        name of the statistic in the librairy or path to a new librairy in csv for unmyelinated diameters repartition

    Returns
    -------
    axons_diameters     : np.array
        Array  containing all the diameters of the generated axon population
    axons_type          : np.array
        Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
    M_diam_list         : np.array
        list of myelinated only diameters
    U_diam_list         : np.array
        list of unmyelinated only diamters
    """
    # create generators
    M_gen, M_popt, M_pcov = create_generator_from_stat(M_stat)
    M_diam_list = []
    M_max_diam_value = M_gen.b - 0.01*(M_gen.b - M_gen.a)
    U_gen, U_popt, U_pcov = create_generator_from_stat(U_stat)
    U_diam_list = []
    U_max_diam_value = U_gen.b - 0.01*(U_gen.b - U_gen.a)
    # area
    A_ax = 0
    A_total = 0
    # axon lists
    M_diam_list = []
    U_diam_list = []
    # loop
    while A_total < A:
        filled = A_total / A
        progression_popup(round(filled*100), 100, begin_message='\t Area filled at ', endl="\r")
        #print('\t Area filled at ' + f"{round(filled*100)}" + ' percent', end="\r")
        U_or_M = np.random.uniform(0, 1)
        if U_or_M < percent_unmyel:
            # generate a unmyelinated axon
            prov_diam = U_gen.rvs(1, size=1)[0]
            while prov_diam > U_max_diam_value:
                prov_diam = U_gen.rvs(1, size=1)[0]
            U_diam_list.append(prov_diam)
            A_ax += np.power(U_diam_list[-1]/2, 2)*np.pi
        else:
            prov_diam = M_gen.rvs(1, size=1)[0]
            while prov_diam > M_max_diam_value:
                prov_diam = M_gen.rvs(1, size=1)[0]
            M_diam_list.append(prov_diam)
            A_ax += np.power(M_diam_list[-1]/2, 2)*np.pi
        A_total = A_ax / FVF
    # concatenate and shuffle
    M = len(M_diam_list)
    U = len(U_diam_list)
    N = M + U
    M_type = np.ones(M)
    U_type = np.zeros(U)
    shuffle_mask = np.random.permutation(N)
    axons_diameters = np.concatenate((M_diam_list, U_diam_list))
    axons_type = np.concatenate((M_type, U_type))
    axons_diameters = axons_diameters[shuffle_mask]
    axons_type = axons_type[shuffle_mask]
    return axons_diameters, axons_type, M_diam_list, U_diam_list

def shuffle_population(axons_diameters, axons_type):
    """
    Shuffle an axonal population

    Parameters
    ----------
    axons_diameters : np.array
        array containing the axons diameters
    axons_type      : np.array
        array containing the axons type ('1' for myelinated, '0' for unmyelinated)

    Returns
    -------
    axons_diameters : np.array
        shuffled axons diamters
    axons_type      : np.array
        corrresponding axons type
    """
    shuffle_mask = np.random.permutation(len(axons_diameters))
    axons_diameters = axons_diameters[shuffle_mask]
    axons_type = axons_type[shuffle_mask]
    return axons_diameters, axons_type

def save_axon_population(f_name, axons_diameters, axons_type, comment=None):
    """
    Save an axonal population to a file

    Parameters
    ----------
    f_name          : str
        name of the file to store the population
    axons_diameters : np.array
        array containing the axons diameters
    axons_type      : np.array
        array containing the axons type ('1' for myelinated, '0' for unmyelinated)
    comment         : str
        comment added in the header of the file, optional
    """
    f = open(f_name, 'w')
    if comment is not None:
        line = '# ' + comment
        f.write(line)
    for k in range(len(axons_diameters)):
        line = str(axons_diameters[k]) + ', ' + str(axons_type[k]) + '\n'
        f.write(line)
    f.close()

def load_axon_population(f_name):
    """
    Load a population from a file

    Parameters
    ----------
    f_name          : str
        name of the file where the population is stored

    Returns
    -------
    axons_diameters     : np.array
        Array containing all the diameters of the generated axon population
    axons_type          : np.array
        Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
    M_diam_list         : np.array
        list of myelinated only diameters
    U_diam_list         : np.array
        list of unmyelinated only diamters
    """
    population_file = np.genfromtxt(f_name, delimiter=',', comments='#')
    axons_diameters = population_file[:, 0]
    axons_type = population_file[:, 1]
    ind_myel = np.argwhere(axons_type == 1)
    ind_unmyel = np.argwhere(axons_type == 0)
    M_diam_list = axons_diameters[ind_myel]
    U_diam_list = axons_diameters[ind_unmyel]
    return axons_diameters, axons_type, M_diam_list, U_diam_list

#############################################
#############################################
#############################################
def axon_packer(diameters, Delta=0, y_gc=0, z_gc=0, max_iter=20000, probe=100, monitor=False,\
    monitoring_Folder='', monitoring_Niter=100, v_att=0.01, v_rep=0.1):
    """
    Axon Packing algorithm: this operation takes a vector of diameter (random population) and places it at best. The used algorithm is largely based on [1]

    Parameters
    ----------
    diameters           : np.array
        Array containing all the diameters of the axon population to pack
    Delta               : float
        minimal inter-axon distance to respect before considering collision, in um
    y_gc                : float
        y coordinate of the gravity center for the packing, in um
    z_gc                : float
        z coordinate of the gravity center for the packing, in um
    max_iter            : int
        Max. number of iterations
    probe               : int
        Number of iterations between two Fiber Volume Fraction probing
    monitor             : bool
        if True, the packing process will be monitored and some steps are plotted and saved
    monitoring_Folder   : str
        in case of monitoring, folder where the images of the packing process are stored
    monitoring_Niter    : str
        in case of monitoring, number of iterations between two monitoring images
    v_att               : float
        vector norm for attraction velocity, in um per iteration
    v_rep               : float
        vector norm for repulsion velocity, in um per iteration

    Returns
    -------
    y_axons         : np.array
        Array containing the y coordinates of axons, in um
    z_axons         : np.array
        Array containing the z coordinates of axons, in um
    iteration       : int
        number of iterations performed
    FVF             : np.array
        probed values for the Fiber Volume Fraction
    probed_iter     : np.array
        index of the FVF probed iterations

    Note
    ----
    - scientific reference
        [1] Mingasson, T., Duval, T., Stikov, N., and Cohen-Adad, J. (2017). AxonPacking: an open-source software to simulate arrangements of axons in white matter. Frontiers in neuroinformatics, 11, 5.
    - dev Note
        the algorithm perform a fixed number of iteration, the code could evoluate to tke into account the FVF convergence, however this value depends on the range on number of axons.
    """
    N = len(diameters)
    max_diam = max(diameters)
    ##########
    ## INIT ##
    ##########
    ### create an initial square grid with the population of axons
    N_init = int(math.ceil(np.sqrt(N))**2)
    N_side = int(np.sqrt(N_init))
    size_init = np.sqrt(N_init*(max_diam+Delta)**2)
    placement_vector = np.linspace(-((size_init/2) - (size_init/(2*N_side))), ((size_init/2) -\
        (size_init/(2*N_side))), num=N_side, endpoint=True)
    y_axons = np.tile(placement_vector, N_side) + y_gc
    z_axons = np.repeat(placement_vector, N_side) + z_gc
    ### remove unwanted places
    N_remove = N_init - N
    ind_to_delete = np.random.choice(len(y_axons), size=N_remove, replace=False)
    y_axons = np.delete(y_axons, ind_to_delete)
    z_axons = np.delete(z_axons, ind_to_delete)
    ### compute total total fiber surface and evaluate surface for FVF computation
    ax_areas = np.power(diameters/2, 2)*np.pi
    A_axons = np.sum(ax_areas)
    size_monitor_square = np.sqrt(A_axons*1.4)
    monitor_area = A_axons*1.4
    FVF = []
    probed_iter = []
    if fg_verbose:
        pass_info('Axon Packer: initial grid computed...')
    if monitor:
        plot_situation(diameters, y_axons, z_axons, size_init, title='Init', y_gc=y_gc, z_gc=z_gc)
        f_name = monitoring_Folder + 'Packer_0.png'
        plt.savefig(f_name)
        plt.close()
    ################
    ## ITERATIONS ##
    ################
    if fg_verbose:
        pass_info('Axon Packer: Begining iterations')
    iteration = 0
    while iteration < max_iter:
        iteration += 1
        if fg_verbose:
            progression_popup(iteration-1, max_iter, begin_message='\t iteration ', endl="\r")
            #print('\t iteration ' + f"{iteration}" + '/' + str(max_iter), end="\r")
        # compute P matrix
        P = compute_P_matrix(diameters, y_axons, z_axons, Delta, N)
        #P = compute_P_fast(diameters, y_axons, z_axons, Delta)
        # check overlap
        colapse = np.argwhere(P < 0)
        all_colapsed_ind = np.unique(colapse)
        # compute velocity, initialy consider that all velocities are attraction
        v_y, v_z = compute_attraction_velocities(y_axons, z_axons, y_gc, z_gc, N, v_att)
        #### prevent from division by 0 in the upper line
        np.nan_to_num(v_y, copy=False, nan=0.0)
        np.nan_to_num(v_z, copy=False, nan=0.0)
        v_y[all_colapsed_ind] = 0                   # neutralize velocity where should be repulsion
        v_z[all_colapsed_ind] = 0                   # same
        # compute velocities for colapsing cases
        v_y, v_z = handle_collisions(y_axons, z_axons, v_y, v_z, all_colapsed_ind, colapse, v_rep)
        # compute new positions
        y_axons, z_axons = update_positions(y_axons, z_axons, v_y, v_z)
        # compute FVF
        if iteration%probe == 0:
            # removing axons too much to the left
            ax_left_pts = y_axons - diameters/2
            FVF_mask = np.argwhere(ax_left_pts > (-size_monitor_square/2 + y_gc))
            # removing axons too much to the right
            ax_right_pts = y_axons + diameters/2
            FVF_mask = np.intersect1d(FVF_mask, np.argwhere(ax_right_pts < \
                (size_monitor_square/2 + y_gc)))
            # removing the axons that are too high
            ax_up_pts = z_axons + diameters/2
            FVF_mask = np.intersect1d(FVF_mask, np.argwhere(ax_up_pts < \
                (size_monitor_square/2 + z_gc)))
            # removing the axons that are too low
            ax_down_pts = z_axons - diameters/2
            FVF_mask = np.intersect1d(FVF_mask, np.argwhere(ax_down_pts > \
                (-size_monitor_square/2 + z_gc)))
            FVF.append(np.sum(ax_areas[FVF_mask])/monitor_area)
            probed_iter.append(iteration)
        # monitoring
        if ((iteration) % monitoring_Niter == 0 and monitor):
            plot_situation(diameters, y_axons, z_axons, size_init, \
                title=str(iteration)+' Iterations', y_gc=y_gc, z_gc=z_gc)
            f_name = monitoring_Folder + 'Packer_' + str(iteration) + '.png'
            plt.savefig(f_name)
            plt.close()
    pass_info('Axon Packer: Iterations done')
    if monitor:
        plot_situation(diameters, y_axons, z_axons, size_init, \
            title=str(iteration)+' Iterations', y_gc=y_gc, z_gc=z_gc)
        f_name = monitoring_Folder + 'Packer_final.png'
        plt.savefig(f_name)
        plt.close()
    return y_axons, z_axons, iteration, np.asarray(FVF), np.asarray(probed_iter)

@numba.jit(fastmath=True, cache=True)
def compute_attraction_velocities(y_axons, z_axons, y_gc, z_gc, N, v_att):
    """
    Computes attraction velocity for axon packing. Just in time compiled to speed up. For internal use only.
    """
    dy = np.ones(N)* y_gc - y_axons
    dz = np.ones(N)* z_gc - z_axons
    dist = np.sqrt((y_axons - y_gc)**2 + (z_axons - z_gc)**2)
    v_y = v_att * dy/dist
    v_z = v_att * dz/dist   # same
    return v_y, v_z

@numba.njit(fastmath=True, cache=True)
def compute_P_matrix(diameters, y_axons, z_axons, Delta, N):
    """
    Computes the proximity matrix for axon packing. Just in time compiled to speed up. For internal use only.
    """
    P = np.zeros((N, N))
    for i in range(N):
        for j in range(i+1, N):
            #P[i, j] = np.sqrt((y_axons[i] - y_axons[j])**2 + (z_axons[i] - z_axons[j])**2) -\
            # ((diameters[i] + diameters[j])/2 + Delta)
            # not hmogeneous to a distance, but work the same at the end and one square root less to compute...
            P[i, j] = ((y_axons[i] - y_axons[j])**2 + (z_axons[i] - z_axons[j])**2) -\
                ((diameters[i] + diameters[j])/2 + Delta)**2
    return P

def compute_P_fast(diameters, y_axons, z_axons, Delta):
    """
    Compyte the proximity matrix for axon packing. Based on numpy and scipy. Slower (just a bit) than JIT version on dev. For internal use only
    """
    points = np.column_stack((y_axons, z_axons))
    N = len(diameters)
    diams = np.tile(diameters, (N, 1))
    #diams = diameters.repeat(N).reshape((-1, N))
    P = spatial.distance.cdist(points, points, 'euclidean') - ((diams + np.transpose(diams))*(1/2)\
        + np.ones((N, N))*Delta)
    np.fill_diagonal(P, 0)
    return np.triu(P)

@numba.njit(fastmath=True, cache=True)
def handle_collisions(y_axons, z_axons, v_y, v_z, all_colapsed_ind, colapse, v_rep):
    """
    Handle collisions between axons for axon packing. Just in time compiled (doble loop...). For internal use only.
    """
    for k in all_colapsed_ind:
        sum_y = 0
        sum_z = 0
        for i in range(len(colapse)):
            duplet = colapse[i]
            if k == duplet[0]:
                sum_y += y_axons[k] - y_axons[duplet[1]]
                sum_z += z_axons[k] - z_axons[duplet[1]]
            elif k == duplet[1]:
                sum_y += y_axons[k] - y_axons[duplet[0]]
                sum_z += z_axons[k] - z_axons[duplet[0]]
        v_y[k] = v_rep * (sum_y / (np.sqrt(sum_y**2 + sum_z**2)))
        v_z[k] = v_rep * (sum_z / (np.sqrt(sum_y**2 + sum_z**2)))
    return v_y, v_z

@numba.njit(fastmath=True, cache=True)
def update_positions(y_axons, z_axons, v_y, v_z):
    """
    Compute new positions considering velicities for axon packing. Just in time compiled to speed up. For internal use only.
    """
    return y_axons + v_y, z_axons + v_z

def delete_collisions(axons_diameters, axons_type, y_axons, z_axons, Delta=0):
    """
    Delete collision cases in a placed population. In case of a detected collision, the axon or smaller diameter is removed.

    Parameters
    ----------
    axons_diameters : np.array
        array containing the axons diameters
    axons_type      : np.array
        array containing the axons type ('1' for myelinated, '0' for unmyelinated)
    y_axons         : np.array
        y coordinate of the axons to store, in um
    z_axons         : np.array
        z coordinate of the axons to store, in um
    Delta           : float
        space between axon fibers under which collision is considered, in um

    Returns
    -------
    new_axons_diameters : np.array
        array containing the axons diameters without collisions
    new_axons_type      : np.array
        array containing the axons type ('1' for myelinated, '0' for unmyelinated)
    new_y_axons     : np.array
        y coordinate of the axons to store, in um
    new_z_axons     : np.array
        z coordinate of the axons to store, in um
    """
    N = len(axons_diameters)
    P = compute_P_matrix(axons_diameters, y_axons, z_axons, Delta, N)
    colapse = np.argwhere(P < 0)
    flag_Collision = (colapse.size != 0)

    while flag_Collision:
        # checking which axons to delete
        ind_to_delete = []
        handled_collisions = []
        for collision in colapse:
            if (collision[0] not in handled_collisions) and (collision[1] not in handled_collisions):
                handled_collisions.append(collision[0])
                handled_collisions.append(collision[1])
                if axons_diameters[collision[0]] < axons_diameters[collision[1]]:
                    ind_to_delete.append(collision[0])
                else:
                    ind_to_delete.append(collision[1])
        # deleting problematic axons
        mask = np.ones(N, dtype=bool)
        mask[ind_to_delete] = False
        axons_diameters = axons_diameters[mask]
        axons_type = axons_type[mask]
        y_axons = y_axons[mask]
        z_axons = z_axons[mask]
        N = len(axons_diameters)
        # check if there are remaing collisions
        P = compute_P_matrix(axons_diameters, y_axons, z_axons, Delta, N)
        colapse = np.argwhere(P < 0)
        flag_Collision = (colapse.size != 0)

    return axons_diameters, axons_type, y_axons, z_axons


def plot_situation(diameters, y_axons, z_axons, size, title=None, y_gc=0, z_gc=0):
    """
    Discplay a population of axons. Doesn't return but declares a matplotlib figure

    Parameters
    ----------
    diameters   : np.array
        diamters of the axons to display, in um
    y_axons     : np.array
        y coordinate of the axons to display, in um
    z_axons     : np.array
        z coordinate of the axons to display, in um
    size        : float
        size of the window as a square side, in um
    title       : str
        title of the figure
    y_gc        : float
        y coordinate of the gravity, in um
    z_gc        : float
        z coordinate of the gravity, in um
    """
    circles = []
    for k in range(len(diameters)):
        circles.append(plt.Circle((y_axons[k], z_axons[k]), diameters[k]/2, color='r', fill=False))
    fig, ax = plt.subplots(figsize=(8, 8))
    for circle in circles:
        ax.add_patch(circle)
    if title is not None:
        plt.title(title)
    plt.xlim(-size/2 + y_gc, size/2 + y_gc)
    plt.ylim(-size/2 + z_gc, size/2 + z_gc)

def save_placed_axon_population(f_name, axons_diameters, axons_type, y_axons, z_axons,\
    comment=None):
    """
    Save a placed axonal population to a file

    Parameters
    ----------
    f_name          : str
        name of the file to store the population
    axons_diameters : np.array
        array containing the axons diameters
    axons_type      : np.array
        array containing the axons type ('1' for myelinated, '0' for unmyelinated)
    y_axons     : np.array
        y coordinate of the axons to store, in um
    z_axons     : np.array
        z coordinate of the axons to store, in um
    comment         : str
        comment added in the header of the file, optional
    """
    f = open(f_name, 'w')
    if comment is not None:
        line = '# '+comment
        f.write(line)
    for k in range(len(axons_diameters)):
        line = str(axons_diameters[k]) + ', ' + str(axons_type[k]) + ', ' + str(y_axons[k]) +\
            ', ' + str(z_axons[k]) +'\n'
        f.write(line)
    f.close()

def load_placed_axon_population(f_name):
    """
    Load a placed population from a file

    Parameters
    ----------
    f_name          : str
        name of the file where the population is stored

    Returns
    -------
    axons_diameters     : np.array
        Array containing all the diameters of the generated axon population
    axons_type          : np.array
        Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'
    y_axons     : np.array
        y coordinate of the axons, in um
    z_axons     : np.array
        z coordinate of the axons, in um
    M_diam_list         : np.array
        list of myelinated only diameters
    U_diam_list         : np.array
        list of unmyelinated only diamters
    """
    population_file = np.genfromtxt(f_name, delimiter=',', comments='#')
    axons_diameters = population_file[:, 0]
    axons_type = population_file[:, 1]
    y_axons = population_file[:, 2]
    z_axons = population_file[:, 3]
    ind_myel = np.argwhere(axons_type == 1)
    ind_unmyel = np.argwhere(axons_type == 0)
    M_diam_list = axons_diameters[ind_myel]
    U_diam_list = axons_diameters[ind_unmyel]
    return axons_diameters, axons_type, y_axons, z_axons, M_diam_list, U_diam_list
