# pylint: skip-file
"""NRV: NeuRon Virtualizer, modeling of the Nervous System,

NRV is a pythonic framework for simulating bio-electronic phenomena and
interface-systems, taking into account both neural dynamics and extracellular
fields. NRV is designed to be accessible to end-user with a basic knowledge of
python and object-oriented programming, and focuses on providing tools to
describe a electrophysiological setup (axons, fascicles, nerves...) and
electrical interfaces (electrodes for stimulation, recording and even
electrical impedance measurements). Simulations can be performed automatically,
and optimization algorithms can be interfaced to a simulation to improve
possibilities of designer novel biomedical approaches.

NRV is open source (under CeCILL license), and developpers pay attention to
limit the dependencies to open source ressources as well. For scientific
comparison with existing solutions, NRV has been designed to interface COMSOL,
however associated code in only maintained and not further developped now. NRV
relies on NEURON for simulation of neural cell properties, and FenicsX for
Finite Element computations.

NRV has been developped by contributors from the CELL reserach group at the
Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University (France)
until june 2023, and is now primarily developed and maintained by the
Bioelectronics group of laboratory IMS (UMR CNRS 5218), INP Bordeaux,
U. of Bordeaux.


.. note::
  to cite NRV:
  Couppey T., Regnacq L., Giraud R., Romain O., Bornat Y., and Kolbl F. (2024)
  NRV: An opem framework for in silico evaluation of peripheral nerve electrical
  stimulation strategies. PLOS Computational Biology 20(7): e1011826.
  https://doi.org/10.1371/journal.pcbi.1011826


.. SeeAlso::
   - **General information**: `nrv-framework.org <https://nrv-framework.org>`_
   - **Discussions and queries**: `Forum NRV <https://nrv-framework.org/forum>`_
   - **Full code**: `Github repository <https://github.com/nrv-framework/NRV>`_


.. note::
  We kindly ask developpers and users to respect our code of conduct, accessible
  from the following page: `Code of conduct <https://nrv-framework.org/?page_id=96>`_

"""

__copyright__ = "2023, nrv-framework.org"
__license__ = "CeCILL"
__version__ = "1.2.2"
__title__ = "NeuRon Virtualizer"
__authors__ = "Florian Kolbl, Roland Giraud, Louis Regnacq, Thomas Couppey"
__contributors__ = __authors__
__project__ = "NeuRon Virtualizer (NRV)"

#####################################
#  check correct NRV configuration  #
#####################################

# GMSH must be imported before neuron to prevent installation issues
import gmsh
import os

nrn_options = "-nogui"
os.environ["NEURON_MODULE_OPTIONS"] = nrn_options
import neuron
from .backend._parameters import parameters

# load configuration module
from .backend._config import nrv_config

# instanciate configuration
CONFIG = nrv_config()

######################
#  Public interface  #
######################
from .backend import _compileMods
from .backend._NRV_Class import load_any

from .fmod._materials import *
from .fmod._electrodes import *
from .fmod._extracellular import *
from .fmod._recording import *
from .fmod.FEM._FEM import *
from .fmod.FEM._COMSOL_model import *
from .fmod.FEM._FENICS_model import *

######### May not be requiered at the end ###############
from .fmod.FEM.mesh_creator._MshCreator import *
from .fmod.FEM.mesh_creator._NerveMshCreator import *
from .ui._NRV_Msh import *
from .fmod.FEM.fenics_utils._FEMSimulation import *
from .fmod.FEM.fenics_utils._FEMParameters import *
from .fmod.FEM.fenics_utils._FEMResults import *
from .fmod.FEM.fenics_utils._fenics_materials import *
from .fmod.FEM.fenics_utils._f_materials import *
from .fmod.FEM.fenics_utils._layered_materials import *

########################################################

from .nmod._axons import *
from .nmod._unmyelinated import *
from .nmod._myelinated import *
from .nmod._fascicles import *
from .nmod._nerve import *
from .nmod.utils._axon_pop_generator import *

from .nmod.results._axons_results import *
from .nmod.results._unmyelinated_results import *
from .nmod.results._myelinated_results import *
from .nmod.results._fascicles_results import *
from .nmod.results._nerve_results import *


from .utils._saving_handler import *
from .utils._nrv_function import *
from .utils._units import *
from .utils._stimulus import *
from .utils.geom._misc import *

from .ui._axon_postprocessing import *
from .ui._axon_simulations import *
from .ui._fascicle_postprocessing import *
from .ui._spec_loaders import *

from .optim._CostFunctions import *
from .optim._Optimizers import *
from .optim._Problems import *
from .optim.optim_utils._ContextModifiers import *
from .optim.optim_utils._CostEvaluation import *
from .optim.optim_utils._OptimFunctions import *


from .eit._protocol import pyeit_protocol
