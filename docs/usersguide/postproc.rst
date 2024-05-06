===============
Post-processing
===============

Post-processing function, both at the cellular or fascicle (nerve) levels have been implemented in NRV. The code is mainly consisting in function, opposed to method. This is due to the nature of results, returned by the ``simulate`` method that consist in a python dictionary and not  a specific object.

This chapter contains:

* a more in depth explanation of the results' dictionary returned by simulate methods
* explanation of axon/cellular level post-processing functions
* explanation of fascicle (nerve) level post-processing functions

Result dictionary
=================
When the an axon is simulated (by calling the ``axon.simulate`` method), a dictionnary is returned, containing all meta-data from the simulation.
The meta data include:

* all properties of the axon,

* all computed results.

The user can also perform some post-processing steps that add results to this dictionary.
Here below we detail the content of the dictionary. 

Dictionary content for configration saving
------------------------------------------

A first set of keys corresponds to data of configuration of the axon:

.. list-table:: Tests functionalities
    :widths: 10 10 50
    :header-rows: 1
    :align: center

    *   - Key
        - Type
        - content
    *   - 001
        - 001
        - General architecture
    *   - Simulation_state
        - bla
        - bla


Dictionary content for computation results
------------------------------------------

here is the list of computation results:

.. list-table:: Tests functionalities
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Key
        - Type
        - content
    *   - `Simulation_state`
        - `str`
        - Final state of running `axon.simulate` method. If 'Successful', then the simulation terminated without any error or interruption. Else set to "Unsucessful", without further detail. Refer to log file for debug.
    *   - `sim_time`
        - `float`
        - Final value of the demanded simulation time.
    *   - `t`
        - `np.array`
        - Array of timesteps in miliseconds
    *   - `x_rec`
        - `np.array`
        - Points in space along the x axis where simulation results are saved.
    *   - `V_mem`
        - `np.array`
        - Values of membrane voltage at the recorded x axis positions stored in the `x_rec` key
    *   - `I_mem`
        - `bla`
        - bla
    *   - `g_mem`
        - `bla`
        - bla
    *   - `g_na`
        - `bla`
        - bla
    *   - `g_k`
        - `bla`
        - bla
    *   - `g_l`
        - `bla`
        - bla
    *   - `Simulation_state`
        - `bla`
        - bla
    *   - `Simulation_state`
        - `bla`
        - bla
    *   - `Simulation_state`
        - `bla`
        - bla

Dictionary content reserved for post-processing
-----------------------------------------------

Some keys are also reserved for post-processing function to store results without over-writting raw results.

.. list-table:: Tests functionalities
    :widths: 10 10 50
    :header-rows: 1
    :align: center

    *   - Key
        - Type
        - content
    *   - 001
        - 001
        - General architecture

Keys outside from those three tables are not used and can be freely reached by the user to store additional results associated with simulations.

Cellular level post-processing
==============================

blablablablablablabla

Fascicle (nerve) level post-processing
======================================

blablablablalbalbalbabla

