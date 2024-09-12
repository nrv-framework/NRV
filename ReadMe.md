[![PyPI version](https://badge.fury.io/py/nrv-py.svg)](https://badge.fury.io/py/nrv-py)
[![Documentation Status](https://readthedocs.org/projects/nrv/badge/?version=latest)](https://nrv.readthedocs.io/en/latest/?badge=latest)
[![License: CeCill](https://img.shields.io/badge/Licence-CeCill-blue )](https://github.com/fkolbl/NRV/blob/master/Licence.txt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10497741.svg)](https://doi.org/10.5281/zenodo.10497741)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nrv-framework/NRV-demo/main)
<!---[![DOI](xxxx)](xxx)-->
<!---[![Build Status](xxxx)](xxx)-->

<img src="https://github.com/nrv-framework/NRV/blob/master/docs/__logo/logo.png" alt="NRV" width="50%" height="auto" class="center">

# NRV
*Python library for Peripheral Nervous System stimulation modeling*

NRV (or NeuRon Virtualizer) is a pythonic framework to enable fast and user friendly simulations of the Peripheral Nervous System. Axons models are simulated with the [NEURON](http://www.neuron.yale.edu/neuron) software, and extracellular fields are computed either from analytic equations such as point source approximation or with a more detailed description of the nerve and electrode geometry and Finite Elements Method, either using [COMSOL](https://www.comsol.com) (additional commercial licence requiered) or the [FENICS project](https://fenicsproject.org). All computations are performed with the quasistatic approximation of the Maxwell equations, no ephaptic coupling. Stimulation waveform can be of random shapes, and any kinds of electrode can be combined to model complex stimulation strategies.

NRV has been optimized for large population of axons, from generating correct population following a specific diameter repartition, through automatic placement to computation and post-processing of the axons activity when a stimulus is applied. Parallel computation, interface with NEURON and COMSOL and FENICS is automatically handled by NRV. For a detailed description and full help on installation, basic usage and API documentation, please visit ou [NRV readthedocs page](https://nrv.readthedocs.io/en/latest/).

NRV has been developped by contributors from the CELL research group at the Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University, until June 2023 and is now developped and maintained by the Bioelectronics group of laboratory IMS (UMR CNRS 5218), INP Bordeaux, U. Bordeaux.


# Installation

NRV is pip installable and the hole process should be quite simple. However, to prevent from third packages version conflict we recommend to create a dedicated conda environnement: 

    conda create -n nrv-env -c anaconda python=3.12 

and activate it before any installation with the command: 

    conda activate nrv-env

## Dependencies

### Open source third-party Dependencies


The pip installation takes care of most of the open source third-party dependencies, but the FEM solver ([FenicsX](http://https://fenicsproject.org/.org>)) and the Message Passing Interface ([MPICH](https://www.mpich.org/>))
are conda-installable only:

    conda install -c conda-forge fenics-dolfinx==0.8.0 mpich



### COMSOL Installation (optional)


NRV can perform computations of FEM with COMSOL. However, the end user has to provide a valid commercial installed license by its own. COMSOL installation can be performed before or after NRV's installation. For using COMSOL, information about the installation must be specified in the `nrv/_misc` code folder, by filling the following fields in the 'NRV.ini' file:

    [COMSOL]
    COMSOL_STATUS = True
    COMSOL_SERVER = PATH_TO_COMSOL_SERVER_BINARIES
    COMSOL_CPU = 1
    COMSOL_PORT = 2036
    TIME_COMSOL_SERVER_LAUNCH = 10
 
Especially, the correct path to the COMSOL server binaries has to be specified, the port has to be adapted if changed from default values.

The use of FenicsX for FEM computations have been extensively tested by NRV's contributor, and we do not recommend to use COMSOL with NRV as new geometries or electrode won't be implemented with COMSOL. Also, the use of commercial licenses limits the reproducibility and open-science possibilities.

## Installing NRV

### Using pip


NRV can simply be installed with pip [nrv-py](https://pypi.org/project/nrv-py/>):

    pip install nrv-py

if you want the very last development version under development, please consider:

    pip install git+https://github.com/fkolbl/NRV.git 

if you already installed a previous version and want to upgrade to the very last development version, please use:

    pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git

You should be now able to import nrv in your python shell:

    import nrv

Be aware that on the first import of NRV, some files related to simulation of ion channels are automatically compiled by NEURON, you may see the results of the compilation (including warning, but no errors) on your prompt. 

### Using docker


This method should be preferred as all dependencies are already setup. Note that in this configuration, COMSOL cannot be used. Assuming that docker is already installed, the first step is to pull the image:

    docker pull nrvframework/nrv

You can then use create a new container using:

    docker run --rm -it nrvframwork/nrv

where the --rm argument suppress the container once finished, and -it gives the interactive console. 
A second image is available to use NRV in Jupyter notebooks:

    docker pull nrvframework/lab

You can then create a container using:

    docker run --rm -p 8888:8888 nrvframework/lab

Where the `-p 8888:8888` maps the port to the local host. This should give you a link and token to load Jupyter from your browser.

### NRV on Windows


NRV is not directly installable on Windows due to some FenicsX dependencies not available on windows. 
However one can easily overcome this problem by using [WLS2](<https://learn.microsoft.com/en-us/windows/wsl/install>). Assuming a blank installation of WLS2 (Ubuntu 22.xx), the following instruction are required to install and use NRV.

Installation of [micromamba](https://github.com/mamba-org/mamba) (a lighter and faster conda equivalent):

    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)

Creation of the environnement: 

    micromamba create -n nrv-env -c anaconda python=3.12 

Sudo update and installation of the required libs:

    sudo apt-get update -y
    sudo apt-get install build-essential libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev libxrender1 libxcursor1 libxft2 libxinerama1 make libx11-dev git bison flex automake libtool libxext-dev libncurses-dev xfonts-100dpi cython3 libopenmpi-dev zlib1g-dev

Activating the environnement and installation the required packages:

    micromamba activate nrv-env
    micromamba install -c conda-forge fenics-dolfinx==0.8.0  sysroot_linux-64=2.17 mpg

Last, one can pip-install NRV:

    pip install nrv-py


The WSL2 terminal must be rebooted before using NRV.
