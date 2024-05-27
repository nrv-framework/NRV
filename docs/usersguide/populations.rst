==========================
Generate axons populations
==========================

Previously simulable objects consists in axons, fascicles and nerve. The last two contain several axons. To create new populations of axons, NRV comes with two functionalities described below:

- Tools for automated generation of populations with controlled diameters, based on experimental observations.

- A packing algorithm that shuffles the generated population on the spacial grid, and that shuffles nodes of Ranvier for myelinated fibers.

It is also possible to use already created and placed populations of fibers:

- populations of axons are stored in the framework at the path ``nrv/_misc/pops`` in ``.pop`` files. These files are equivalents to CSV files with the following columns:

    1. Diameter of the fiber.

    2. The value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

    3. Not a Number (`Nan`).

    4. Not a Number (`Nan`).

The two last column are present to prevent from confusion with placed populations (see below) and code compatibility. There are 6 different populations for different total number of axons: 100, 200, 500, 1000, 2000, 5000.

- placed populations of axons are stored in the path ``nrv/_misc/pops`` in ``.pop`` files.These files are equivalents to CSV files with the following columns:

    1. Diameter of the fiber.

    2. The value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

    3. y-axis coordinate of the fiber.

    4. z-axis coordinate of the fiber.

There are 6 different populations for different total number of axons: 100, 200, 500, 1000, 2000, 5000.

Diameter distributions
======================

Create ex-novo population
-------------------------

To create ex-novo population of fibers, a function called ``create_axon_population`` can be used. This function returns:

- a list of axons diameters in :math:`\mu m`

- a list corresponding to axons type as: the value 1.0 for myelinated fibers, the value 0.0 for unmyelinated fibers.

- a list of the subgroup of myelinated fiber diameters,

- a list of the subgroup of myelinated fiber diameters,

The arguments for the function are:

- N: (``int``) the number of axon to generate for the population (nnmyelinated and myelinated)

- percent_unmyel: (``float``) ratio of unmyelinated axons in the population. Should be between 0 and 1.

- M_stat: (``str``) name of the statistic in the library or path to a new library in csv for myelinated diameter statistics.

- U_stat: (``str``) name of the statistic in the library or path to a new library in csv for unmyelinated diameter statistics.

There are predefined statistics taken from the litterature for unmyelinated fibers. These statistics are then interpolated and used as generators.

.. list-table:: pre-defined statistics for unmyelinated fibers
    :widths: 50 150
    :header-rows: 1
    :align: center

    *   - Name
        - scientific source and comment
    *   - "Ochoa_U"
        - From human normal sural nerve, scientific reference [stat1]
    *   - "Jacobs_11_A"
        - From human normal sural nerve, scientific reference [stat2]
    *   - "Jacobs_11_B"
        - From human normal sural nerve, scientific reference [stat2]
    *   - "Jacobs_11_C"
        - From human normal sural nerve, scientific reference [stat2]
    *   - "Jacobs_11_D"
        - From human normal sural nerve, scientific reference [stat2]

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
        - From human normal sural nerve, scientific reference [stat3]
    *   - "Schellens_2"
        - From human normal sural nerve, scientific reference [stat3]
    *   - "Ochoa_M"
        - Statistics from human normal sural nerve, scientific reference [stat1]
    *   - "Jacobs_9_A"
        - From human normal sural nerve, scientific reference [stat2]
    *   - "Jacobs_9_B"
        - From human normal sural nerve, scientific reference [stat2]

These statistics (grey curves), and their interpolations in NRV (blue curves) and an example of generated population histogramm are depicted in the figure bellow:

.. image:: ../images/distributions_myelinated.png

The scientific references used are:

- [stat1] Ochoa, J., & Mair, W. G. P. (1969). The normal sural nerve in man: I. Ultrastructure and numbers of fibres and cells. Acta neuropathologica, 13, 197-216.

- [stat2] Jacobs, J. M., & Love, S. (1985). Qualitative and quantitative morphology of human sural nerve at different ages. Brain, 108(4), 897-924.

- [stat3] Schellens, R. L., van Veen, B. K., Gabreëls‐Festen, A. A., Notermans, S. L., van't Hof, M. A., & Stegeman, D. F. (1993). A statistical approach to fiber diameter distribution in human sural nerve. Muscle & Nerve: Official Journal of the American Association of Electrodiagnostic Medicine, 16(12), 1342-1350.


Describe a new statistical law
------------------------------

Predefined statistics are simple csv files with two columns:

1. Starting value of the bin for diameter histogram.

2. Value of the probability for the corresponding bin

The length of the bins is automatically determined by two successive values. Note last bin is the same size as previous one. Sum of probabilities is automatically normalized to 1.

Users can find the predefined statistics at the path ``nrv/_misc/stats/``. Adding files to this folder make the statistics accessible by the filname without the extension. It is also possible to specify the statistics with a string beeing the path to the specific file.


Axon Packing
============

Once generated, the population can be packed, i.e. fibers are automatically placed on the y-z plane with a given proximity and with no overlap. Starting on a grid, axons are automatically migrated in the direction of a so-called gravity center during a number of iterations. At each step, a velocity for each axon is computed, considering the attraction to the gravity center and the collisions that can occur between cells with a minimal distance to respect between fibers. The animation below is an example of population packing:

.. image:: ../images/packing_anim.gif

the packing is performed with a single function called ``axon_packer``. This function returns:

- y_axons: (numpy.array) an array containing the y coordinates of axons, in :math:`\mu m``

- z_axons: (numpy.array) an array containing the z coordinates of axons, in :math:`\mu m``

This function is designed to interface with the ``create_axon_population`` detailed previously. Especially, the maint inputs of the ``axon_packer`` function are:

- diameters: np.array Array containing all the diameters of the axon population to pack

- y_gc: float y coordinate of the gravity center for the packing, in um

- z_gc: float z coordinate of the gravity center for the packing, in um

- delta: (float) minimal inter-axon distance to respect before considering collision, in um, (by default set to 0.5)

- n_iter: (int) Number of iterations (by default set to 20000, please note that **large population require more iterations**)

Some arguments of the algorithms can be tuned:

- v_att: float vector norm for attraction velocity, in um per iteration

- v_rep: float vector norm for repulsion velocity, in um per iteration

The process can be monitored (*monitoring used to generate the animation above as an example*), using the following arguments:

- monitor: (bool) monitor the packing algorithm by saving regularly plot of the population

- monitoring_Folder: (str) where to save the monitoring plots

- n_monitor: (int) number of iterration between two successive plots when monitoring the algorithm 


Interacting with populations
============================

It is also possible to plot the population on a ``matplotlib`` figure using the function ``plot_population``, with the follwing arguments:

- diameters: (numpy.array) diameters of the axons to display, in um

- y_axons: (numpy.array) y coordinate of the axons to display, in um

- z_axons: (numpy.array) z coordinate of the axons to display, in um

- ax: (matplotlib.axes) (sub-) plot of the matplotlib figure

- size: (float) size of the window as a square side, in um

- axon_type: (numpy.array) type of the axon (Myelinated = 1; Unmyelinated = 0) - Optionnal

- title: (str )title of the figure

- y_gc: (float) y coordinate of the gravity, in um

- z_gc: (float) z coordinate of the gravity, in um

Saving a placed population to a ``.ppop`` file can be done using the ``save_axon_population`` function, with the following parameters:

- f_name: (str) name of the file to store the population

- axons_diameters: (np.array) array containing the axons diameters

- axons_type: (np.array) array containing the axons type ('1' for myelinated, '0' for unmyelinated)

- y_axons: (np.array) y coordinate of the axons to store, in um

- z_axons: (np.array) z coordinate of the axons to store, in um

- comment: (str) comment added in the header of the file, optional

Loading a ``.ppop`` file can be done using the function ``load_axon_puplation`` taking as argument a string with the filename or path and returning:

- axons_diameters: (numpy.array) Array containing all the diameters of the generated axon population

- axons_type: (numpy.array) Array containing a '1' value for indexes where the axon is myelinated (A-delta or not), else '0'

- y_axons: (numpy.array) y coordinate of the axons, in um

- z_axons: (numpy.array) z coordinate of the axons, in um

- M_diam_list: (numpy.array) list of myelinated only diameters

- U_diam_list: (numpy.array) list of unmyelinated only diamters