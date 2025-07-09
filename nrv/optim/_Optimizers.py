"""
NRV-:class:`.Optimizer` handling.
"""

from abc import ABCMeta, abstractmethod
import os
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter, asctime, localtime
import traceback
import json
import sys
import pyswarms as ps
from pyswarms.backend.topology import Star, Ring
import scipy.optimize as scpopt


from ..backend._NRV_Class import NRV_class
from ..backend._parameters import parameters
from ..backend._log_interface import set_log_level, rise_error, rise_warning

from .optim_utils._OptimResults import optim_results

dir_path = parameters.nrv_path + "/_misc"
dir_path + "/log/NRV.log"
# mymodule.py


class Optimizer(NRV_class, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, method=None):
        super().__init__()
        self._method = method
        self.swarm_optimizer = False

    def minimize(self, f: callable, **kwargs) -> optim_results:
        """
        Minimze the function ``f`` using the `optimzer`'s parameters

        Parameters
        ----------
        f : callable
            function to minimize
        kwargs                  : dict
            containing parameters to change in the class (:class:``PSO_optimizer``)

        Returns
        -------
        optim_results
            results of the optimization
        """
        self.set_parameters(**kwargs)
        results = optim_results(self.save(save=False))
        results["date"] = asctime(localtime())
        results["status"] = "Processing"
        return results

    def __call__(self, f: callable, **kwargs: Any) -> optim_results:
        return self.minimize(f, **kwargs)


class scipy_optimizer(Optimizer):
    """


    Parameters
    ----------
    method : str | callable, optional
        Type of solver.  Should be one of
            - 'Nelder-Mead'
            - 'Powell'
            - 'CG'
            - 'BFGS'
            - 'Newton-CG'
            - 'L-BFGS-B'
            - 'TNC'
            - 'COBYLA'
            - 'SLSQP'
            - 'trust-constr'
            - 'dogleg'
            - 'trust-ncg'
            - 'trust-exact'
            - 'trust-krylov'
            - custom - a callable object

    x0 : np.ndarray, optional
        Initial guess. Array of real elements of size (n,), where n is the number of independent variables,. by default None
    args : tuple, optional
        Extra arguments passed to the objective function and its derivatives (fun, jac and hess functions), by default ()
    jac : {callable,  '2-point', '3-point', 'cs', bool}, optional
        Method for computing the gradient vector, optional
        _description_, by default None
    hess : {callable, '2-point', '3-point', 'cs', HessianUpdateStrategy}, optional
        Method for computing the Hessian matrix, by default None
    hessp : callable, optional
        Hessian of objective function times an arbitrary vector p. Only for
        Newton-CG, trust-ncg, trust-krylov, trust-constr, by default None
    bounds : sequence or `Bounds`, optional
        Bounds on variables for Nelder-Mead, L-BFGS-B, TNC, SLSQP, Powell,
        trust-constr, and COBYLA methods., by default None
    constraints : {Constraint, dict} or List of {Constraint, dict}, optional
        Constraints definition. Only for COBYLA, SLSQP and trust-constr, by default ()
    tol : float, optional
        Tolerance for termination, by default None
    callback : callable, optional
        A callable called after each iteration, by default None
    maxiter : int, optional
        _description_, by default None
    options : dict, optional
        A dictionary of solver options, by default None
    dimension : int, optional
        _description_, by default None
    normalize : bool, optional
        _description_, by default False

    Note
    ----
    The following arguments are those used in scipy.optimize.minimize (see scipy documentation [2] for more informations): ``x0``, ``args``, ``jac``, ``hess``, ``hessp``, ``bounds``, ``constraints``, ``tol``, ``callback``, ``options``

    Examples
    --------
    The following lines shows how `scipy_optimizer` can be used to minimze a 2D sphere function.

    >>> import nrv
    >>> my_cost1 = nrv.sphere()
    >>> my_opt = nrv.scipy_optimizer(dimension=2, x0= [100, 10], maxiter=10)
    >>> res = my_opt.minimize(my_cost1)
    >>> print("best position",res.x, "best cost", res.best_cost)

        best position [-1.52666570e-08 -1.32835147e-07] best cost 1.337095622502969e-07


    References
    ----------
    [1] `scipy <https://docs.scipy.org/doc/scipy/>`_

    [2] `scipy.optimize.minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html#scipy.optimize.minimize>`_
    """

    def __init__(
        self,
        method: str = None,
        x0: np.ndarray = None,
        args: tuple = (),
        jac: callable = None,
        hess: callable = None,
        hessp: callable = None,
        bounds: tuple = None,
        constraints: dict = (),
        tol: float = None,
        callback: callable = None,
        maxiter: int = None,
        options: dict = None,
        dimension: int = None,
        normalize: bool = False,
    ):
        if method is None:
            super().__init__("scipy_default")
        else:
            super().__init__("scipy_" + method)
        self.x0 = x0
        self.args = args
        self.scipy_method = method
        self.jac = jac
        self.hess = hess
        self.hessp = hessp
        self.bounds = bounds
        self.constraints = constraints
        self.tol = tol
        self.callback = callback
        self.options = options or {}
        self.maxiter = maxiter
        self.dimensions = dimension
        self.normalize = normalize
        self.scale_translation = None
        self.scale_homothety = None
        self.scaled_bounds = None

    def __update_dimensions(self, results):
        """ """
        if self.bounds is None:
            if self.dimensions is not None:
                self.bounds = [(None, None) for _ in range(self.dimensions)]
        if self.x0 is None:
            if self.bounds is None:
                rise_error(
                    "scipy optimizer: at least x0 or boundaries should be initiate"
                )
            else:
                self.dimensions = len(self.bounds)
                self.x0 = []

                for i in range(self.dimensions):
                    min, max = self.bounds[i]
                    if min is None:
                        min = np.finfo(np.float32).min
                    if max is None:
                        max = np.finfo(np.float32).max
                    self.x0 += [np.random.uniform(min, max)]
                results["x0"] = self.x0
        else:
            self.dimensions = len(self.x0)
            results["dimensions"] = self.dimensions

    def __normalize_bound(self, results):
        self.scale_translation = np.zeros(self.dimensions)
        self.scale_homothety = np.ones(self.dimensions)
        if not self.normalize:
            self.scaled_bounds = self.bounds
        else:
            self.scaled_bounds = []
            for i, bd in enumerate(self.bounds):
                self.scaled_bounds += [(0, 1)]
                self.scale_translation[i] = bd[0]
                self.scale_homothety[i] = bd[1] - bd[0]
        results["scale_translation"] = self.scale_translation
        results["scale_homothety"] = self.scale_homothety
        results["scaled_bounds"] = self.scaled_bounds

    def minimize(self, f: callable, **kwargs) -> optim_results:
        results = super().minimize(f, **kwargs)
        if self.maxiter is not None:
            self.options["maxiter"] = self.maxiter
        self.__update_dimensions(results)
        self.__normalize_bound(results)
        results["cost_history"] = []
        results["position_history"] = []

        def f_history(x):
            x = (results["scale_homothety"] * x) + results["scale_translation"]
            c = f(x)
            results["position_history"].append([x])
            results["cost_history"].append(c)
            return c

        t0 = perf_counter()
        res = scpopt.minimize(
            fun=f_history,
            x0=self.x0,
            args=self.args,
            method=self.scipy_method,
            jac=self.jac,
            hess=self.hess,
            hessp=self.hessp,
            bounds=self.scaled_bounds,
            constraints=self.constraints,
            tol=self.tol,
            callback=self.callback,
            options=self.options,
        )
        res.x = (results["scale_homothety"] * res.x) + results["scale_translation"]

        t_opt = perf_counter() - t0
        results["optimization_time"] = t_opt
        results["best_cost"] = res.fun
        results["best_position"] = res.x

        results.update(res)
        # hess_inv cannot be converted to json
        if "hess_inv" in results:
            del results["hess_inv"]
        results["status"] = "Completed"
        return results


class PSO_optimizer(Optimizer):
    """
    Perform a Particle swarm optimization (PSO) on with a defined cost function using pyswarms
    library[1]

    Parameters
    ----------
    n_particles           	: int
        number of particle of the swarm, by default 5
    dimensions              : int
        number of dimensions of each particle
    options                 : dict
        hyperparameter of the PSO
    maxiter                    : int
        number of iteration of the PSO
    n_processes             : int
        number of process used to parallelize cost calculation, by default None
    bounds                  : tupple
        bounds of the particle, if equal no bounds, by default (0, 0)
    init_pos                : array
        initial position of the particles if None random, by default None
    print_time              : bool
        if True, print the optimisation time, by default True
    opt_type                : str
        Neightboorhood type, by default "global"
        type possibly:

            - "global"                : Global best PSO (star topology)
            - "local"                 : Local best PSO (ring topology)

    static      : bool
        if False and opt_type is local, update the neigthboorhood of each particle every iterations
    bh_strategy             : str
        out of bound position strategy for pyswarms optimizer [2]:

            - "nearest"               : Round the value to the nearest bound (default)
            - "periodic"              : set to the modulus of the value between the two bounds
            - "random"                : set to a random value
            - "shrink"                : reduce the velocity to finish land on the bound
            - "reflective"            : mirror the position form inside to ouside the bounds
            - "intermediate"          : set to intermediate value between previous pos and bound

    oh_strategy             : dict (like {"w":str, "c1":str, "c2":str})
        Dynamic options strategy for pyswarms optimizer [3], if None static options,
        by default None:

            - "exp_decay"             : Decreases the parameter exponentially between limits
            - "lin_variation"         : Decreases/increases the parameter linearly between limits
            - "nonlin_mod"            : Decreases/increases the parameter between limits
                                    according to a nonlinear modulation index
            - "rand"                  : takes a uniform random value between limits

    ftol                    : float
        relative error in objective_func(best_pos) acceptable for convergence, if None -np.inf
        default None
    ftol                    : int
        number of iterations over which the relative error in objective_func(best_pos) is
        acceptable for convergence, by default 1
    save_results            : bool
        save or not the output in a .json file, by default False
    saving_file             : str
        name of the file on wich the output should be saved, by default "pso_results.json"

    Returns
    -------
    results     : optim_results
        contains all the parameters and outputs of the PSO

    References
    ----------
    links to pyswarms doc:
        [1] `Pyswams <https://pyswarms.readthedocs.io/en/latest/index.html>`_

        [2] `Pyswams handlers <https://pyswarms.readthedocs.io/en/latest/api/pyswarms.handlers.html>`_
    """

    def __init__(
        self,
        n_particles=5,
        bounds=(0, 0),
        dimensions=50,
        options=None,
        maxiter=1,
        n_processes=None,
        init_pos=None,
        print_time=False,
        opt_type="global",
        static=False,
        ftol=None,
        ftol_iter=1,
        bh_strategy="nearest",
        oh_strategy=None,
        save_results=False,
        saving_file="pso_results.json",
        comment=None,
    ):
        super().__init__("PSO")
        self.swarm_optimizer = True
        self.n_particles = n_particles
        self.dimensions = dimensions
        self.options = options
        self.maxiter = maxiter
        self.n_processes = n_processes
        self.bounds = bounds
        self.init_pos = init_pos
        self.print_time = print_time
        self.opt_type = opt_type
        self.static = static
        self.ftol = ftol
        self.ftol_iter = ftol_iter
        self.bh_strategy = bh_strategy
        self.oh_strategy = oh_strategy
        self.save_results = save_results
        self.saving_file = saving_file
        self.comment = comment

    def __nrv2pyswarms_bounds(self):
        if np.size(self.bounds) == 2 * self.dimensions:
            if isinstance(self.bounds[0], tuple) and np.size(self.bounds[0]) == 2:
                max_bound = np.zeros(self.dimensions)
                min_bound = np.zeros(self.dimensions)
                for i, bd in enumerate(self.bounds):
                    max_bound[i] = max(bd)
                    min_bound[i] = min(bd)
                return (min_bound, max_bound)
        if np.size(self.bounds) > 2:
            return self.bounds
        elif self.bounds[0] == self.bounds[1]:
            return None
        else:
            max_bound = max(self.bounds) * np.ones(self.dimensions)
            min_bound = min(self.bounds) * np.ones(self.dimensions)
            return (min_bound, max_bound)

    def minimize(self, f_swarm: callable, **kwargs) -> optim_results:
        """
        Perform a Particle swarm optimization

        Parameters
        ----------
        f_swarm     : callable
            function taking in parameter a swarm (dim-dimensions array) and returning the cost for each
            particle (1-dimensionnal array)
        kwargs                  : dict
            containing parameters to change in the class (:class:``PSO_optimizer``)

        Returns
        -------
        optim_results
            results of the optimization
        """
        # self.__mproc_handling()
        results = super().minimize(f_swarm, **kwargs)

        verbose = parameters.get_nrv_verbosity() > 2
        # initial position
        if not np.iterable(self.init_pos):
            self.init_pos = None

        # create pyswarms bounds
        psbounds = self.__nrv2pyswarms_bounds()

        if self.opt_type.lower() == "local":
            if not self.options or len(self.options) < 5:
                self.options = {"c1": 0.5, "c2": 0.5, "w": 0.5, "k": 5, "p": 2}
            topology = Ring(static=self.static)
        # Check number of pcu
        else:
            if not self.options:
                self.options = {"c1": 0.5, "c2": 0.5, "w": 0.5}
            topology = Star()

        # Initialize results directory
        if self.opt_type.lower() != "global":
            results["optimization_parameters"]["static"] = self.static

        if self.comment is not None:
            results["comment"] = self.comment

        if self.save_results:
            with open(self.saving_file, "w") as outfile:
                json.dump(results, outfile)

        if self.ftol is None:
            ## As np.inf cannot be encode by json encoding ftol is used as a local varialble
            ftol = -np.inf
            self.ftol_iter = 1
        else:
            ftol = self.ftol

        try:
            # Call instance of PSO
            optimizer = ps.single.general_optimizer.GeneralOptimizerPSO(
                n_particles=self.n_particles,
                dimensions=self.dimensions,
                options=self.options,
                oh_strategy=self.oh_strategy,
                bounds=psbounds,
                ftol=ftol,
                ftol_iter=self.ftol_iter,
                init_pos=self.init_pos,
                bh_strategy=self.bh_strategy,
                topology=topology,
            )
            optimizer.rep = set_log_level("WARNING", clear_log_file=True)
            __lab = "PSO optimizer"
            if self.n_processes is None or self.n_processes == 1:
                __lab += " - 1 proc"
            else:
                __lab += f" - {self.n_processes} procs"
            optimizer.name = __lab

            # Perform optimization
            t0 = perf_counter()
            cost, pos = optimizer.optimize(
                f_swarm,
                iters=self.maxiter,
                n_processes=None,
                verbose=verbose,
            )
            t_opt = perf_counter() - t0

            pos_history = np.array(optimizer.pos_history)
            self.nit = np.shape(pos_history[:, 0, :])[0]

            if self.print_time:
                print(
                    "the cumputing time for ",
                    self.nit,
                    " iterations and ",
                    self.n_particles,
                    " particles is : ",
                    t_opt,
                    "s",
                )

            # Save results
            results["nit"] = self.nit
            results["nfev"] = self.nit * self.n_particles
            results["status"] = "Completed"
            results["best_position"] = pos.tolist()
            results["x"] = results["best_position"]
            results["best_cost"] = cost

            results["optimization_time"] = t_opt
            results["cost_history"] = optimizer.cost_history
            results["neighbor_bestc"] = optimizer.mean_neighbor_history
            results["personal_bestc"] = optimizer.mean_pbest_history

            velocity_history = np.array(optimizer.velocity_history)
            pos_history = np.array(optimizer.pos_history)
            for i in range(self.n_particles):
                results["position" + str(i + 1)] = pos_history[:, i, :].tolist()
                results["velocity" + str(i + 1)] = velocity_history[:, i, :].tolist()
            if self.save_results:
                with open(self.saving_file, "w") as outfile:
                    json.dump(results, outfile)
        except KeyboardInterrupt:
            results["status"] = "Interrupted"
            if self.save_results:
                with open(self.saving_file, "w") as outfile:
                    json.dump(results, outfile)
            rise_error(KeyboardInterrupt, "Interuption raised during PSO")
        except:
            results["status"] = "Failed"
            results["Error_from_prompt"] = traceback.format_exc()
            print(results["Error_from_prompt"])
            if self.save_results:
                with open(self.saving_file, "w") as outfile:
                    json.dump(results, outfile)

        return results
