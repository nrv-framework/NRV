import numpy as np

from ..backend.NRV_Class import NRV_class
from .CostFunctions import CostFunction
from .Optimizers import Optimizer


def cost_function_swarm_from_particle(cost_function_part, **kwargs):
    """
    Generate a cost function for a swarm from a cost function for a particle

    Parameters
    ----------
    cost_function_part    : func
        cost function return a cost (float) from a particle (1-dimensional array)
    verbose      : tupple
        if True, print a progress bar for updated whenby default True

    Returns
    -------
    part        : np.ndarray
        vector of values of the part in the len_part dimension
    """
    def cost_function_swarm(swarm):
        L = len(swarm)
        costs = np.zeros((L))
        for i in range(L):
            particle = swarm[i][:]
            costs[i] = cost_function_part(particle, **kwargs)
            #print("part=", particle, "c=", costs[i] )
        return costs
    return cost_function_swarm

class Problem(NRV_class):
    """
    Problem Class

    A class to describe problems that should be optimized with the NRV Framework.
    The problem should be described with a simulation and a cost, using the object
    CostFunction, and various optimization algorithms can be used to find optimal solution.

    This class is abstract and is not supposed to be used directly by the end user. NRV can
    handle two types of problems:
        - problems where a geometric parameter can be optimized: please refer to ...
        - problems where the waveform can be optimized: please refer to ...
    """

    def __init__(self, cost_function:CostFunction = None, optimizer:Optimizer =None):
        super().__init__()
        self._CostFunction = cost_function
        self._Optimizer = optimizer
        # For cases where optimisation is done on a swarm(groupe) of particle
        self.swarm_optimizer = False
        self._SwarmCostFunction = None

    # Handling the CostFunction attribute
    @property
    def costfunction(self):
        """
        Cost function of a Problem,
        the cost function should be a CosFunction object, it should return a scalar.
        NRV function should be prefered"""
        return self._CostFunction

    @costfunction.setter
    def costfunction(self, cf:CostFunction):
        # need to add a verification that the cost function is a scallar and so on
        self._CostFunction = cf

    @costfunction.deleter
    def costfunction(self):
        self._CostFunction = None

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
    def optimizer(self, optim:Optimizer):
        self._Optimizer = optim
        self.swarm_optimizer = self._Optimizer.swarm_optimizer

    @optimizer.deleter
    def optmizer(self):
        # self._Optimizer = None
        pass

    # Call method is where the magic happens
    def __call__(self, **kwargs):
        if not self.swarm_optimizer:
            results = self._Optimizer(self._CostFunction, **kwargs)
        else:
            self._SwarmCostFunction = cost_function_swarm_from_particle(self._CostFunction)
            results = self._Optimizer(self._SwarmCostFunction, **kwargs)
        return results

    # additional methods
    def context_and_cost(self, context_func, cost_func, residual):
        self.CostFunction = CostFunction(context_func, cost_func, residual)

    def autoset_optimizer(self):
        pass

