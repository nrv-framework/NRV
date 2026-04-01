import matplotlib.pyplot as plt
from .._CostFunctions import cost_function
import numpy as np

from ...backend._NRV_Results import NRV_results
from ...backend._log_interface import pass_info, rise_warning


class optim_results(NRV_results):
    """
    Container class storing optimization parameters, history, and best solution data.
    """

    def __init__(self, context=None):
        """
        Initialize an optimization-results container.

        Parameters
        ----------
        context : Any, optional
            Optimization-parameter context stored under ``optimization_parameters``.
        """
        super().__init__({"optimization_parameters": context})

    def load(self, data, blacklist=[], **kwargs):
        """
        Load optimization results and reserialize the nested optimization parameters.
        """
        super().load(data, blacklist, **kwargs)
        self["optimization_parameters"] = self["optimization_parameters"].save(
            save=False
        )

    ############################
    ##   Processing methods   ##
    ############################

    ## PSO relative methods
    def is_stabilized(self, part, it, threshold=0.1):
        """
        Check whether one particle velocity has fallen below a stabilization threshold.

        Parameters
        ----------
        part : int
            Particle identifier.
        it : int
            Iteration index.
        threshold : float, optional
            Absolute velocity threshold.

        Returns
        -------
        bool
            ``True`` when all velocity components are below the threshold.
        """
        velocity = self["velocity" + str(part)][it]
        for i in velocity:
            if abs(i) >= threshold:
                return False
        return True

    def stabilization_it(self, parts=None, nit=None, threshold=None):
        """
        Estimate the last iteration at which selected particles were not yet stabilized.

        Parameters
        ----------
        parts : int | iterable | None, optional
            Particle identifier, iterable of identifiers, or ``None`` for the whole swarm.
        nit : int | None, optional
            Number of iterations to inspect.
        threshold : float | None, optional
            Stabilization threshold. If omitted, derive it from particle 1 velocity history.

        Returns
        -------
        int | np.ndarray | None
            Stabilization iteration index or indices.
        """
        if threshold == None:
            threshold = max(max(self["velocity1"])) / 100
            pass_info("No threshold in parameters, set to Vpart1max/100 = ", threshold)

        # One particle
        if type(parts) == int:
            if nit is None:
                nit = self.nit
            for i in range(nit - 1, 0, -1):
                if not self.is_stabilized(parts, i, threshold):
                    return i
            return None

        # A particle list
        elif np.iterable(parts):
            list_it = []
            for i in parts:
                list_it += [
                    self.stabilization_it(parts=int(i), nit=nit, threshold=threshold)
                ]
            return np.array(list_it)

        # The whole swram
        else:
            swarm = 1 + np.arange(self["optimization_parameters"]["n_particles"])
            return self.stabilization_it(swarm, nit=nit, threshold=threshold)

    def add_filter(self, part_filter):
        """
        Apply a post-processing filter to every stored particle position.

        Parameters
        ----------
        part_filter : callable
            Filter applied to each position vector.

        Returns
        -------
        optim_results
            Updated results object.
        """
        n_particles = self["optimization_parameters"]["n_particles"]
        nit = self.nit
        resultsf = self
        for i in range(n_particles):
            resultsf["position" + str(i + 1) + " filtered"] = [[] for j in range(nit)]
            for j in range(nit):
                part = resultsf["position" + str(i + 1)][j]
                filtered_part = part_filter(part)
                resultsf["position" + str(i + 1) + " filtered"][j] = filtered_part
        return resultsf

    def findbestpart(self, decimals=10, verbose=False, lim_it=None):
        """
        Find which particle reached the recorded best position.

        Parameters
        ----------
        decimals : int, optional
            Decimal precision used for approximate comparison.
        verbose : bool, optional
            If ``True``, print the search progress.
        lim_it : int | None, optional
            Maximum iteration index inspected.

        Returns
        -------
        int
            Particle identifier, or ``-1`` when the search fails.
        """
        if decimals < -15:
            rise_warning("Best results not founded returning -1")
            return -1
        n_particles = self["optimization_parameters"]["n_particles"]
        nit = self.nit
        bestpos = self["best_position"]
        ibestpart = 0

        if lim_it is None:
            lim_it = nit

        for j in range(lim_it):
            for i in range(1, 1 + n_particles):
                pos = self["position" + str(i)]
                if all(np.around(pos[j], decimals) == np.around(bestpos, decimals)):
                    if verbose:
                        print("it=", j)
                    return i

        if verbose:
            pass_info("not found with decimals =", decimals)
        return self.findbestpart(decimals - 1, verbose=verbose, lim_it=lim_it)

    def compute_best_pos(self, cost_function: cost_function, **kwrgs):
        """
        Recompute simulation results at the recorded best position.

        Parameters
        ----------
        cost_function : cost_function
            Cost-function object able to simulate the corresponding context.
        **kwrgs : dict
            Reserved for future use.

        Returns
        -------
        sim_results
            Simulation results at the best position.
        """
        return cost_function.get_sim_results(self.x)

    ############################
    ##    plotting methods    ##
    ############################
    def plot_cost_history(
        self,
        ax: plt.axes,
        nitstop: int = -1,
        xlog: bool = False,
        ylog: bool = False,
        **ax_kwargs,
    ):
        """
        Plot the optimization cost history.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            Target axes.
        nitstop : int, optional
            Final iteration displayed.
        xlog : bool, optional
            If ``True``, use a logarithmic x-axis.
        ylog : bool, optional
            If ``True``, use a logarithmic y-axis.
        **ax_kwargs : dict
            Additional plotting keyword arguments.
        """
        cost = self["cost_history"]
        ax.plot(cost[0:nitstop], **ax_kwargs)
        if xlog:
            ax.set_xscale("log")
        if ylog:
            ax.set_yscale("log")
