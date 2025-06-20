import numpy as np
from typing import Iterable
from itertools import combinations
from rich.progress import track
import matplotlib.pyplot as plt

from ._axon_pop_generator import plot_population
from ...utils.geom import Circle, overlap_checker
from ...utils.geom._cshape import CShape
from ...backend._log_interface import rise_warning, pass_info

# ---- #
# misc #
# ---- #
def dist_matrix(X:tuple[np.ndarray, np.ndarray, np.ndarray])->np.ndarray:
    """
    Get a matrix containing the distance of three array containg the position and radius of various circles. 

    Note
    ----
    For `n` circles the matrix return is of dimension `(n,n)` and the index (i,j) contains the distance between the ith and jth circles.

    Tip
    ---
    By definition, the returned matrix is symetric and with a zero diagonal.


    Parameters
    ----------
    X : tuple[np.ndarray, np.ndarray, np.ndarray]
        Tuple of 1D-``ndarray`` of same lengh containing the respectively: 
            - the y position of each circle
            - the z position of each circle
            - the radius of each circle

    Returns
    -------
    np.ndarray
    """
    return ((X[0][:, np.newaxis] - X[0])**2 + (X[1][:, np.newaxis] - X[1])**2)**0.5 - (X[2][:, np.newaxis] + X[2])

def get_ppop_info(y, z, r, verbose=False, with_all_dist=False):
    _info = {}
    all_dist = dist_matrix((y, z, r))
    if with_all_dist:
        _info["all_dist"]
    n = all_dist.shape[0]
    i_n = np.identity(n, dtype=bool)
    all_dist[i_n] = np.nan

    _info["n"] = n
    _info["min_dist"] = np.nanmin(all_dist)
    _info["avg_min_dist"] = np.nanmin(all_dist, axis=1).mean()
    _info["avg_max_dist"] = np.nanmin(all_dist, axis=1).max()
    _info["outer_box"] = (np.min(y), np.min(z)), (np.max(y), np.max(z))
    if verbose:
        pass_info(f"minimal distance: {_info["min_dist"]}")
        pass_info(f"average minimal distance: {_info["avg_min_dist"]}")
        pass_info(f"Maximal minimal distance: {_info["avg_max_dist"]}")
        pass_info(f"Outer box: {_info["outer_box"]}")
    return _info


# ----------- #
# Axon Placer #
# ----------- #
class Placer:
    """A class for drawing circles-inside-a-circle."""
    def __init__(self, geom:CShape|None=None, delta:float=.01, delta_trace:float|None=None, delta_in:float|None=None, n_iter:int=500, radius:float=250, rho_min:float=0.005, rho_max:float=0.05):
        """Initialize the Circles object.

        R is the radius of the large circle within which the small circles are
        to fit.
        n is the maximum number of circles to pack inside the large circle.
        rho_min is rmin/R, giving the minimum packing circle radius.
        rho_max is rmax/R, giving the maximum packing circle radius.
        """
        if geom is not None:
            self.geom = geom
        else:
            self.geom = Circle(center=(0,0), radius=radius)
        # The centre of the canvas
        self.rmin, self.rmax = radius * rho_min, radius * rho_max
        self.delta_in = delta
        self.delta_trace = delta
        if delta_in is not None:
            self.delta_in = delta_in
        if delta_trace is not None:
            self.delta_trace = delta_trace

        self.n_iter = n_iter

    def _place_circle(self, r, first=False):
        # The guard number: if we don't place a circle within this number
        # of trials, we give up.
        for _ in range(self.n_iter):
            # Pick a random position, uniformly on the larger circle's interior
            X = self.geom.get_point_inside(1, delta=r+self.delta_trace)
            if first:
                return X, True
            if not any(overlap_checker(c=X, r=r, c_comp=self.pos[self.placed,:],r_comp=self.r[self.placed], delta=self.delta_in)):
                return X, True
        # for this circle.
        # pass_info('guard reached.')
        return np.zeros(2) , False

    def place_all(self, r:int|Iterable):
        """Place the little circles inside the big one."""
        
        # First choose a set of n random radii and sort them. We use
        if isinstance(r, int):
            self.n = r
            r = self.rmin + (self.rmax - self.rmin) * np.random.random(self.n)
        else:
            self.n = len(r)

        # Sort the radii to start by placing the larger radius (more difficult to place)
        ir_s = np.argsort(r)[::-1]
        ir_rs = np.argsort(ir_s)
        r[::-1].sort()
        self.r = r

        self.pos = np.zeros((self.n,2))
        self.placed = np.zeros((self.n), dtype=bool)
        # Do our best to place the circles, larger ones first.
        self.pos[0,:], self.placed[0] = self._place_circle(self.r[0], first=True)
        for i in track(range(1, self.n)):
            self.pos[i,:], self.placed[i] = self._place_circle(self.r[i])
        # return 2*r, y, z
        if not self.placed.all():
            pass_info(np.sum(~self.placed), "axons not placed")
        return self.r[ir_rs], self.pos[ir_rs,0], self.pos[ir_rs,1], self.placed[ir_rs]



# ----------- #
# Axon Packer #
# ----------- #
def init_packing(
    diam: np.ndarray,
    delta: np.float32,
    y_gc: np.float32,
    z_gc: np.float32,
) -> np.array:
    """
    Initialize Axon packing Algorithm - Internal use Only
    """
    Naxon = len(diam)
    ids = np.arange(Naxon)  # get IDs of each axons
    max_diam = np.max(diam)  # get max axon diameter

    # Vector of initial velocity
    velocity = np.zeros([2, Naxon])

    ### create an initial square grid with the population of axons
    N_init = np.int32(np.ceil(np.sqrt(Naxon)) ** 2)
    N_side = np.int32(np.sqrt(N_init))
    size_init = np.sqrt(N_init * (max_diam + delta) ** 2)
    grid_size = (size_init / 2) - (size_init / (2 * N_side))
    grid = np.linspace(-grid_size, grid_size, num=N_side, endpoint=True)
    y_axons = np.tile(grid, N_side) + y_gc
    z_axons = np.repeat(grid, N_side) + z_gc

    ### remove unwanted places
    N_remove = N_init - Naxon
    ind_to_delete = np.random.choice(len(y_axons), size=N_remove, replace=False)
    y_axons = np.delete(y_axons, ind_to_delete)
    z_axons = np.delete(z_axons, ind_to_delete)

    # Define position vector:
    pos = np.array([y_axons, z_axons])

    # Position of center of gravity
    gc = np.array([y_gc, z_gc])

    return (pos, velocity, gc, ids)


def get_axon_combinaisons(ids: np.ndarray) -> np.array:
    """
    get all possible combinaison of axons IDs = n(n-1)/2 - Internal use only
    """
    return np.asarray(list(combinations(ids, 2)))


def get_axon_other_id(ids: np.ndarray) -> np.array:
    """
    For each axon, get ids all other axon: N*(N-1) - Internal use only
    """
    Nax = len(ids)
    return np.asarray(list(combinations(ids, Nax - 1)))


"""def get_axon_interdistance(
        pos: np.ndarray,
        ids_pairs: np.ndarray
    )-> np.array:
    
    Compute the distance between each pair of axons - Internal use only
    @Note: The sqrt could probably be omitted  to increase speed
    
    #get the pairs of y and z positions of all axons
    y_pairs = np.array([pos[0][ids_pairs[:,0]], pos[0][ids_pairs[:,1]]]).T  #we get the y,z position of each combinaison
    z_pairs = np.array([pos[1][ids_pairs[:,0]], pos[1][ids_pairs[:,1]]]).T
    #we get the dy and dz combinaison 
    dy_pairs = np.diff(y_pairs, axis=1).ravel()
    dz_pairs = np.diff(z_pairs, axis=1).ravel()
    #We return the position.
    return(np.sqrt(dz_pairs**2 + dy_pairs**2))"""


def get_axon_inter_radius(diam: np.ndarray, ids_pairs: np.ndarray) -> np.array:
    """
    return the inter-radis of each pair of axons - Internal use only
    """
    diam_pair = np.array(
        [diam[ids_pairs[:, 0]], diam[ids_pairs[:, 1]]]
    ).T  # we get the diameter of each combinaison
    return np.abs(np.sum(diam_pair, axis=1).ravel()) / 2


def get_delta_pairs(pos: np.ndarray, ids_pairs: np.ndarray) -> np.array:
    """
    Evaluate the (z,y) distance of each axons pairs
    """
    return np.diff(
        np.array([pos[ids_pairs[:, 0]], pos[ids_pairs[:, 1]]]).T, axis=1
    ).ravel()


def get_deltad_pairs(pos: np.ndarray, ids_pairs: np.ndarray) -> np.array:
    """
    Evaluate the eucledian distance coordinate of each axons pairs - Internal use only
    @Note: The sqrt could probably be omitted to increase speed
    """
    return np.sqrt(
        get_delta_pairs(pos[0], ids_pairs) ** 2
        + get_delta_pairs(pos[1], ids_pairs) ** 2
    )


def get_gravity_dr(pos: np.ndarray, gc: np.ndarray, Naxons: np.int32) -> np.array:
    """
    Evaluate the (z,y) distance to the gravity center of each axons - Internal use only
    """
    return (np.ones([2, Naxons]).T * gc).T - pos


def get_gravity_dist(pos: np.ndarray, gc: np.ndarray, Naxons: np.int32) -> np.array:
    """
    Evaluate the eucledian distance to the gravity center of each axons - Internal use only
    @Note: The sqrt could probably be omitted to increase speed
    """
    return np.sqrt(
        np.sum((get_gravity_dr(pos, gc, Naxons).T - gc) ** 2, axis=1) + 1e-10
    )


def compute_attraction_v(
    pos: np.ndarray, gc: np.ndarray, Naxons: np.int32, v_att: np.float32
) -> np.array:
    """
    Evaluate the attraction velocity for every axons - Internal use only
    """
    return v_att * get_gravity_dr(pos, gc, Naxons) / get_gravity_dist(pos, gc, Naxons)


def compute_repulsion_v(pos1: np.ndarray, pos2: np.ndarray, v_rep: np.float32) -> np.array:
    """
    Evaluate the repulsion velocity for the colliding axons only - Internal use only
    """
    vnew = v_rep * (pos1 - pos2)
    return vnew, -vnew


def get_colliding_ids(
    pos: np.ndarray, id_pairs: np.ndarray, diam_pairs: np.ndarray, delta: np.float32
) -> np.array:
    """
    get ids of colliding axons - Internal use only
    """
    return id_pairs[get_deltad_pairs(pos, id_pairs) < (diam_pairs + delta)]


def get_distance_in_range(
    pos: np.ndarray, id_others: np.ndarray, diam: np.ndarray, delta: np.float32
) -> np.array:

    id = np.arange(len(pos[0]))
    id = np.flip(id)

    r_comb = (diam[id_others] + diam[id][:, None]) / 2

    y_dis = pos[0][id][:, None] - pos[0][id_others]
    x_dis = pos[1][id][:, None] - pos[1][id_others]
    dist = np.sqrt(y_dis**2 + x_dis**2) - r_comb

    stop_c = 1.2 * delta
    if stop_c < 1:
        stop_c = 1
    # low_bound = np.min(dist,axis = 1)>0.95*delta
    # up_bound = np.min(dist,axis = 1)<2*delta
    # pass_info(np.min(dist,axis = 1))
    # exit()
    return np.max(np.min(dist, axis=1)) < stop_c

    # pass_info(len(id_others[up_bound]))
    # exit()

    # if len(id_others[low_bound & up_bound]) == len(id):
    # if len(id_others[up_bound]) == len(id):
    #    return True
    # else:
    #    return False


def update_axon_packing(
    pos: np.ndarray,
    id_pairs: np.ndarray,
    diam_pairs: np.ndarray,
    gc: np.ndarray,
    v_att: np.float32,
    v_rep: np.float32,
    delta: np.float32,
    Naxon: np.int32,
) -> np.array:
    """
    Update the axon array position by 1 increment - Internal use only
    """

    velocity = compute_attraction_v(pos, gc, Naxon, v_att)
    ic = get_colliding_ids(pos, id_pairs, diam_pairs, delta)
    velocity[:, ic[:, 0]], velocity[:, ic[:, 1]] = compute_repulsion_v(
        pos[:, ic[:, 0]], pos[:, ic[:, 1]], v_rep
    )
    return pos + velocity


def axon_packer(
    diameters: np.ndarray,
    y_gc: np.float32 = 0,
    z_gc: np.float32 = 0,
    delta: np.float32 = 0.5,
    n_iter: np.int32 = 20000,
    v_att: np.float32 = 0.01,
    v_rep: np.float32 = 0.1,
    monitor=False,
    monitoring_Folder="",
    n_monitor=200,
):
    """
    Axon Packing algorithm: this operation takes a vector of diameter (random population) and places it at best. The used algorithm is largely based on [1]

    Parameters
    ----------
    diameters           : np.ndarray
        Array containing all the diameters of the axon population to pack
    delta               : float
        minimal inter-axon distance to respect before considering collision, in um
    n_iter            : int
        Number of iterations
    v_att               : float
        vector norm for attraction velocity, in um per iteration
    v_rep               : float
        vector norm for repulsion velocity, in um per iteration
    y_gc                : float
        y coordinate of the gravity center for the packing, in um
    z_gc                : float
        z coordinate of the gravity center for the packing, in um
    monitor             : bool
        monitor the packing algorithm by saving regularly plot of the population
    monitoring_Folder   : str
        where to save the monitoring plots
    n_monitor           : int
        number of iterration between two successive plots when monitoring the algorithm

    Returns
    -------
    y_axons         : np.ndarray
        Array containing the y coordinates of axons, in um
    z_axons         : np.ndarray
        Array containing the z coordinates of axons, in um

    Note
    ----
    - scientific reference
        [1] Mingasson, T., Duval, T., Stikov, N., and Cohen-Adad, J. (2017). AxonPacking: an open-source software to simulate arrangements of axons in white matter. Frontiers in neuroinformatics, 11, 5.
    - This algorithm cannot be parallelized for the moment.
    - dev Note
        the algorithm perform a fixed number of iteration, the code could evoluate to tke into account the FVF convergence, however this value depends on the range on number of axons.
    """
    pass_info("Axon packing initiated. This might take a while...")
    pos, velocity, gc, ids = init_packing(diameters, delta, y_gc, z_gc)
    max_pos = 2.2 * (np.max(pos[0]) - y_gc)
    id_pairs = get_axon_combinaisons(ids)
    diam_pair = get_axon_inter_radius(diameters, id_pairs)
    Naxon = len(pos[0])

    id_others = get_axon_other_id(ids)

    # for _ in track(range (n_iter)):
    #    pos = update_axon_packing(pos,id_pairs,diam_pair,gc,v_att,v_rep,delta,Naxon)
    if monitor:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_axis_off()
        fig.add_axes(ax)
    for i in track(range(n_iter)):
        pos = update_axon_packing(
            pos, id_pairs, diam_pair, gc, v_att, v_rep, delta, Naxon
        )

        if monitor and i % n_monitor == 0:
            y_prov = pos[0].copy()
            z_prov = pos[1].copy()
            ax.cla()
            plot_population(
                diameters, y_prov, z_prov, ax, max_pos, y_gc=y_gc, z_gc=z_gc
            )
            plt.savefig(monitoring_Folder + "vignette_" + str(i) + ".png")

        """
        if (get_distance_in_range(pos,id_others,diameters,delta)):
        #t.append(get_distance_in_range(pos,id_others,diameters,delta))
            pass_info("Stop criterion reached!")
            break
        """
    y_axons = pos[0].copy()
    z_axons = pos[1].copy()
    pass_info("Packing done!")
    y_c, z_c = get_barycenter(
        diameters, y_axons, z_axons
    )  # center the population back to 0,0
    return y_axons - y_c, z_axons - z_c


def expand_pop(y_axons: np.ndarray, z_axons: np.ndarray, factor: float) -> np.array:
    """
    Expand population of placed axons by a specified number

    Parameters
    ----------
    y_axons     : np.ndarray
        y coordinate of the axons, in um
    z_axons     : np.ndarray
        z coordinate of the axons, in um
    factor          : float
        expansion factor, unitless
    """
    if factor < 1:
        rise_warning("expansion factor must be greater than one. Factor set to 1")
        factor = 1
    return (y_axons * factor, z_axons * factor)


def remove_collision(
    axons_diameters: np.ndarray,
    y_axons: np.ndarray,
    z_axons: np.ndarray,
    axon_type: np.ndarray|None=None,
    delta: float = 0,
    return_mask:bool = False,
) -> np.array:
    """
    Remove collinding axons in a population

    Parameters
    ----------
    axons_diameters : np.ndarray
        array containing the axons diameters
    y_axons     : np.ndarray
        y coordinate of the axons to store, in um
    z_axons     : np.ndarray
        z coordinate of the axons to store, in um
    axon_type   : np.ndarray
        type of the axon (Myelinated = 1; Unmyelinated = 0)
    delta               : float
        minimal inter-axon distance to respect before considering collision, in um
    return_mask         : bool
        return, if True return only a mask with the valid axons.
    """

    Naxon = len(axons_diameters)
    ids = np.arange(Naxon)
    id_pairs = get_axon_combinaisons(ids)
    pos = np.zeros([2, Naxon])
    pos[0, :] = y_axons
    pos[1, :] = z_axons
    diam_pairs = get_axon_inter_radius(axons_diameters, id_pairs)
    ic = get_colliding_ids(pos, id_pairs, diam_pairs, delta)
    ic = ic[:, 0]
    if len(ic) > 0:
        rise_warning(f"{len(ic)} axon collisions detected - Axons discarded.")
    if not return_mask:
        return (
            np.delete(axons_diameters, ic),
            np.delete(y_axons, ic),
            np.delete(z_axons, ic),
            np.delete(axon_type, ic),
        )
    else:
        _ok = np.ones_like(axons_diameters, dtype=bool)
        _ok[ic] = False
        return _ok


def get_circular_contour(
    axons_diameters: np.ndarray, y_axons: np.ndarray, z_axons: np.ndarray, delta: float = 10
) -> float:
    """
    Get a circular contour diameter of the axon population

    Parameters
    ----------
    axons_diameters : np.ndarray
        array containing the axons diameters
    y_axons     : np.ndarray
        y coordinate of the axons to store, in um
    z_axons     : np.ndarray
        z coordinate of the axons to store, in um
    delta               : float
        distance between the contour and the closest axon, in um
    """
    dist_axon = np.sqrt((y_axons**2 + z_axons**2))
    dist_axon += axons_diameters / 2
    radius = np.max(dist_axon) + delta
    return radius * 2


def remove_outlier_axons(
    axons_diameters: np.ndarray,
    y_axons: np.ndarray,
    z_axons: np.ndarray,
    axon_type: np.ndarray|None=None,
    diameter: float = 10,
) -> np.array:
    """
    Remove axons in a population located outside a circular border, defined by its diameter

    Parameters
    ----------
    axons_diameters : np.ndarray
        array containing the axons diameters
    y_axons     : np.ndarray
        y coordinate of the axons to store, in um
    z_axons     : np.ndarray
        z coordinate of the axons to store, in um
    axon_type   : np.ndarray
        type of the axon (Myelinated = 1; Unmyelinated = 0)
    diameter               : float
        diameter of the circular border, in um
    """
    dist_axon = np.sqrt((y_axons**2 + z_axons**2))
    dist_axon += axons_diameters / 2
    inside_border = dist_axon <= diameter / 2
    n_remove = len(np.where(inside_border == False)[0])
    if n_remove > 0:
        rise_warning(f"{n_remove} outlier axons discarded.")

    return (
        axons_diameters[inside_border],
        y_axons[inside_border],
        z_axons[inside_border],
        axon_type[inside_border],
    )



def get_barycenter(axons_diameters, y_axons, z_axons):
    """
    Compute barycenter of the population

    Parameters
    ----------
    axons_diameters : np.ndarray
        array containing the axons diameters
    y_axons     : np.ndarray
        y coordinate of the axons to store, in um
    z_axons     : np.ndarray
        z coordinate of the axons to store, in um
    """
    diam_sum = np.sum(axons_diameters)
    return (
        np.sum(axons_diameters * y_axons) / diam_sum,
        np.sum(axons_diameters * z_axons) / diam_sum,
    )
