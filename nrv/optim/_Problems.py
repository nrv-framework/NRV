"""
NRV-:class:`.Problem` handling.
"""

import numpy as np
import faulthandler
import traceback
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
)

from ..backend._parameters import parameters
from ..backend._NRV_Class import NRV_class
from ..backend._NRV_Mproc import get_pool

from ..backend._log_interface import rise_error, pass_debug_info, set_log_level
from .optim_utils._OptimResults import optim_results
from ._CostFunctions import cost_function
from ._Optimizers import Optimizer

import sys

# enable faulthandler to ease 'segmentation faults' debug
faulthandler.enable()


class Problem(NRV_class):
    """
    Problem Class

    A class to describe problems that should be optimized with the NRV Framework.
    The problem should be described with a simulation and a cost, using the object
    cost_function, and various optimization algorithms can be used to find optimal solution.

    This class is abstract and is not supposed to be used directly by the end user. NRV can
    handle two types of problems:
    - problems where a geometric parameter can be optimized: please refer to ...
    - problems where the waveform can be optimized: please refer to ...
    """

    def __init__(
        self,
        cost_function: cost_function = None,
        optimizer: Optimizer = None,
        save_problem_results: bool = False,
        problem_fname: str = "optim.json",
        n_proc: int = None,
    ):
        super().__init__()
        self._CostFunction = cost_function
        self._Optimizer = optimizer
        # For cases where optimisation is done on a swarm(groupe) of particle
        self.swarm_optimizer = False
        # self._SwarmCostFunction = None
        self.save_problem_results = save_problem_results
        self.problem_fname = problem_fname
        self.mp_type = None
        self.n_proc = n_proc or parameters.optim_Ncores

    # Handling the cost_function attribute
    @property
    def costfunction(self) -> cost_function:
        """
        Cost function of a Problem,
        the cost function should be a CosFunction object, it should return a scalar.
        NRV function should be prefered
        """
        return self._CostFunction

    @costfunction.setter
    def costfunction(self, cf: cost_function):
        # need to add a verification that the cost function is a scallar and so on
        self._CostFunction = cf

    @costfunction.deleter
    def costfunction(self):
        self._CostFunction = None

    def _SwarmCostFunction(self, swarm):
        s_l = len(swarm)
        costs = np.zeros((s_l))
        if self.mp_type == "costfunction":
            for i in range(s_l):
                particle = swarm[i][:]
                costs[i] = self._CostFunction(particle)
        else:

            # LR: This still generate PETSC errors (not crashing the script tho). Adding pool.close()/pool.join() crashes everything however
            with get_pool(n_jobs=self.n_proc) as pool:
                for i_c, cost in enumerate(pool.imap(self._CostFunction, swarm)):
                    costs[i_c] = cost

        return costs

    def compute_cost(self, X):
        return self._CostFunction(X)

    # Handling the Optimizer attribute
    @property
    def optimizer(self):
        """
        Optimizer of the problem,
        the Optimizer should be an Optimizer object. It has reference to optimization
        methods and constraints
        """
        return self._Optimizer

    @optimizer.setter
    def optimizer(self, optim: Optimizer):
        self._Optimizer = optim
        self.swarm_optimizer = self._Optimizer.swarm_optimizer

    @optimizer.deleter
    def optmizer(self):
        # self._Optimizer = None
        pass

    # Call method is where the magic happens
    def __call__(self, **kwargs) -> optim_results:
        """
        Perform the optimization: minimze the `cost_function` using `optmizer`

        Parameters
        ----------

        kwargs
            containing parameters of the optimizer to change

        Returns
        -------
        optim_results
            results of the optimization


        Raises
        ------
        KeyboardInterrupt
        """
        try:
            kwargs = self.__update_saving_parameters(**kwargs)
            if self.mp_type is None:
                self.set_multiprocess_type()
            if not self.swarm_optimizer:
                results = self._Optimizer(self._CostFunction, **kwargs)
            else:
                results = self._Optimizer(self._SwarmCostFunction, **kwargs)
                results["status"] = "Completed"
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            results["status"] = "Error"
            rise_error(traceback.format_exc())

        set_log_level("INFO")
        if self.save_problem_results:
            results.save(save=True, fname=self.problem_fname)
        return results

    # Mcore handling
    def __check_m_proc_CostFunction(self):
        """
        check if a cost funciton can be parallelized
        """
        if isinstance(self._CostFunction, cost_function):
            return self._CostFunction.is_m_proc_func
        else:
            return False

    def set_multiprocess_type(self, costfunction_mp=True, n_core=None):
        """
        Set if multiprocessing should be applied to the optimizaiton or the CostFunction simulation

        Warning
        -------
        For now, only costfunction can be parallelized. This will be improve in the future
        """
        if n_core is not None:
            self.n_proc = n_core
        # parallelizable optimizer
        if "n_processes" in self._Optimizer.__dict__:
            if self.__check_m_proc_CostFunction() and costfunction_mp:
                # * To add number of n_core_fascicle = n_core
                self._Optimizer.n_processes = None
                self.mp_type = "costfunction"
            else:
                # * To add number of n_core_fascicle = 1
                #!! Bug cannot compute local method generated from cost_function_swarm_from_particle
                self._Optimizer.n_processes = self.n_proc
                #!!self._Optimizer.n_processes = None
                self.mp_type = "optimizer"
        else:
            # * To add number of n_core_fascicle = n_core
            self.mp_type = "costfunction"

    # additional methods
    def __update_saving_parameters(self, **kwargs):
        """
        internal use only: update the results saving parameters
        and remove the corresponding keys from kwargs
        """
        if "save_problem_results" in kwargs:
            self.save_problem_results = kwargs.pop("save_problem_results")
        if "problem_fname" in kwargs:
            self.problem_fname = kwargs.pop("problem_fname")
        return kwargs

    def context_and_cost(self, context_func, cost_func, residual):
        self.cost_function = cost_function(context_func, cost_func, residual)

    def autoset_optimizer(self):
        pass
