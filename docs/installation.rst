Installation
============

NRV is pip installable and the whole installation process should be quite simple. However, to prevent from third packages version conflict we recommend to create a dedicated conda environnement: 

.. code:: bash

    conda create -n nrv-env -c anaconda python=3.12 

.. Tip::
    You can also use `Mamba <https://mamba.readthedocs.io/en/latest/>`_ to speed up the installation. Once Mamba is installed, the installation command line is almost identical:

    .. code:: bash

        mamba create -n nrv-env -c anaconda python=3.12 

and activate it before any installation with the command: 

.. code:: bash

    conda activate nrv-env

.. Warning:: 
    **For macOS users (June 2025):** 
    There are known compatibility issues between Xcode versions **higher than 16.2** and the FEM solver used in this project.  
    If you encounter problems running simulations involving FEM, please **downgrade Xcode to version 16.2** to ensure stability and correct functionality.  


Dependencies
------------

Open source third-party Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The pip installation takes care of most of the open source third-party dependencies, but the FEM solver (`FenicsX <http://https://fenicsproject.org/.org>`_) and the Message Passing Interface (`MPICH <https://www.mpich.org/>`_)
are conda-installable only. We also recommend to install gmsh and ipython from conda.

.. code:: bash

    conda install -c conda-forge fenics-dolfinx==0.9.0 mpich python-gmsh ipykernel

.. Warning::
    For Linux users, the default `blas` library used in `FenicsX` may not be compatible with the preconditioner used in NRV, which may result in necessary CPU overhead during electric field computation. To avoid this it is thus advised to force the installation as bellow

    .. code:: bash

        conda install -c conda-forge fenics-dolfinx "libblas=*=*blis"

.. Tip::
    With Mamba, the command is:

    .. code:: bash

        mamba install -c conda-forge fenics-dolfinx==0.9.0 mpich python-gmsh ipykernel

COMSOL Installation
^^^^^^^^^^^^^^^^^^^

NRV can perform computations of FEM with COMSOL. However, the end user has to provide a valid commercial installed license by its own. COMSOL installation can be performed before or after NRV's installation. For using COMSOL, information about the installation must be specified in the ''nrv/_misc'' code folder, by filling the following fields in the ''NRV.ini'' file:
::

    [COMSOL]
    COMSOL_STATUS = True
    COMSOL_SERVER = PATH_TO_COMSOL_SERVER_BINARIES
    COMSOL_CPU = 1
    COMSOL_PORT = 2036
    TIME_COMSOL_SERVER_LAUNCH = 10
 
Especially, the correct path to the COMSOL server binaries has to be specified, the port has to be adapted if changed from default values.

The use of FenicsX for FEM computations have been extensively tested by NRV's contributor, and we do not recommend to use COMSOL with NRV as new geometries or electrode won't be implemented with COMSOL. Also, the use of commercial licenses limits the reproducibility and open-science possibilities.

Installing NRV
--------------

Using pip
^^^^^^^^^

NRV can simply be installed with pip (`nrv-py <https://pypi.org/project/nrv-py/>`_):

.. code:: bash

    pip install nrv-py

if you want the very last development version under development, please consider:

.. code:: bash

    pip install git+https://github.com/fkolbl/NRV.git 

if you already installed a previous version and want to upgrade to the very last development version, please use:

.. code:: bash

    pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git

You should be now able to import nrv in your python shell:

.. code:: python3

    import nrv

Be aware that on the first import of NRV, some files related to simulation of ion channels are automatically compiled by NEURON, you may see the results of the compilation (including warning, but no errors) on your prompt. 

Using docker
^^^^^^^^^^^^

This method should be preferred as all dependencies are already setup. Note that in this configuration, COMSOL cannot be used. Assuming that docker is already installed, the first step is to pull the image:

.. code:: bash

    docker pull nrvframework/nrv

You can then use create a new container using:

.. code:: bash

    docker run --rm -it nrvframwork/nrv

where the --rm argument suppress the container once finished, and -it gives the interactive console. 
A second image is available to use NRV in Jupyter notebooks:

.. code:: bash

    docker pull nrvframework/lab

You can then create a container using:

.. code:: bash

    docker run --rm -p 8888:8888 nrvframework/lab

Where the -p 8888:8888 maps the port to the local host. This should give you a link and token to load Jupyter from your browser.

NRV on Windows
^^^^^^^^^^^^^^

NRV is not directly installable on Windows due to some FenicsX dependencies not available on windows. 
However one can easily overcome this problem by using (`WLS2 <https://learn.microsoft.com/en-us/windows/wsl/install>`_). Assuming a blank installation of WLS2 (Ubuntu 22.xx), the following instruction are required to install and use NRV.

Installation of `micromamba <https://github.com/mamba-org/mamba>`_ (a lighter and faster conda equivalent):

.. code:: bash

    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)

Creation of the environnement: 

.. code:: bash

    micromamba create -n nrv-env -c anaconda python=3.12 

Sudo update and installation of the required libs:

.. code:: bash

    sudo apt-get update -y
    sudo apt-get install build-essential libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev libxrender1 libxcursor1 libxft2 libxinerama1 make libx11-dev git bison flex automake libtool libxext-dev libncurses-dev xfonts-100dpi cython3 libopenmpi-dev zlib1g-dev

Activating the environnement and installation the required packages:

.. code:: bash

    micromamba activate nrv-env
    micromamba install -c conda-forge fenics-dolfinx==0.9.0  sysroot_linux-64=2.17 mpg mpich python-gmsh ipykernel

Last, one can pip-install NRV:

.. code:: bash
    
    pip install nrv-py


The WSL2 terminal must be rebooted before using NRV.
