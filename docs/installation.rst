Installation
============



Installation Step-by-Step
-------------------------

.. seealso::
    If you want to quickly create a mamba/micromamba environment where you can run NRV, look at `Quick installation <installation.html#quick-installation>`_


NRV is pip-installable and the whole installation process should be quite simple. However, to prevent third-party package version conflicts, we recommend creating a dedicated conda environment:

.. code:: bash

    conda create -n nrv-env -c anaconda python=3.12 

.. Tip::
    You can also use `Mamba or Micromamba <https://mamba.readthedocs.io/en/latest/>`_ to speed up the installation. Once Mamba is installed, the installation command line is almost identical:

    .. code:: bash

        mamba create -n nrv-env -c anaconda python=3.12 

Then activate it before any installation with the command:

.. code:: bash

    conda activate nrv-env

.. Warning:: 
    **For macOS users (June 2025):** 
    There are known compatibility issues between Xcode versions **higher than 16.2** and the FEM solver used in this project.  
    If you encounter problems running simulations involving FEM, please **downgrade Xcode to version 16.2** to ensure stability and correct functionality.  


Dependencies
------------

Open-Source Third-Party Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The pip installation takes care of most of the open-source third-party dependencies, but the FEM solver (`FenicsX <http://https://fenicsproject.org/.org>`_) and the Message Passing Interface (`MPICH <https://www.mpich.org/>`_)
are only installable via conda. We also recommend installing gmsh and ipython from conda.

.. code:: bash

    conda install -c conda-forge::mpi4py fenics-dolfinx==0.9.0 python-gmsh ipykernel

.. Warning::
    For Linux users, the default `blas` library used in `FenicsX` may not be compatible with the preconditioner used in NRV, which may result in unnecessary CPU overhead during electric field computation. To avoid this, it is advised to force the installation as below.

    .. code:: bash

        conda install -c conda-forge mpi4py fenics-dolfinx==0.9.0 libblas=*=*blis python-gmsh ipykernel

.. Tip::
    With Mamba, the command is:

    .. code:: bash

        mamba install -c conda-forge mpi4py fenics-dolfinx==0.9.0 python-gmsh ipykernel

COMSOL Installation
^^^^^^^^^^^^^^^^^^^

NRV can perform FEM computations with COMSOL. However, the end user must provide a valid commercial license. COMSOL can be installed before or after NRV. To use COMSOL, information about the installation must be specified in the ``nrv/_misc`` code folder by filling in the following fields in the ``NRV.ini`` file:
::

    [COMSOL]
    COMSOL_STATUS = True
    COMSOL_SERVER = PATH_TO_COMSOL_SERVER_BINARIES
    COMSOL_CPU = 1
    COMSOL_PORT = 2036
    TIME_COMSOL_SERVER_LAUNCH = 10
 
In particular, the correct path to the COMSOL server binaries must be specified, and the port must be adapted if it differs from the default value.

The use of FenicsX for FEM computations has been extensively tested by NRV contributors, and we do not recommend using COMSOL with NRV, as new geometries or electrodes will not be implemented with COMSOL. Also, the use of commercial licenses limits reproducibility and open-science possibilities.

Installing NRV
--------------

Using pip
^^^^^^^^^

NRV can simply be installed with pip (`nrv-py <https://pypi.org/project/nrv-py/>`_):

.. code:: bash

    pip install nrv-py

If you want the latest development version, please consider:

.. code:: bash

    pip install git+https://github.com/fkolbl/NRV.git 

If you already installed a previous version and want to upgrade to the latest development version, please use:

.. code:: bash

    pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git

You should now be able to import nrv in your Python shell:

.. code:: python3

    import nrv

Be aware that on the first import of NRV, some files related to ion-channel simulation are automatically compiled by NEURON. You may see the results of the compilation on your prompt, including warnings but no errors.

Using Docker
^^^^^^^^^^^^

This method should be preferred, as all dependencies are already set up. Note that in this configuration, COMSOL cannot be used. Assuming that Docker is already installed, the first step is to pull the image:

.. code:: bash

    docker pull nrvframework/nrv

You can then create a new container using:

.. code:: bash

    docker run --rm -it nrvframwork/nrv

where the ``--rm`` argument removes the container once finished, and ``-it`` provides an interactive console.
A second image is available to use NRV in Jupyter notebooks:

.. code:: bash

    docker pull nrvframework/lab

You can then create a container using:

.. code:: bash

    docker run --rm -p 8888:8888 nrvframework/lab

Here, ``-p 8888:8888`` maps the port to the local host. This should give you a link and token to open Jupyter in your browser.

NRV on Windows
^^^^^^^^^^^^^^

NRV is not directly installable on Windows due to some FenicsX dependencies not being available on Windows.
However, this problem can easily be overcome by using (`WSL2 <https://learn.microsoft.com/en-us/windows/wsl/install>`_). Assuming a blank WSL2 installation (Ubuntu 22.xx), the following instructions are required to install and use NRV.

Installation of `micromamba <https://github.com/mamba-org/mamba>`_ (a lighter and faster conda equivalent):

.. code:: bash

    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)

Creation of the environment:

.. code:: bash

    micromamba create -n nrv-env -c anaconda python=3.12 

Update with sudo and install the required libraries:

.. code:: bash

    sudo apt-get update -y
    sudo apt-get install build-essential libglu1-mesa libxi-dev libxmu-dev libglu1-mesa-dev libxrender1 libxcursor1 libxft2 libxinerama1 make libx11-dev git bison flex automake libtool libxext-dev libncurses-dev xfonts-100dpi cython3 libopenmpi-dev zlib1g-dev

Activate the environment and install the required packages:

.. code:: bash

    micromamba activate nrv-env
    micromamba install -c conda-forge fenics-dolfinx==0.9.0  sysroot_linux-64=2.17 mpich python-gmsh ipykernel

Finally, NRV can be installed with pip:

.. code:: bash
    
    pip install nrv-py


The WSL2 terminal must be rebooted before using NRV.

Quick Installation
------------------

A simpler installation method has been available since ``NRV-v1.2.2``. The goal is to create a new mamba or micromamba environment from recipes stored in ``.yaml`` files in the GitHub repository.

.. warning:: 
    This method has not been extensively tested yet. If any errors occur, please report them and use the standard method detailed `above <installation.html#installation-step-by-step>`_.

On Linux
^^^^^^^^

.. code:: bash
    curl -L -o env.yaml https://raw.githubusercontent.com/nrv-framework/NRV/refs/heads/master/conda/nrv_linux.yaml
    mamba env create -f env.yaml
    rm env.yaml

On macOS
^^^^^^^^

.. code:: bash
    curl -L -o env.yaml https://raw.githubusercontent.com/nrv-framework/NRV/refs/heads/master/conda/nrv_macos.yaml
    mamba env create -f env.yaml
    rm env.yaml

.. Tip::
    In both cases you can test the installation using (note that this command could take longer to execute as ``nrv`` is imported for the first time):

    .. code:: bash
        mamba run -n nrv python -c "import nrv; print(nrv.__version__)"
