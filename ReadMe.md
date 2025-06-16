[![PyPI version](https://badge.fury.io/py/nrv-py.svg)](https://badge.fury.io/py/nrv-py)
[![Documentation Status](https://readthedocs.org/projects/nrv/badge/?version=latest)](https://nrv.readthedocs.io/en/latest/?badge=latest)
[![License: CeCill](https://img.shields.io/badge/Licence-CeCill-blue )](https://github.com/fkolbl/NRV/blob/master/Licence.txt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10497741.svg)](https://doi.org/10.5281/zenodo.10497741)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nrv-framework/NRV-demo/main)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nrv-py)

<!---[![DOI](xxxx)](xxx)-->
<!---[![Build Status](xxxx)](xxx)-->

<img src="https://github.com/nrv-framework/NRV/blob/master/docs/__logo/logo.png" alt="NRV" width="50%" height="auto" class="center">

# NRV
*Python library for Peripheral Nervous System stimulation modeling*

NRV (or NeuRon Virtualizer) is a pythonic framework to enable fast and user friendly simulations of the Peripheral Nervous System. Axons models are simulated with the [NEURON](http://www.neuron.yale.edu/neuron) software, and extracellular fields are computed either from analytic equations such as point source approximation or with a more detailed description of the nerve and electrode geometry and Finite Elements Method, either using [COMSOL](https://www.comsol.com) (additional commercial licence requiered) or the [FENICS project](https://fenicsproject.org). All computations are performed with the quasistatic approximation of the Maxwell equations, no ephaptic coupling. Stimulation waveform can be of random shapes, and any kinds of electrode can be combined to model complex stimulation strategies.

NRV has been optimized for large population of axons, from generating correct population following a specific diameter repartition, through automatic placement to computation and post-processing of the axons activity when a stimulus is applied. Parallel computation, interface with NEURON and COMSOL and FENICS is automatically handled by NRV. For a detailed description and full help on installation, basic usage and API documentation, please visit ou [NRV readthedocs page](https://nrv.readthedocs.io/en/latest/).

NRV has been developped by contributors from the CELL research group at the Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University, until June 2023 and is now developped and maintained by the Bioelectronics group of laboratory IMS (UMR CNRS 5218), INP Bordeaux, U. Bordeaux.

📚 **Full Documentation available here**: [https://nrv.readthedocs.io/en/latest/](https://nrv.readthedocs.io/en/latest/)

## 📄 Citation

If you use **NRV** in your research, please cite the following paper:

Couppey, T., Regnacq, L., Giraud, R., Romain, O., Bornat, Y., & Kolbl, F. (2024). NRV: An open framework for in silico evaluation of peripheral nerve electrical stimulation strategies. PLOS Computational Biology, 20(7), e1011826.
> [https://doi.org/10.1371/journal.pcbi.1011826](https://doi.org/10.1371/journal.pcbi.1011826)

### BibTeX

```bibtex
@article{couppey2024nrv,
  title={NRV: An open framework for in silico evaluation of peripheral nerve electrical stimulation strategies},
  author={Couppey, Thomas and Regnacq, Louis and Giraud, Roland and Romain, Olivier and Bornat, Yannick and Kolbl, Florian},
  journal={PLOS Computational Biology},
  volume={20},
  number={7},
  pages={e1011826},
  year={2024},
  publisher={Public Library of Science San Francisco, CA USA}
}
```

## Installation


NRV is pip installable and the whole installation process should be quite simple. However, to prevent third-party package version conflicts we recommend creating a dedicated conda environment:



```bash
conda create -n nrv-env -c anaconda python=3.12
```

💡 **Tip:**
You can also use [Mamba](https://mamba.readthedocs.io/en/latest/) to speed up the installation. Once Mamba is installed, the installation command line is almost identical:  


``` bash

mamba create -n nrv-env -c anaconda python=3.12

```

 And activate it before any installation with the command:  

``` bash
conda activate nrv-env
```

⚠️ **Warning for macOS users (June 2025):**  
There are known compatibility issues between Xcode versions higher than 16.2 and the FEM solver used in this project.  
If you encounter problems running simulations involving FEM, please downgrade Xcode to version 16.2 to ensure stability and correct functionality.

### Open-source Dependencies


The pip installation takes care of most of the open source third-party dependencies, but the FEM solver ([FenicsX](https://fenicsproject.org/)) and the Message Passing Interface ([MPICH](https://www.mpich.org/))  
are conda-installable only. We also recommend installing gmsh and ipython from conda:



```bash
conda install -c conda-forge fenics-dolfinx==0.9.0 mpich python-gmsh ipykernel
```

⚠️ **Warning for Linux users:**  The default blas library used in FenicsX may not be compatible with the preconditioner used in NRV, which may result in additional CPU overhead during electric field computation.
To avoid this, it is advised to force the installation as below:

```bash
conda install -c conda-forge fenics-dolfinx "libblas=*=*blis"
```

💡 **Tip:**
With Mamba, the command is:

```bash
mamba install -c conda-forge fenics-dolfinx==0.9.0 mpich python-gmsh ipykernel
```

## COMSOL Installation
NRV can perform FEM computations with COMSOL. However, the end user must provide a valid commercial installed license by themselves. COMSOL installation can be performed before or after NRV's installation.

For using COMSOL, information about the installation must be specified in the nrv/_misc code folder by filling the following fields in the NRV.ini file:

```ini
[COMSOL]
COMSOL_STATUS = True
COMSOL_SERVER = PATH_TO_COMSOL_SERVER_BINARIES
COMSOL_CPU = 1
COMSOL_PORT = 2036
TIME_COMSOL_SERVER_LAUNCH = 10
```

Especially, the correct path to the COMSOL server binaries has to be specified, and the port must be adapted if changed from default values.

The use of FenicsX for FEM computations has been extensively tested by NRV's contributors, and we do not recommend using COMSOL with NRV as new geometries or electrodes won't be implemented with COMSOL. Also, the use of commercial licenses limits reproducibility and open-science possibilities.

### Installing NRV
Using pip
NRV can simply be installed with pip (nrv-py):

```bash
pip install nrv-py
```

If you want the very last development version under development, please consider:

```bash
pip install git+https://github.com/fkolbl/NRV.git
```

If you already installed a previous version and want to upgrade to the very last development version, please use:

```bash
pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git
```

You should now be able to import nrv in your Python shell:

```python
import nrv
```

Be aware that on the first import of NRV, some files related to simulation of ion channels are automatically compiled by NEURON. You may see compilation results (including warnings, but no errors) in your prompt.

### Using Docker
This method should be preferred as all dependencies are already set up. Note that in this configuration, COMSOL cannot be used.

Assuming Docker is already installed, the first step is to pull the image:

```bash
docker pull nrvframework/nrv
```

You can then create a new container using:

```bash
docker run --rm -it nrvframework/nrv
```

where the --rm argument deletes the container once finished, and -it gives the interactive console.

A second image is available to use NRV in Jupyter notebooks:

```bash
docker pull nrvframework/lab
```
You can then create a container using:

```bash
docker run --rm -p 8888:8888 nrvframework/lab
```
Where the -p 8888:8888 maps the port to the localhost. This should give you a link and token to load Jupyter from your browser.

### NRV on Windows
NRV is not directly installable on Windows due to some FenicsX dependencies not available on Windows.
However, one can easily overcome this problem by using WSL2.

💡 **Tip:** A full support of FenicsX on windows is planned! 

Assuming a blank installation of WSL2 (Ubuntu 22.xx), the following instructions are required to install and use NRV.

Installation of micromamba (a lighter and faster conda equivalent):

```bash
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
```
Creation of the environment:

```bash
micromamba create -n nrv-env -c anaconda python=3.12
```
Sudo update and installation of the required libraries:

```bash
sudo apt-get update -y
sudo apt-get install build-essential libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev libxrender1 libxcursor1 libxft2 libxinerama1 make libx11-dev git bison flex automake libtool libxext-dev libncurses-dev xfonts-100dpi cython3 libopenmpi-dev zlib1g-dev
```
Activating the environment and installing the required packages:

```bash
micromamba activate nrv-env
micromamba install -c conda-forge fenics-dolfinx==0.9.0 sysroot_linux-64=2.17 mpg mpich python-gmsh ipykernel
```
Finally, pip-install NRV:

```bash
pip install nrv-py
```
The WSL2 terminal must be rebooted before using NRV.
