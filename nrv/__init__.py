""" NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""

# Meta information
__title__           = 'NRV'
__version__         = '0.0.1'
__date__            = '2021–06–11'
__author__          = 'Florian Kolbl'
__contributors__    = 'Florian Kolbl, Roland Giraud, Louis Regnacq, Thomas Couppey'
__copyright__       = 'Florian Kolbl'
__license__         = 'CeCILL'

# Public interface
from .compileMods import *
from .materials import *
from .electrodes import *
from .stimulus import *
from .FEM import *
from .fascicle_generator import *
from .MCore import Mcore_handler
from .CL_postprocessing import *
from .FL_postprocessing import *
from .CL_simulations import *
from .extracellular import *
from .axons import *
from .unmyelinated import *
from .myelinated import *
from .thin_myelinated import *
from .fascicles import *
from .nerves import *

