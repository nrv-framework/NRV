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


from .backend import compileMods


from .fmod.materials import *
from .fmod.electrodes import *
from .fmod.stimulus import *
from .fmod.extracellular import *
from .fmod.recording import *
from .fmod.FEM.FEM import *
from .fmod.FEM.COMSOL_model import *
from .fmod.FEM.FENICS_model import *
######### May not be requiered at the end ###############
from .fmod.FEM.mesh_creator.MshCreator import *
from .fmod.FEM.mesh_creator.NerveMshCreator import *
from .fmod.FEM.fenics_utils.FEMSimulation import *    
from .fmod.FEM.fenics_utils.SimParameters import *
from .fmod.FEM.fenics_utils.SimResult import *
########################################################

from .nmod.axons import *
from .nmod.unmyelinated import *
from .nmod.myelinated import *
from .nmod.thin_myelinated import *
from .nmod.fascicles import *
from .nmod.fascicle_generator import *
from .nmod.nerves import *


from .utils.saving_handler import *
from .utils.cell.CL_postprocessing import *
from .utils.cell.CL_simulations import *
from .utils.cell.CL_discretization import *

from .utils.fascicle.FL_postprocessing import * 
