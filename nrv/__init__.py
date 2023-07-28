""" NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""

# Meta information
__title__           = 'NRV'
__project__         = 'NeuRon Virtualizer (NRV)'
__version__         = '0.9.10'
__date__            = '2023–07–23'
__author__          = 'Florian Kolbl'
__contributors__    = 'Florian Kolbl, Roland Giraud, Louis Regnacq, Thomas Couppey'
__copyright__       = '2023, Florian Kolbl'
__license__         = 'CeCILL'

#################################
# check environnement variables #
#################################
import os
import inspect
import platform
# create a dummy object to locate frameworks path
class DummyClass: pass
nrv_path = os.path.dirname(os.path.abspath(inspect.getsourcefile(DummyClass)))
root_path = nrv_path.replace('/nrv/','')
# check the PATH with os.environ['PATH'], modify bash/zsh profile
current_PATH = os.environ['PATH']
conf_file = '.bashrc'
if platform.system() == 'Darwin':
    conf_file = '.zshrc'
if not (nrv_path+':' in current_PATH or ':'+nrv_path in current_PATH):
    with open(os.path.expanduser('~/'+conf_file), "a") as outfile:
        outfile.write('\n\n\n# >>>>> NRV setup >>>>>\n')
        outfile.write('export PATH="'+nrv_path+':$PATH"\n')
        outfile.write('# <<<<< NRV setup <<<<<\n')
    outfile.close()
    print(conf_file + ' file modified, please source or restart console to be able to used nrv2calm')
# create the environnement variable NRVPATH if it does not exist
if not 'NRVPATH' in os.environ:
    os.environ['NRVPATH'] = nrv_path
# change the permissions on nrv2calm
if not os.access(nrv_path+'/nrv2calm', os.X_OK):
    mode = os.stat(nrv_path+'/nrv2calm').st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(nrv_path+'/nrv2calm', mode)

# Public interface
from .backend import compileMods
from .backend.parameters import *

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
from .fmod.FEM.mesh_creator.NRV_Msh import *
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
from .nmod.nerve import *

from .utils.saving_handler import *
from .utils.nrv_function import *
from .utils.cell.CL_postprocessing import *
from .utils.cell.CL_simulations import *
from .utils.cell.CL_discretization import *
from .utils.fascicle.FL_postprocessing import * 

from .optim.CostFunctions import *
from .optim.Optimizers import *
from .optim.Problems import *
