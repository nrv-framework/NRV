Post-processing
===============

NRV provides dedicated objects and methods to facilitate simulation post-processing and analysis. This section describes how to use these features effectively.

NRV Result Objects
------------------

When executed, NRV :class:`~nrv.backend.NRV_simulable` objects return instances derived from the base class :class:`~nrv.backend.NRV_results`. Specifically:

- :class:`~nrv.nmod.axon` simulations return :class:`~nrv.nmod.results.axon_results` objects  
- :class:`~nrv.nmod.fascicle` simulations return :class:`~nrv.nmod.results.fascicle_results` objects  
- :class:`~nrv.nmod.nerve` simulations return :class:`~nrv.nmod.results.nerve_results` objects  

.. note::  
   Objects inheriting from :class:`~nrv.backend.NRV_results` behave both like Python objects and dictionaries. This means you can access their data using attribute or key syntax interchangeably:

   .. code-block:: python3

       val = my_result.my_key

   is equivalent to:

   .. code-block:: python3

       val = my_result['my_key']

These result objects store all relevant simulation parameters: for example, a :class:`~nrv.nmod.results.axon_results` object contains axon diameters, a :class:`~nrv.nmod.results.fascicle_results` object contains descriptions of axon populations, and a :class:`~nrv.nmod.results.nerve_results` object contains fascicle descriptions.  

Additionally, each result object includes a copy of the extracellular and intracellular simulation contexts for comprehensive analysis.

Detailed descriptions of these objects follow below.


Axon results
------------

The following table describes all the keys/member available in a :class:`~nrv.nmod.results.axon_results` object:

.. list-table:: axon_results key/member
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Key/Member
        - Type
        - content
    *   - `Simulation_state`
        - `str`
        - Final state of running :meth:`~nrv.nmod.axon.simulate` method. If 'Successful', then the simulation terminated without any error or interruption. Else set to "Unsuccessful".
    *   - `Error_from_prompt`
        - `str`
        - If the `simulation_state` is unsuccessful, this key contains the error message that has been returned (and that should also appear in the logfile).
    *   - `sim_time`
        - `float`
        - Final value of the simulation time, in ms
    *   - `Neuron_t_max`
        - `float`
        - Final timing achieved by the neuron solver once the simulation initiated, in ms.
    *   - `t`
        - `np.array`
        - Array of timesteps, in ms.
    *   - `x_rec`
        - `np.array`
        - Points in space along the x axis where simulation results are saved, in um.
    *   - `V_mem`
        - `np.array`
        - Values of membrane voltage with time at the recorded x axis positions stored in the `x_rec` key
    *   - `I_mem`
        - `np.array`
        - Values of membrane current with time at the recorded x axis positions stored in the `x_rec` key
    *   - `g_mem`
        - `np.array`
        - Small signal linearization of the membrane conductance with time at the recorded x axis positions stored in the `x_rec` key
    *   - `g_na`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_k`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Potassium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_l`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_na`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_k`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Potassium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_l`
        - `np.array`
        - For unmyelinated models "HH", "Rattay_Aberham" and "Sundt". Leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nav17`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.7 channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nav18`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.8 channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nav19`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.7 channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kA`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kM`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kdr`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kna`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_h`
        - `np.array`
        - For unmyelinated model "Tigerholm". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_naleak`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kleak`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nav17`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.7 channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nav18`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.8 channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nav19`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium NAV1.7 channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kA`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kM`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kdr`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kna`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_h`
        - `np.array`
        - For unmyelinated model "Tigerholm". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_naleak`
        - `np.array`
        - For unmyelinated model "Tigerholm". Sodium leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kleak`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potassium leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.

    *   - `g_naf`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nas`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kd`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_ka`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kds`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kca`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_can`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_cat`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.

    *   - `I_naf`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nas`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kd`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_ka`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kds`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kca`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_can`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_cat`
        - `np.array`
        - For unmyelinated models "Schild_94"and "Schild_97". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.

    *   - `g_na`
        - `np.array`
        - For myelinated model "MRG". Sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nap`
        - `np.array`
        - For myelinated model "MRG". Persistent Sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_k`
        - `np.array`
        - For myelinated model "MRG". Potassium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_l`
        - `np.array`
        - For myelinated model "MRG". Leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_i`
        - `np.array`
        - For myelinated model "MRG". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_na`
        - `np.array`
        - For myelinated model "MRG". Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nap`
        - `np.array`
        - For myelinated model "MRG". Persistent Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_k`
        - `np.array`
        - For myelinated model "MRG". Potassium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_l`
        - `np.array`
        - For myelinated model "MRG". Leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_i`
        - `np.array`
        - For myelinated model "MRG". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.

    *   - `g_na`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_nap`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Persistent sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_k`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Potassium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kf`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Fast Potassium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_l`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_q`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_na`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nap`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Persistent sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_k`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Potassium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kf`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Fast Potassium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_l`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_q`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.


To save space in the :class:`~nrv.nmod.results.axon_results` object and discard unnecessary keys, some flags can be set in the :class:`~nrv.nmod.axon` object prior to the simulation:

.. code:: python3

    my_axon.record_V_mem = True         # save V_mem in the result object
    my_axon.record_I_mem = True         # save I_mem in the result object
    my_axon.record_g_mem = True         # save g_mem in the result object
    my_axon.record_g_ions = True        # save all g_xx in the result object
    my_axon.record_I_ions = True        # save all I_xx in the result object
    my_axon.record_particles = True     # save all particles in the result object

.. note::

   By default, only the ``record_V_mem`` flag is set to ``True``.


Several methods are implemented in the :class:`~nrv.nmod.results.axon_results` class. These include:

- :meth:`~nrv.nmod.results.axon_results.is_recruited`: returns ``True`` if an action potential is detected in the axon.
- :meth:`~nrv.nmod.results.axon_results.get_avg_AP_speed`: returns the conduction velocity of the action potential.
- :meth:`~nrv.nmod.results.axon_results.is_blocked`: detects if the axon conduction is blocked (for example, using KES stimulation).
- :meth:`~nrv.nmod.results.axon_results.rasterize`: rasterizes the ``V_mem`` data to facilitate analysis.

An example of using the different methods available in :class:`~nrv.nmod.results.axon_results` is available in the :doc:`examples <../examples/generic/18_Action_Potential_Analysis>` 


.. note::

   The :meth:`~nrv.nmod.results.axon_results.is_blocked` method requires *at least* an intracellular pulse to test axon conduction.



Fascicle results
----------------

The :class:`~nrv.nmod.results.fascicle_results` object aggregates parameters from the :class:`~nrv.nmod.fascicle` object and contains an :class:`~nrv.nmod.results.axon_results` for each simulated :class:`~nrv.nmod.axon` of fascicle. Each :class:`~nrv.nmod.results.axon_results` can be accessed using the following keys:

.. code:: python3

    my_axon_result = my_fascicle_result.axonx
    my_axon_result = my_fascicle_result['axonx']  # equivalent

where ``x`` ranges from 0 to the total number of axons-1 in the fascicle. You can retrieve all available axon keys using the :meth:`~nrv.nmod.results.fascicle_results.get_axons_key` method. Additional methods include:

- :meth:`~nrv.nmod.results.fascicle_results.get_recruited_axons`: returns the proportion (between 0 and 1) of recruited axons in the fascicle.
- :meth:`~nrv.nmod.results.fascicle_results.plot_recruited_fibers`: generates a plot of activated fibers within the fascicle.

Nerve results
-------------

The :class:`~nrv.nmod.results.nerve_results` object aggregates parameters from the :class:`~nrv.nmod.nerve` object and contains a :class:`~nrv.nmod.results.fascicle_results` for each simulated :class:`~nrv.nmod.nerve` within the nerve. Each :class:`~nrv.nmod.results.fascicle_results` can be accessed with the following keys:

.. code:: python3

    my_fascicle_result = my_nerve_result.fasciclex
    my_fascicle_result = my_nerve_result['fasciclex']  # equivalent

where ``x`` ranges from 0 to the total number of fascicles-1 in the nerve. You can retrieve all available fascicle keys using the :meth:`~nrv.nmod.results.nerve_results.get_fascicle_key` method. Other useful methods include:

- :meth:`~nrv.nmod.results.nerve_results.get_fascicle_results`: returns the :class:`~nrv.nmod.results.fascicle_results` for a specified fascicle ID.
- :meth:`~nrv.nmod.results.nerve_results.plot_recruited_fibers`: plots activated fibers within the nerve.

Post-processing functions
-------------------------

NRV allows the use of custom post-processing functions to filter and reduce data after the simulation of each individual :class:`~nrv.nmod.axon` in a :class:`~nrv.nmod.fascicle` or :class:`~nrv.nmod.nerve` object.  
These functions are called **after each axon simulation**, and operate on the resulting :meth:`~nrv.nmod.results.axon_results` object.

This mechanism is mainly used to remove unnecessary keys (e.g., membrane's voltage after action potential detection) in order to **reduce memory usage** during large-scale simulations.

.. note::
   Although we now use post-processing functions, the class member is still called ``postproc_script`` for backward compatibility with earlier versions of NRV.  

.. warning::
   In future releases, the terminology may evolve to clarify the difference between legacy "scripts" and callable Python functions.

Usage
-----

Post-processing functions can be set at the :class:`~nrv.nmod.fascicle` or :class:`~nrv.nmod.nerve` level using the ``postproc_script`` attribute.  
Optional arguments to the post-processing function can be passed using the ``postproc_kwargs`` attribute.

Built-in functions (formerly scripts)
-------------------------------------

NRV provides a few built-in post-processing scripts:

- :meth:`~nrv.ui.default_PP`: rasterizes ``V_mem`` and removes it if ``record_V_mem`` is disabled. This is the default behavior.
- :meth:`~nrv.ui.rmv_keys`: rasterizes ``V_mem`` and removes all keys except minimal axon metadata.
- :meth:`~nrv.ui.is_recruited`: rasterizes ``V_mem``, performs AP detection, and removes all irrelevant keys.
- :meth:`~nrv.ui.is_blocked`: rasterizes ``V_mem``, detects conduction block, and keeps only relevant keys.
- :meth:`~nrv.ui.sample_keys`: Undersample the desired keys and remove most of the :meth:`~nrv.nmod.results.axon_results`-object's other keys to alleviate RAM usage
- :meth:`~nrv.ui.sample_g_mem`: Undersample the membrane conductivity (``results["g_mem"]``)  and remove most of the `axon_results` other keys to alleviate RAM usage
- :meth:`~nrv.ui.vmem_plot`: Plot and save the membrane potential along each axon of the fascicle in a specified folder
- :meth:`~nrv.ui.raster_plot`: Plot and save the raster plot along each axon of the fascicle in a specified folder


.. note::
    Built-in post-processing scripts can be assigned either by directly passing the function or by specifying its name as a string.
    Both approaches are equivalent and compatible with the internal dispatcher:

    .. code:: python

        my_fasc.postproc_script = default_PP

    is equivalent to:

    .. code:: python

        my_fasc.postproc_script = "default_PP"

Custom post-processing functions
--------------------------------

You can define your own function with the following signature:

.. code:: python

   def my_custom_postproc(results: nrv.axon_results, **kwargs) -> nrv.axon_results:
       # modify results in-place or return modified copy
       return results

The function receives the :meth:`~nrv.nmod.results.axon_results` object and optional keyword arguments.

Examples
--------

**For a fascicle:**

.. code:: python

   import nrv
   import numpy as np

   def test_pp(results: nrv.axon_results, num=0):
       results["comment"] = "Custom PP accessed"
       results["num"] = num
       results.remove_key(keys_to_keep={"ID", "comment", "num"})
       return results

   fasc = nrv.fascicle()
   fasc.define_length(10000)
   fasc.axons_diameter = np.array([5.7])
   fasc.axons_type = np.array([1])
   fasc.axons_y = np.array([0])
   fasc.axons_z = np.array([0])
   fasc.postproc_script = test_pp
   fasc.postproc_kwargs = {"num": 1}

   results = fasc.simulate()

**For a nerve:**

.. code:: python

   import nrv
   import numpy as np

   def test_pp(results: nrv.axon_results, num=0):
       results["comment"] = "Custom PP accessed"
       results["num"] = num
       results.remove_key(keys_to_keep={"ID", "comment", "num"})
       return results

   fasc = nrv.fascicle()
   fasc.axons_diameter = np.array([5.7, 1.0])
   fasc.axons_type = np.array([1, 0])
   fasc.axons_y = np.array([0, 10])
   fasc.axons_z = np.array([0, 0])
   fasc.define_circular_contour(D=50)

   nerve = nrv.nerve(Length=10000)
   nerve.add_fascicle(fasc, ID=1)
   nerve.postproc_script = test_pp
   nerve.postproc_kwargs = {"num": 2}

   results = nerve.simulate()




