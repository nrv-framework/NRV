==========================
Generate axons populations
==========================

Previously simulable objects consists in axons, fascicles and nerve. The last two contain several axons. To create new populations of axons, NRV comes with two functionalities described below:

- Tools for automated generation of populations with controlled diameters, based on experimental observations.

- A packing algorithm that shuffles the generated population on the spacial grid, and that shuffles nodes of Ranvier for myelinated fibers.

It is also possible to use already created and placed populations of fibers:

- populations of axons are stored in the framework at the path `nrv/_misc/pops` in `.pop` files. These files are equivalents to CSV files with the following columns:

    1. Diameter of the fiber.

    2. The value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

    3. Not a Number (`Nan`).

    4. Not a Number (`Nan`).

The two last column are present to prevent from confusion with placed populations (see below) and code compatibility. There are 6 different populations for different total number of axons: 100, 200, 500, 1000, 2000, 5000.

- placed populations of axons are stored in the path `nrv/_misc/pops` in `.pop` files.These files are equivalents to CSV files with the following columns:

    1. Diameter of the fiber.

    2. The value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

    3. y-axis coordinate of the fiber.

    4. z-axis coordinate of the fiber.

There are 6 different populations for different total number of axons: 100, 200, 500, 1000, 2000, 5000.

Diameter distributions
======================

Create ex-novo population
-------------------------

To create ex-novo population of fibers, a function called `create_axon_population` can be used. This function returns:

- a list of axons diameters in :math:`\mu m`

- a list corresponding to axons type as: the value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

- a list of the subgroup of myelinated fiber diameters,

- a list of the subgroup of myelinated fiber diameters,

The arguments for the function are:

- N: (`int`) the number of axon to generate for the population (nnmyelinated and myelinated)

- percent_unmyel: (`float`) ratio of unmyelinated axons in the population. Should be between 0 and 1.

- M_stat: (`str`) name of the statistic in the library or path to a new library in csv for myelinated diameter statistics.

- U_stat: (`str`) name of the statistic in the library or path to a new library in csv for unmyelinated diameter statistics.

There are predefined statistics taken from the litterature for unmyelinated fibers. These statistics are then interpolated and used as generators.

.. list-table:: pre-defined statistics for unmyelinated fibers
    :widths: 50 150
    :header-rows: 1
    :align: center

    *   - Name
        - scientific source and comment
    *   - "Ochoa_U"
        - scientific source and comment
    *   - "Jacobs_11_A"
        - scientific source and comment
    *   - "Jacobs_11_B"
        - scientific source and comment
    *   - "Jacobs_11_C"
        - scientific source and comment
    *   - "Jacobs_11_D"
        - scientific source and comment

These statistics (grey curves), and their interpolations in NRV (red curves) and an example of generated population histogramm are depicted in the figure bellow:

.. image:: ../images/distributions_unmyelinated.png

as well as for myelinated fibers:

.. list-table:: pre-defined statistics for myelinated fibers
    :widths: 50 150
    :header-rows: 1
    :align: center

    *   - Name
        - scientific source and comment
    *   - "Schellens_1"
        - scientific source and comment
    *   - "Schellens_2"
        - scientific source and comment
    *   - "Ochoa_M"
        - scientific source and comment
    *   - "Jacobs_9_A"
        - scientific source and comment
    *   - "Jacobs_9_B"
        - scientific source and comment

These statistics (grey curves), and their interpolations in NRV (blue curves) and an example of generated population histogramm are depicted in the figure bellow:

.. image:: ../images/distributions_myelinated.png

Describe a new statistical law
------------------------------


Axon Packing
============
cf tests unitaires + tutorials