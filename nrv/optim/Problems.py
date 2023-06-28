from ..backend.log_interface import rise_error, rise_warning, pass_info
from ..backend.file_handler import json_dump
from ..backend.NRV_Class import NRV_class
from .CostFunctions import CostFunction

class Problem(NRV_class):
    '''
    Problem Class

    A class to describe problems that should be optimized with the NRV Framework.
    The problem should be described with a simulation and a cost, using the object
    CostFunction, and various optimization algorithms can be used to find optimal solution.

    This class is abstract and is not supposed to be used directly by the end user. NRV can
    handle two types of problems:
        - problems where a geometric parameter can be optimized: please refer to ... 
        - problems where the waveform can be optimized: please refer to ...
    '''
    def __init__(self):
        self._CostFunction = None
        self._Optimizer = None

    # Handling the CostFunction attribute
    @property
    def CostFunction(self):
        '''
        Cost function of a Problem,
        the cost function should be a CosFunction object, it should return a scalar.
        NRV function should be prefered'''
        return self._CostFunction
    
    @CostFunction.setter
    def CostFunction(self, cost_function):
        # need to add a verification that the cost function is a scallar and so on
        self._CostFunction = cost_function

    @CostFunction.deleter
    def CostFunction(self):
        self._CostFunction = None

    def compute_cost(self, X):
        return self._CostFunction(X)

    @property
    def Optimizer(self):
        '''
        Optimizer of the problem,
        the Optimizer should be an Optimizer object. It has reference to optimization
        methods and constraints
        '''
        return self._Optimizer

    @Optimizer.setter
    def Optimizer(self, optimizer):
        self._Optimizer = optimizer

    @Optimizer.deleter
    def Optmizer(self):
        self._Optimizer = None

    # Call method is where the magic happens
    def __call__(self):
        pass

    #additional methods
    def context_and_cost(self, context_func, cost_func):
        self.CostFunction = CostFunction(context_func, cost_func)

    def autoset_optimizer(self):
        pass

    
    
