from ..backend.NRV_Class import NRV_class

from abc import ABCMeta, abstractmethod


# import pyswarms


class Optimizer(NRV_class, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, method=None):
        self._method = method


class PSO_optimizer(Optimizer):
    def __init__(self):
        super().__init__("PSO")
        pass
