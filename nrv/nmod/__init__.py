"""NEURON Models - nmod: handles neural fiber models using the NEURON software.

nmod contains all the code to describe the axonal fibers using .mod mechanisms
with NEURON. This subpackage contains all primitives to describe:

  - unmyelinated axons with different models of nonlinear conductances,
  - myelinated axons with different models of nonlinear conductances,
  - fascicles consisting in bundles of (potentiallymixed ) axons,
  - nerves containing one or more fascicles.

nmod also contains tools to automatically generate fascicles and nerves,
with fiber repartition mimicking realistic anatomical observations.

Classes describing fibers, fascicles and nerves are simulable, meaning they
all have a `simulate` method that triggers the simulation. Only the top level
structure of the simulated scenario has to be simulated by the user, nrv takes
care of handling the simulation, potential combination with subpackages
(such as nmod or eit for instance). Parallel computing is also handled
internally.

.. SeeAlso::
   :doc:`Scientific details</scientific>`, :doc:`Simulables users guide</usersguide/simulables>`
"""

from ._axons import axon
from ._axon_population import axon_population
from ._unmyelinated import unmyelinated
from ._myelinated import myelinated
from ._fascicles import fascicle
from ._nerve import nerve
from . import results, utils

submodules = ["results", "utils"]

classes = [
    "axon",
    "unmyelinated",
    "myelinated",
    "axon_population",
    "fascicle",
    "nerve",
]

functions = [
    "create_axon_population",
    "plot_population",
    "save_axon_population",
    "load_axon_population",
    "fill_area_with_axons",
    "axon_packer",
    "expand_pop",
    "remove_collision",
    "remove_outlier_axons",
    "get_circular_contour",
    "load_stat",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
