import numpy as np
import pyswarms

class Optimizer(NRV_class):
  def __init__(self, ndim):
    self._method = None
    self._ndim = ndim

