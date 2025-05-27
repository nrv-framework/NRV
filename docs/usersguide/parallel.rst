====================
Parallel computation
====================

Rapid explanation
=================

NRV has been designed to enable parallel computing without changing the description of simulated problems. In the case of axon fibers simulation, if ephaptic coupling is neglected (interactions between fibers), the problem is called *embarrassingly parallel*, meaning that the behavior of individual fibers can be computed on different cores without inducing a need for communications between cores.

However, the computational load distribution is a bit more complex:

- FEM computations are not included in the former remark,

- For post-processing, the results of different axon simulations in a fascicle/nerve simulation are gathered, meaning a basic synchronicity between simulations.

- Axon population generation and packing are based on specific algorithms.

NRV aims at providing solutions for the end user, where the scalability of the simulation, from a few cells to large nerves does not imply user knowledge and considerations on these points are handled internally.

At this time of development, the following figure indicates what part of the process are fully parallelized:

.. image:: ../images/NRV_parallel.png

One have to note that the generation and packing of population is for the moment only on one core. Post-processing is usually performed on a limited number of cores, or at least separated from computations when performing large computation, we do not want to change this habit. However, in future versions, we plan to parallelize these task to limit execution time.

Before version 1.2, the multi-core splitting was handled using the Message Passing Interface (MPI). This is not the case anymore since version 1.2, where only the python standard API is used to handle parallelization. This means that NRV can be used on any computer, from a laptop to a cluster, without requiring any specific installation.

A huge effort has been made to ensure that axon generation and packing is fast and efficient, and that the user does not have to worry about the time spent by these steps even on populations around 1,000 axons or more on one core. The CPU dispatch of simulation is now fully invisible for the user, who can still specify the number of CPU for main computational steps in the ``NRV.ini`` file. The user can also specify the number of CPU used for each step in python file.

An example with a benchmark script
==================================
In order to illustrate how large computation can be handled, we provide an example of a nerve simulation. The script is ....



Pythonic tools and perspectives
===============================

Few internal tools have been developed to ease the process of launching large computations, described here below. We also express our wishes as developer for future versions.

Command line launching
----------------------

Once NRV is installed, the library also comes with a command line launcher called ``nrv2calm``. The exact meaning of this name is based on a pun word in french. This tools basically scan your code to evaluate if the computation should be parallel or not. It then calls correctly python with a predefined number of cores. As an example to launch a script called ``myscript.py`` with 4 cores, it is possible to write on command  line:

::

    nrv2calm -n 4 myscript.py

when not specified in the command line, the number of cores used for axon fibers parallelization is defined in the file ``nrv/_misc/NRV.ini``. In this file, the number of cores for each computational step can be specified:

.. list-table:: specifying the number of cores in the ini file
    :widths: 50 150
    :header-rows: 1
    :align: center

    *   - KEY
        - meaning and comment
    *   - FASCICLE_CPU
        - number of CPU used to distribute calls to NEURON
    *   - COMSOL_CPU
        - number of CPU used for comsol computations, Warning: this should correspond to the commercial licence you are using.
    *   - GMSH_CPU
        - number of CPU used for meshing with GMSH, we recommend with the current version of GMSH not to exceed 4 to get consistent results and limit meshing time.
    *   - FENICS_CPU
        - number of CPU used for FEM computation with FenicsX. For the moment, we recommend to keep 1, however computation with more CPU is possible. We still work on adapting the pre-conditioner and solver to the number of CPU to ensure consistent results.

Note that except the number of CPU used for calls to NEURON, these keys directly control the behavior of NRV for FEM and meshing, whatever the number of CPU given to MPI. This ensures optimal usage of third party libraries, and is automatically handled by NRV.

In order to force ``nrv2calm`` to launch in multi-core, it is possible to add the line ``#pragma parallel`` in the python script. If launched directly with the python interpreter, this ligne will be ignored and has no consequence on the script execution.

Isolate code that should not be parallelized
--------------------------------------------

It is possible to isolate code that has to run on a single code inside a script that will be launched in multi-cores. To do so, the code as to be placed in a function decorated with ``@singlecore``. As an example, here is a function that returns a placed population in a script launched in multi-cores, but that will execute only on a single CPU:

.. code:: ipython3

    import nrv

    @nrv.singlecore
    def generate_population(N):
        axons_diameters, _, _, _ = nrv.create_axon_population(N,
                                                              percent_unmyel=0.7,
                                                              M_stat="Ochoa_M",
                                                              U_stat="Ochoa_U",
                                                              )
        Y, Z = nrv.axon_packer(axons_diameters)
        return axons_diameters, Y, X

Developer's perspective
-----------------------

We are still working on the parallelization of computations by gaining experience in using the framework intensively:

- we hope to parallelize the population generation as well as the packing in future versions.

- we hope to improve the way FenicsX is used, by automatically choosing some simulation parameters (pre-conditioner, solver...) considering the computational load,

- we are on the process of designing more accurate decorators to write the simulation steps in functions and automatize better the job splitting strategy

- we currently design test-benches to automatically setup optimal parameters for individual machines (from laptop to clusters)

- we know that mpi4py is not a native python library, and we have in mind to use the library ``multiprocessing`` for better integration. This process is long, but part of our roadmap. Check the changelog if interested.
