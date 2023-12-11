# pylint: skip-file
""" NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""

__copyright__ = "2023, Florian Kolbl"
__license__ = "CeCILL"
__version__ = "0.9.13"
__title__ = "NeuRon Virtualizer"

#####################################
#  check environnement variables    #
#  check correct NRV configuration  #
#####################################
import os
import inspect
import platform
# GMSH must be imported before neuron to prevent installation issues
import gmsh


# create a dummy object to locate frameworks path
class DummyClass:
    """Dummy class"""

    pass


nrv_path = os.path.dirname(os.path.abspath(inspect.getsourcefile(DummyClass)))
root_path = nrv_path.replace("/nrv/", "")
# check the PATH with os.environ['PATH'], modify bash/zsh profile
current_PATH = os.environ["PATH"]
conf_file = ".bashrc"
if platform.system() == "Darwin":
    # for MacOsX platforms
    conf_file = ".zshrc"
if not (
    nrv_path + ":" in current_PATH
    or ":" + nrv_path in current_PATH
    or "/nrv:" in current_PATH
):
    with open(os.path.expanduser("~/" + conf_file), "r") as outfile:
        # test if bash/zsh profile already modified
        Flag = False
        lines = outfile.readlines()
        for line in lines:
            if "NRV setup" in line:
                Flag = True
    outfile.close()
    with open(os.path.expanduser("~/" + conf_file), "a") as outfile:
        # modify or suggest user to source it
        if not Flag:
            # in this case, thte bash/zsh profile is not modified yet,
            # # then do it
            outfile.write("\n\n\n# >>>>> NRV setup >>>>>\n")
            outfile.write('export PATH="' + nrv_path + ':$PATH"\n')
            outfile.write("# <<<<< NRV setup <<<<<\n")
            print(
                conf_file
                + " file modified, please source or restart console to be able to used nrv2calm"
            )
        # ask to source bash/zsh profile
        else:
            print(
                "Please restart console to be able to use nrv2calm or source your own bash/zsh profile"
            )
    outfile.close()
# create the environnement variable NRVPATH if it does not exist
if "NRVPATH" not in os.environ:
    os.environ["NRVPATH"] = nrv_path
# change the permissions on nrv2calm
if not os.access(nrv_path + "/nrv2calm", os.X_OK):
    mode = os.stat(nrv_path + "/nrv2calm").st_mode
    mode |= (mode & 0o444) >> 2  # copy R bits to X
    os.chmod(nrv_path + "/nrv2calm", mode)

######################
#  Public interface  #
######################
from .backend import compileMods
from .backend.parameters import *
from .backend.NRV_Class import load_any

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
from .optim.optim_utils.ContextModifier import *
from .optim.optim_utils.CostEvaluation import *
from .optim.optim_utils.InterpolationFunctions import *