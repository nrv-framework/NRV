"""OPTIMIZATION methods - optim: automated optimization of any simulation parameter

optim has been designed to enable optimization or automated space search of
parameters. Any simulation can be considered as a context for optimization.
NRV has to simple descriptors for optimization of geometrical quantities as
well as stimulation waveforms. However, there is no formal restriction and
specific search space can be described by the used (even electrophysiological
quantities or morphology).

The  The optimization problem, defined in a ``Problem``-class, couples a
``Cost_Function``-object, which evaluates the cost of the problem based on
user-specified outcomes, to an optimization method or algorithm embedded in
a ``Optimizer``-object (see below for access to class description).

The Cost_Function-class is constructed around 389 four main objects:

* a filter: which is an optional Python ``callable``-object, for vector
  formatting or space restriction of the optimization space,
* a static context: it defines the starting point of the simulation model to
  be  optimized. It can be any of the ``nmod``-objects or more genenerally a
  NRV ``simulable``-object,
* a ``ContextModifier``-object: it updates the static context according to the
  output of the optimization algorithm and the optimization space. The
  ``ContextModifier``-object is an abstract class, and two daughter classes
  for specific optimization problems are currently predefined: for stimulus
  waveform or geometry optimization (see below in the class list). Novel form
  of user-defined optimization should be described in a custom class that
  inherits from ``ContextModifier``,
* a CostEvaluation-class, which is a generic Python callable-class, and that
  can also be user-defined.


Optimization methods and algorithms implemented in NRV rely on third-party
optimization libraries:

* SciPy optimize, that should be prefered for continuous problems,
* Pyswarms for Particle Swarms Optimization metaheuristic in
  high-dimensional or discontinuous cases.


"""

from ._CostFunctions import cost_function
from ._Optimizers import Optimizer, scipy_optimizer, PSO_optimizer
from ._Problems import Problem

submodules = ["optim_utils"]

classes = ["Problem", "Optimizer", "scipy_optimizer", "PSO_optimizer", "cost_function"]

functions = []

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
