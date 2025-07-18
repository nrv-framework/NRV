=================
Axons populations
=================

`Simulable` objects are either single axons, fascicles and nerve. The last two contain one more many axons. Since version 1.2.2, NRV has a dedicated object to store and handle populations, aiming at simplifying the operations associated with large number of axons. 

An empty population can be created with an instance of the class :class:`~nrv.nmod.axon_population`. This object basically couples a list of simulable axons with a geometry (automatically used in FEM simulations). To create new populations of axons, NRV comes with different methods for the two steps described below:

1. **Population Generation**: with tools for automated generation of populations with controlled diameters, based on experimental observations.

2. **Population Placement**: with Placing and Packing algorithms that shuffles the generated population spacialy, and that shuffles nodes of Ranvier for myelinated fibers.


.. tip::

    A simple way to see a :class:`~nrv.nmod.axon_population` (``axon_population.geom``) instance is as a :class:`~nrv.utils.geom.CShape` coupled with a :class:`pandas.DataFrame` (``axon_population.axon_pop``).
         - The fist defining where axons can be placed.
         - The second gather axons properties and flags to target subpopulation of axons.


The :class:`pandas.DataFrame` ``axon_population.axon_pop`` contains the following information:
  .. list-table:: columns of `axon_population.axon_pop` DataFrame
    :widths: 10 10 50 10
    :header-rows: 1

    * - Column label
      - type
      - Description
      - Flag
  
    * - ``"types"``
      - ``int``
      - Myelination of the axon (0: unmyelinated, 1: myelinated)
      - :attr:`~nrv.nmod.axon_population.has_pop`

    * - ``"diameters"``
      - ``float``
      - Diameter of the axon in :math:`\mu m`
      - :attr:`~nrv.nmod.axon_population.has_pop`

    * - ``"y"``
      - ``float``
      - y-position of the axon in :math:`\mu m`
      - :attr:`~nrv.nmod.axon_population.has_placed_pop`

    * - ``"z"``
      - ``float``
      - z-position of the axon in :math:`\mu m`
      - :attr:`~nrv.nmod.axon_population.has_placed_pop`

    * - ``"is_placed"``
      - ``bool``
      - True is the axon is placed in the geometry
      - :attr:`~nrv.nmod.axon_population.has_placed_pop`

    * - ``"node_shft"``
      - ``float``
      - Relative x-shift of the myelinated node of Ranviers
      - :attr:`~nrv.nmod.axon_population.has_node_shift`

    * - ...
      - ``bool``
      - Additional mask add with :meth:`~nrv.nmod.axon_population.add_mask`
      - `-`



.. note::
    The `Flag` column of this table is a built-in property of :class:`~nrv.nmod.axon_population` returning ``True`` if the property is already defined.




Population generation
=====================

There are several ways of using/creating populations:

- NRV contains some populations and placed populations already defined. Since version 1.2.2, its is easy and fast to generate new populations, these populations should be use for educational scripts only.
- a population can be generated using a distribution probability,
- a population can be generated from data (stored in various formats)

A simple example of compact code is given in the examples (see :doc:`example 20 <../examples/generic/20_create_population>`)

.. seealso::
    :doc:`Example 20 <../examples/generic/20_create_population>` --- Axon population generation.

Generate a population from data
-------------------------------

.. tip::
    It is also possible to use already created and placed populations of fibers as shown bellow.

It is possible to generate a desired population give two iterables, describing both the axon myelination (`1` or `True` for myelinated axons, `0` or `False` for unmyelinated axons) and the axons diameters. These iterables can be:

- tuples, in this case, the following syntax should be used, with `ax_type` and `ax_diameters` two one dimentional array-like or iterables
    .. code-block:: python

        import nrv
        pop = nrv.axon_population()
        pop.create_population_from_data((ax_type, ax_diameters))

- with a unique numpy array combining both myelination and diameters following the next syntax:
    .. code-block:: python

        import numpy as np
        data = np.vstack((ax_type, ax_diameters))
        pop = axon_population()
        pop.create_population_from_data(data)

- with a dictionnary containing `ax_type` and `ax_diameters` two one dimentional array-like or iterables at the keys `types` and `diameter` respectively, like in the syntax:
    .. code-block:: python

        data = {"types":ax_type, "diameters":ax_diameters, "other_key":0}
        pop = axon_population()
        pop.create_population_from_data(data)

- with a `pandas` dataframe also containing`ax_type` and `ax_diameters` two one dimentional array-like or iterables at the keys `types` and `diameter` respectively, like in the syntax:
    .. code-block:: python

        from pandas import DataFrame
        data =  DataFrame({"types":ax_type, "diameters":ax_diameters, "other_key":np.random.rand(len(ax_type))})
        pop = axon_population()
        pop.create_population_from_data(data)

Create *ex-novo* populations (recommended method)
-------------------------------------------------

To create a new population of fibers from scratch, you can use the method :meth:`~nrv.nmod.axon_population.create_population_from_stat`. This method will directly feed:

- the population's axon diameters (in :math:`\mu m`).
- the population axon types, where ``1.0`` corresponds to myelinated fibers and ``0.0`` to unmyelinated fibers.
    .. code-block:: python

        pop.create_population_from_stat(n_ax=100)


The arguments for the function are:

- ``n_ax`` (``int``): Number of axons to generate in the population (both myelinated and unmyelinated).
- ``percent_unmyel`` (``float``): Ratio of unmyelinated axons in the population. Must be between 0 and 1.
- ``M_stat`` (``str``): Name of the statistical distribution in the library, or a path to a custom CSV file containing myelinated fiber diameter statistics.
- ``U_stat`` (``str``): Name of the statistical distribution in the library, or a path to a custom CSV file containing unmyelinated fiber diameter statistics.

There are predefined statistical distributions available for unmyelinated fibers, derived from literature. These distributions are interpolated and used as random generators for axon diameters.

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

The script use to plot those histograms is made available in the :doc:`examples list<../examples/generic/13_axon_distributions>`

The scientific references used are:

- [stat1] Ochoa, J., & Mair, W. G. P. (1969). The normal sural nerve in man: I. Ultrastructure and numbers of fibres and cells. Acta neuropathologica, 13, 197-216.

- [stat2] Jacobs, J. M., & Love, S. (1985). Qualitative and quantitative morphology of human sural nerve at different ages. Brain, 108(4), 897-924.

- [stat3] Schellens, R. L., van Veen, B. K., Gabreëls‐Festen, A. A., Notermans, S. L., van't Hof, M. A., & Stegeman, D. F. (1993). A statistical approach to fiber diameter distribution in human sural nerve. Muscle & Nerve: Official Journal of the American Association of Electrodiagnostic Medicine, 16(12), 1342-1350.


.. tip::

    To define a new statistical law, you should store it in a `csv` files with two columns:

    1. Starting value of the bin for diameter histogram.
    2. Value of the probability for the corresponding bin

    The length of the bins is automatically determined by two successive values. Note last bin is the same size as previous one. Sum of probabilities is automatically normalized to 1.
    Users can find the predefined statistics at the path ``nrv/_misc/stats/``. Adding files to this folder make the statistics accessible by the filname without the extension. It is also possible to specify the statistics with a string beeing the path to the specific file.

Axon population already existing in NRV
---------------------------------------

Populations of axons are stored in the framework under the path ``nrv/_misc/pops`` as ``.pop`` files. These files follow a CSV-like structure with the following columns:

.. list-table:: 
   :header-rows: 1

   * - Fiber diameter
     - Fiber type
     - Not a Number
     - Not a Number
   * - (in µm)
     - (1.0 for myelinated / 0.0 for unmyelinated)
     - (`NaN`)
     - (`NaN`)

.. note::
    The last two columns are placeholders used to maintain compatibility with placed populations (see below) and to ensure consistent data formatting in the code.

Six predefined unplaced populations are available, corresponding to different total numbers of axons: 100, 200, 500, 1000, 2000, and 5000.

Population placement
====================

The second step to fully define the :class:`~nrv.nmod.axon_population` consist in positioning the fibres. As for the generation, this can be done:

- Using building randomized methods,
- From data (stored in various formats)

.. seealso::
    :doc:`Example 21 <../examples/generic/21_place_population>` --- Axon population placement.

Axon placed population already existing in NRV
----------------------------------------------

Placed populations of axons are stored under the path ``nrv/_misc/pops`` in ``.pop`` files. These files are similar to CSV files and contain the following columns:

.. list-table:: 
   :header-rows: 1

   * - Fiber diameter
     - Fiber type
     - y-axis coordinate
     - z-axis coordinate
   * - (in µm)
     - (1.0 for myelinated / 0.0 for unmyelinated)
     - (in µm)
     - (in µm)

Six predefined placed populations are available, corresponding to different total numbers of axons: 100, 200, 500, 1000, 2000, and 5000.



Axon Placing and Packing
------------------------

Once generated, the population have to be spacialy distributed, i.e. fibers are automatically placed on the y-z plane with a given proximity and with no overlap. This can be done using two methods:

- **Axon placing**: This method places the fibers on random positions, ensuring that they do not overlap and that they respect a minimal distance between them.
- **Axon packing**: This method places the fibers on a grid and then iteratively moves them towards a gravity center, ensuring that they do not overlap and that they respect a minimal distance between them.

If the packing method is the one that has been historically used in the framework, the placing method is a new addition that allows for faster operations and is more suitable for large populations. The placing method is also more flexible, as it allows for the placement of fibers in a specific area of the grid, while the packing method is more suitable for creating a compact population.

Axon Placing
^^^^^^^^^^^^

Axon placing is performed with a single function called :meth:`~nrv.nmod.placer`, which is designed to interface with the :meth:`~nrv.nmod.create_axon_population` function detailed previously. The placer function takes care of distributing the fibers on the y-z plane, ensuring that they do not overlap and that they respect a minimal distance between them.

Axon Packing
^^^^^^^^^^^^


Starting on a grid, axons are automatically migrated in the direction of a so-called gravity center during a number of iterations. At each step, a velocity for each axon is computed, considering the attraction to the gravity center and the collisions that can occur between cells with a minimal distance to respect between fibers. The animation below is an example of population packing.

.. image:: ../images/packing_anim.gif

The packing is performed with a single function called :meth:`~nrv.nmod.axon_packer`, and the function is designed to interface with the :meth:`~nrv.nmod.create_axon_population` function detailed previously. 

.. important::
    The packer only works with circular geometry, not with ellipses neither with generic polygons, and is not recommended. It is maintained mostly for backward compatibility. If the algorithms seems elegant, we noticed that sometimes unmyelinated axons aggregates around myelinated ones, in a strange fashion. It turns out that the placer does not have this behaviour and is computationally much more efficient, especially for large populations. USE PACKING AT YOUR OWN RISK.

Interacting with populations
============================

Basic methods
-------------

Methods have been implemented to interact with population in an easy way. If you need to remove some information, two methods for clearing data are implemented:

- `clear_population` that basically get back to an empty population,
- `clear_population_placement` that removes all geometrical properties of the population (generated by the placer/packer).

to handle the placement of axons, two geometrical operations have been implemented:

- a `rotate` method,
- a `translate` method.

A population can be plot using the `plot` method that takes as parameter the axes of a `matplotlib` figure.

Populations as DataFrames and playing with masks
------------------------------------------------

More importantly, the structure of an `NRV` population is based on `pandas` DataFrames. Theerefore, it is possible for postprocessing of results to:

- evaluate conditional expression with the `plot` method,
- add a mask (with the method `add_mask`) to automatically select a subgroup of the population. When a mask is added, it is associated with a label that can be reused for other operations.

.. seealso::
    :doc:`Example 22 <../examples/generic/22_access_subpopulation>` --- Handling subpopulation of axons.

    :doc:`Example 23 <../examples/generic/23_subpop_iclamp>` --- Attach a current clamp to specific subpopulation of axons.