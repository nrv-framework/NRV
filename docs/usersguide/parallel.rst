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

At version 1.x.x, the multi-core splitting is handled using the Message Passing Interface (MPI) and the python available library ``mpi4py``. However, this package is not a mandatory requirement for NRV to work: if not installed, the package will only work in single-core mode, without raising any exception nor warning. If correctly installed, the user can specify a number of cores when launching the python scripts, and job splitting is handled internally.

An example with a benchmark script
==================================
In order to illustrate how large computation can be handled, we provide a benchmark example that consist in two files:

- here is a first python script :download:`for nerve generation ('gen_nerve_benchmark.py') <../scripts/gen_nerve_benchmark.py>`. This script generates a nerve filled with an axon population. The nerve and all geometrical parameters, electrodes and stimuli is saved to a ``.json`` file. This step is not computationally expensive, except for the population generation and packing (see perspectives). For the moment, this is launched in single-core mode

- here is a second python script :download:`with the simulation ('nerve_benchmark.py') <../scripts/nerve_benchmark.py>`. This scripts contains the simulation and post-processing. One can remark a test on function ``nrv.MCH.do_master_only_work()``. This is only true on the CPU core with the lowest rank, defining the so-called *master-core*. The code bellow this instruction is then executed in single-core mode (in the present example, it corresponds to the post-processing).

To launch the code in single core mode, simply use in the command line:

::

    python gen_nerve_benchmark.py
    python nerve_benchmark.py

To launch the code using several cores for the simulation (here an example on 8 cores):

::

    python gen_nerve_benchmark.py
    mpirun -n 8 python nerve_benchmark.py

no code adaptation is required. The test on ``nrv.MCH.do_master_only_work()`` can appear unfamiliar to end user, to ease process of parallel computation, we propose two alternatives (with the same results) in the next section.

Pythonic tools and perspectives
===============================

Few internall tools have been develop to ease the process of launching large computations, described here below. We also express our wishes as developer for future versions.

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
