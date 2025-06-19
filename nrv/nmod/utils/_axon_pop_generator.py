"""
Axon population generator usefull functions.
"""

import faulthandler
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import rv_continuous, gamma

from ...backend._log_interface import pass_info, progression_popup, rise_warning
from ...backend._parameters import parameters

# WARNING:
# no prompt message for numpy division by zeros: handled in the code !!!
np.seterr(divide="ignore", invalid="ignore")

# verbosity level
fg_verbose = True

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()

# get the built-in material librairy
dir_path = parameters.nrv_path + "/_misc"
stat_library = os.listdir(dir_path + "/stats/")

#################################################
## Nerve composition statistics and generators ##
#################################################
myelinated_stats = [
    "Schellens_1",
    "Schellens_2",
    "Ochoa_M",
    "Jacobs_9_A",
    "Jacobs_9_B",
    "Jacobs_9_C",
    "Jacobs_9_D",
]
unmyelinated_stats = [
    "Ochoa_U",
    "Jacobs_11_A",
    "Jacobs_11_B",
    "Jacobs_11_C",
    "Jacobs_11_D",
]


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
    f_in_librairy = str(stat_name) + ".csv"
    if f_in_librairy in stat_library:
        stat_file = np.genfromtxt(dir_path + "/stats/" + f_in_librairy, delimiter=",")
    else:
        # stat_file = np.genfromtxt(dir_path + "/stats/" + f_in_librairy, delimiter=",")
        stat_file = np.genfromtxt(f_in_librairy, delimiter=",")
    diameters = stat_file[:, 0]
    presence = stat_file[:, 1]
    return diameters, presence


def get_stat_expected(fname:str)->float:
    """
    Get expected value from a stat stored in a file

    Parameters
    ----------
    fname : str
        name of the statistic in the librairy or path to a new librairy in csv

    Returns
    -------
    float
    """
    diameters, presence = load_stat(fname)
    return np.mean(diameters*presence)


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
    return c1 * (gamma.pdf(x, a1, scale=1 / beta1, loc=0.2))


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
    return c1 * (gamma.pdf(x, a1, scale=1 / beta1, loc=2)) + c2 * (
        gamma.pdf(x, a2, scale=1 / beta2, loc=transition)
    )


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
        return self.c1 * (gamma.pdf(x, self.a1, scale=1 / self.beta1, loc=0.2))


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
        return self.c1 * (
            gamma.pdf(x, self.a1, scale=1 / self.beta1, loc=2)
        ) + self.c2 * (gamma.pdf(x, self.a2, scale=1 / self.beta2, loc=self.transition))


def create_generator_from_stat(
    stat, myelinated=True, dmin=None, dmax=None, one_gamma: bool = False
):
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
    one_gamma    : bool
        If true, the stat generator is forced to one gamma only

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
    if myelinated and dmax > 10 and not one_gamma:
        popt1, pcov1 = curve_fit(
            two_Gamma,
            xdata=diameters,
            ydata=presence,
            bounds=(
                [1, 2, 0, 1, 0, 0, 2],
                [np.inf, 15, np.inf, np.inf, 15, np.inf, 14],
            ),
        )
        generator = nerve_gen_two_gamma()
        generator.set_bounds(dmin, dmax)
        generator.configure(*popt1)
    else:
        popt1, pcov1 = curve_fit(
            one_Gamma,
            xdata=diameters,
            ydata=presence,
            bounds=([1, 0, 0], [np.inf, 10, np.inf]),
        )
        generator = nerve_gen_one_gamma()
        generator.set_bounds(dmin, dmax)
        generator.configure(*popt1)
    return generator, popt1, pcov1


def create_axon_population(
    N, percent_unmyel=0.7, M_stat="Schellens_1", U_stat="Ochoa_U"
):
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
    U = int(N * percent_unmyel)
    M = N - U
    pass_info(
        "On "
        + str(N)
        + " axons to generate, there are "
        + str(M)
        + " Myelinated and "
        + str(U)
        + " Unmyelinated"
    )
    # generate the myelinated axons
    xspace1 = np.linspace(1, 20, num=500)
    if len(M_popt) < 4:
        data = one_Gamma(xspace1, *M_popt)
    else:
        data = two_Gamma(xspace1, *M_popt)
    data = data / np.sum(data)
    M_diam_list = np.random.choice(xspace1, M, p=data)
    M_type = np.ones(M)

    # generate the unmyelinated axons
    xspace1 = np.linspace(0.1, 3, num=500)
    data = one_Gamma(xspace1, *U_popt)
    data = data / np.sum(data)
    U_diam_list = np.random.choice(xspace1, U, p=data)
    U_type = np.zeros(U)

    shuffle_mask = np.random.permutation(N)
    axons_diameters = np.concatenate((M_diam_list, U_diam_list))
    axons_type = np.concatenate((M_type, U_type))
    axons_diameters = axons_diameters[shuffle_mask]
    axons_type = axons_type[shuffle_mask]
    return axons_diameters, axons_type, M_diam_list, U_diam_list


def fill_area_with_axons(
    A, percent_unmyel=0.7, FVF=0.55, M_stat="Schellens_1", U_stat="Ochoa_U"
):
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
    M_max_diam_value = M_gen.b - 0.01 * (M_gen.b - M_gen.a)
    U_gen, U_popt, U_pcov = create_generator_from_stat(U_stat)
    U_diam_list = []
    U_max_diam_value = U_gen.b - 0.01 * (U_gen.b - U_gen.a)
    # area
    A_ax = 0
    A_total = 0
    # axon lists
    M_diam_list = []
    U_diam_list = []
    # loop
    while A_total < A:
        filled = A_total / A
        progression_popup(
            round(filled * 100), 100, begin_message="\t Area filled at ", endl="\r"
        )
        # print('\t Area filled at ' + f"{round(filled*100)}" + ' percent', end="\r")
        U_or_M = np.random.uniform(0, 1)
        if U_or_M < percent_unmyel:
            # generate a unmyelinated axon
            prov_diam = U_gen.rvs(1, size=1)[0]
            while prov_diam > U_max_diam_value:
                prov_diam = U_gen.rvs(1, size=1)[0]
            U_diam_list.append(prov_diam)
            A_ax += np.power(U_diam_list[-1] / 2, 2) * np.pi
        else:
            prov_diam = M_gen.rvs(1, size=1)[0]
            while prov_diam > M_max_diam_value:
                prov_diam = M_gen.rvs(1, size=1)[0]
            M_diam_list.append(prov_diam)
            A_ax += np.power(M_diam_list[-1] / 2, 2) * np.pi
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



def plot_population(
    diameters, y_axons, z_axons, ax, size, axon_type=None, y_gc=0, z_gc=0
) -> None:
    """
    Display a population of axons.

    Parameters
    ----------
    diameters   : np.array
        diamters of the axons to display, in um
    y_axons     : np.array
        y coordinate of the axons to display, in um
    z_axons     : np.array
        z coordinate of the axons to display, in um
    ax          : matplotlib.axes
        (sub-) plot of the matplotlib figure
    size        : float
        size of the window as a square side, in um
    axon_type   : np.array
        type of the axon (Myelinated = 1; Unmyelinated = 0) - Optionnal
    title       : str
        title of the figure
    y_gc        : float
        y coordinate of the gravity, in um
    z_gc        : float
        z coordinate of the gravity, in um
    """
    if axon_type is None:
        for k in range(len(diameters)):
            ax.add_patch(
                plt.Circle(
                    (y_axons[k], z_axons[k]), diameters[k] / 2, color="r", fill=True
                )
            )
    else:
        # plot the final results, with distinction between un- and myelinated axons
        myelinated_mask = np.argwhere(axon_type == 1)
        y_myelinated = y_axons[myelinated_mask]
        z_myelinated = z_axons[myelinated_mask]
        M_diam_list = diameters[myelinated_mask]
        for k in range(len(y_myelinated)):
            ax.add_patch(
                plt.Circle(
                    (y_myelinated[k], z_myelinated[k]),
                    M_diam_list[k] / 2,
                    color="r",
                    fill=True,
                )
            )

        unmyelinated_mask = np.argwhere(axon_type == 0)
        y_unmyelinated = y_axons[unmyelinated_mask]
        z_unmyelinated = z_axons[unmyelinated_mask]
        U_diam_list = diameters[unmyelinated_mask]
        for k in range(len(y_unmyelinated)):
            ax.add_patch(
                plt.Circle(
                    (y_unmyelinated[k], z_unmyelinated[k]),
                    U_diam_list[k] / 2,
                    color="b",
                    fill=True,
                )
            )

    ax.set_xlim(-size / 2 + y_gc, size / 2 + y_gc)
    ax.set_ylim(-size / 2 + z_gc, size / 2 + z_gc)


def save_axon_population(
    f_name, axons_diameters, axons_type, y_axons=None, z_axons=None, comment=None
):
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
    if y_axons is None:
        y_axons = np.zeros([len(axons_diameters)])
        y_axons[:] = np.nan

    if z_axons is None:
        z_axons = np.zeros([len(axons_diameters)])
        z_axons[:] = np.nan

    f = open(f_name, "w")
    if comment is not None:
        line = "# " + comment
        f.write(line)
    for k in range(len(axons_diameters)):
        line = (
            str(axons_diameters[k])
            + ", "
            + str(axons_type[k])
            + ", "
            + str(y_axons[k])
            + ", "
            + str(z_axons[k])
            + "\n"
        )
        f.write(line)
    f.close()


def load_axon_population(f_name):
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
    population_file = np.genfromtxt(f_name, delimiter=",", comments="#")
    axons_diameters = population_file[:, 0]
    axons_type = population_file[:, 1]
    y_axons = population_file[:, 2]
    z_axons = population_file[:, 3]
    ind_myel = np.argwhere(axons_type == 1)
    ind_unmyel = np.argwhere(axons_type == 0)
    M_diam_list = axons_diameters[ind_myel]
    U_diam_list = axons_diameters[ind_unmyel]

    if np.isnan(y_axons).all() or np.isnan(z_axons).all():
        rise_warning("Loaded population has no y,z coordinates.")

    return axons_diameters, axons_type, M_diam_list, U_diam_list, y_axons, z_axons
