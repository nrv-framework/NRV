===============
Post-processing
===============

NRV provides object and method to facilitate simulation post-processing and analysis. This chapter describes how to use those features.

NRV Result objects
==================

When called, NRV ``simulable`` objects return object inhering from the ``NRV_results`` class. Specifically:

- ``axon`` simulations return ``axon_results`` objects
- ``fascicle`` simulations return ``fascicle_results`` objects
- ``nerve`` simulations return ``nerve_results`` objects

.. note::
  NRV_results behave like a python object and a like dictionary. In other words:

  .. code:: ipython3

      val = my_result.my_key
        
  is equivalent to:

  .. code:: ipython3

      val = my_result['my_key']

Those objects contain every parameter of the simulation, e.g axon diameter in a ``axon_results``, axon population description in a ``fascicle_results``,
fascicles description in ``nerve_results``, etc. Each object inhering from ``NRV_results`` also includes a copy of the extracellular and intracellular context.
Those objects are described hereafter.

axon_results
------------

The following table describes all the keys/member available in a ``axon_results`` object:

.. list-table:: axon_results key/member
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Key/Member
        - Type
        - content
    *   - `Simulation_state`
        - `str`
        - Final state of running ``axon.simulate`` method. If 'Successful', then the simulation terminated without any error or interruption. Else set to "Unsuccessful".
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


To save some space in the ``axon_results`` object and discarded unnecessary keys, some flags can be set in the ``axon`` object, prior to the simulation: 

.. code:: ipython3

    my_axon.record_V_mem = True         #save V_men in the result object
    my_axon.record_I_mem = True         #save I_men in the result object
    my_axon.record_g_mem = True         #save g_men in the result object
    my_axon.record_g_ions = True        #save all g_xx in the result object
    my_axon.record_I_ions = True        #save all I_xx in the result object
    my_axon.record_particles = True     #save all particles in the result object 
    
.. Note::

    By default, only the ``record_V_mem`` flag is set to ``True``.

Several methods are implemented in the ``axon_result`` class. It includes the ``is_recruited`` method which returns ``True`` if an action-potential
is detected in the axon, the ``speed`` method that returns the velocity of the AP, the ``block`` method that detects if an axon has its conduction 
block or not (using KES for example), the ``rasterize`` method that rasterizes ``V_mem`` to facilitate data analysis, etc. 

.. Note::
    The ``block`` method required an intracellular pulse to test the conduction of the axon.


fascicle_results
----------------

``fascicle_results`` object aggregate ``fascicle`` object parameters and every ``axon_result`` correspond to each ``axon`` object simulated 
in the fascicle. Each ``axon_result`` is available with the following key: 

.. code:: ipython3

    my_axon_result = my_fascicle_result.axonx
    my_axon_result = my_fascicle_result['axonx']    #equivalent

where ``x`` ranges from 0 to the number of axon-1 in the fascicle. All available axon keys can be obtained with the ``get_axons_key`` method. Other available methods include 
the ``get_recruited_axons`` method which returns the proportion (between 0 and 1) of axon recruited in the fascicle. The ``plot_recruited_fibers`` method facilitates plot of activated fiber in the fascicle. 

nerve_results
-------------

``nerve_results`` object aggregate ``nerve`` object parameters and every ``fascicle_result`` correspond to each ``fascicle`` object simulated 
in the nerve. Each ``fascicle_result`` is available with the following key: 

.. code:: ipython3

    my_fascicle_result = my_nerve_result.fasciclex
    my_fascicle_result = my_nerve_result['fasciclex']    #equivalent

where ``x`` ranges from 0 to the number of fascicle-1 in the nerve. All available fascicle keys can be obtained with the ``get_fascicle_key`` method. Other available methods include 
the ``get_fascicle_results`` method which returns a ``fascicle_result`` of a specified fascicle ID, or the ``plot_recruited_fibers`` method that plots activated fiber in the nerve. 

Post-processing script
=======================

NRV provides a way to run external post-processing script during ``nerve`` or ``fascicle`` simulation. Those scripts are meant to apply filtering/post-processing functions
to each simulate ``axon_result`` object during the simulation. It is mainly used to remove unnecessary keys (after AP detection for example) to alleviate RAM usage during large simulation. 
Post-processing scripts are selected by setting the ``postproc_script`` class member of ``fascicle`` or ``nerve`` objects:

.. code:: ipython3

    my_fascicle.postproc_script = "my_postproc_script"      #for fascicle
    my_nerve.postproc_script = "my_postproc_script"         #for nerve


Those scripts can be custom, but NRV provides some pre-written scripts: 

- ``default`` : rasterizes ``V_mem`` and remove the ``V_mem`` if the ``record_V_mem`` flag is set. It is the script called by default.  
- ``ap_detection`` : rasterizes ``V_mem`` and remove all the keys except the rasterized result and axons parameters (type, diameter, position, etc)
- ``is_blocked`` : rasterizes and detects block state, and remove all the keys except the rasterized result and axons parameters (type, diameter, position, etc)

.. warning::
  Post-processing scripts are called "on-the-fly", i.e. any modification of the script during the simulation runtime will impact the post-processing.

.. warning::
  Post-processing scripts will be replaced by callable object in future release of the API.

