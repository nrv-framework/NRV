Installation
============

NRV is pip installable and the hole process should be quite simple. However, to prevent from third packages version conflict we recommend to create a dedicated conda environnement: 
::

    conda create -n nrv-env

and activate it before any installation with the command: 
::

    conda activate nrv-env

Even if the pip installation can take care of dependncies, somes third party librairy are safer to install with conda instead of pip, please consider the following method for a successfull use of NRV.

Dependencies
------------

Open source third-party Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First install latest versions of common scientific librairies, as well as numba (for code acceleration) and icecream for debug: 
::

    conda install -c conda-forge mpi4py matplotlib numba scipy icecream

Then install everything for open source FEM computation with FENICS and GMSH:
::

    conda install -c conda-forge fenics-dolfinx mpich python-gmsh pyvista

Then, install additional packages from pip, *and only these ones*:
::

    pip install mph ezdxf neuron

COMSOL Installation
^^^^^^^^^^^^^^^^^^^

NRV can perform computations of FEM with COMSOL. However, the end user has to provide a valid commercial installed licence by its own. COMSOL installation can be performed before or after NRV's installation. For using COMSOL, informations about the install must be specified in the ''nrv/_misc'' code folder, by filling the following fields in the ''NRV.ini'' file:
::

    [COMSOL]
    COMSOL_STATUS = True
    COMSOL_SERVER = PATH_TO_COMSOL_SERVER_BINARIES
    COMSOL_CPU = 1
    COMSOL_PORT = 2036
    TIME_COMSOL_SERVER_LAUNCH = 10
 
Espcially, the correct path to the COMSOL server binaries has to be specified, the port has to be adapted if changed from default values.

The use of FenicsX for FEM computations have been repeatedely tested by NRV's contributor, and we do not recommend to use COMSOL with NRV as novel geometries or electrode won't be implemented for COMSOL. Also, the use of commercial licences limits the reproducibility and open-science possibilities.

Installing NRV
--------------

Using pip
^^^^^^^^^

NRV can simply be installed with pip:
:: 

    pip install nrv-py

if you want the very last development version under developpement, please consider:
::

    ​​pip install git+https://github.com/fkolbl/NRV.git 

if you already installed a previous version and want to upgrade to the very last development version, please use:
::

    pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git

You should be now able to import nrv in your python shell:
::

    import nrv

which should return to the prompt the number of processors used to launch the package. Be aware that on the first import of NRV, some files related to simulation of ion channel are automatically compiled by NEURON, you may see the results of the compilation (including warning, but no errors) on your prompt. 

Using docker
^^^^^^^^^^^^

This method should be prefered as all dependencies are already setup. Note that in this configuration, COMSOL cannot be used. Assuming that docker is already installed, the first step is to pull the image:
::

    docker pull nrvframework/nrv

You can then use create a new container using:
::

    docker run --rm -it nrvframwork/nrv

where the --rm argument suppress the container once finished, and -it gives the interactive console. 
A second image is available to use NRV in Jupyter notebooks:
::

    docker pull nrvframework/lab

You can then creat a container using:
::

    docker run --rm -p 8888:8888 nrvframework/lab

where the -p 8888:8888 maps the port to the local host. This should give you a link and token to load Jupyter from your browser.