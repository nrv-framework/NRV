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

First install latest versions of common scientific librairies, as well as numba (for code acceleration) and icecream for debug: 
::

    conda install -c conda-forge mpi4py matplotlib numba scipy icecream

Then install everything for open source FEM computation with FENICS and GMSH:
::

    conda install -c conda-forge fenics-dolfinx mpich python-gmsh pyvista

Then, install additional packages from pip, *and only these ones*:
::

    pip install mph ezdxf neuron

Installing NRV
--------------

NRV can simply be installed with pip:
:: 

    pip install nrv-py

if you want the very last development version under developpement, please consider:
::

    ​​pip install git+https://github.com/fkolbl/NRV.git 

if you already installed a previous version and want to upgrade to the very last development version, please use:
::

    pip install --upgrade --force-reinstall --ignore-installed git+https://github.com/fkolbl/NRV.git


Testing installation
--------------------

You should be now able to import nrv in your python shell:
::

    import nrv

which should return to the prompt the number of processors used to launch the package. Be aware that on the first import of NRV, some files related to simulation of ion channel are automatically compiled by NEURON, you may see the results of the compilation (including warning, but no errors) on your prompt. 