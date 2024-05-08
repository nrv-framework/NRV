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
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Key
        - Type
        - content
    *   - 001
        - 001
        - General architecture
    *   - `bla`
        - `np.array`
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
        - Final state of running `axon.simulate` method. If 'Successful', then the simulation terminated without any error or interruption. Else set to "Unsucessful".
    *   - `Error_from_prompt`
        - `str`
        - If the `simulation_state` is unsuccessful, this key contains the error message that has been returned (and that should also appear in the logfile).
    *   - `sim_time`
        - `float`
        - Final value of the demanded simulation time.
    *   - `Neuron_t_max`
        - `float`
        - Final timing achieved by the neuron solver once the simulation initiated. in miliseconds,
    *   - `t`
        - `np.array`
        - Array of timesteps in miliseconds
    *   - `x_rec`
        - `np.array`
        - Points in space along the x axis where simulation results are saved.
    *   - `V_mem`
        - `np.array`
        - Values of membrane voltage with time at the recorded x axis positions stored in the `x_rec` key
    *   - `I_mem`
        - `np.array`
        - Values of membrane voltage with time at the recorded x axis positions stored in the `x_rec` key
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
        - For unmyelinated model "Tigerholm". Potatium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kM`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potatium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kdr`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potatium ??? channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
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
        - For unmyelinated model "Tigerholm". Potatium leakage channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
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
        - For unmyelinated model "Tigerholm". Potatium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kM`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potatium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kdr`
        - `np.array`
        - For unmyelinated model "Tigerholm". Potatium ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.
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
        - For unmyelinated model "Tigerholm". Potatium leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.

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
        - For myelinated model "MRG". Persistant Sodium channels cconductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_k`
        - `np.array`
        - For myelinated model "MRG". Potatium channels cconductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_l`
        - `np.array`
        - For myelinated model "MRG". Leakage channels cconductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_i`
        - `np.array`
        - For myelinated model "MRG". ??? channels cconductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_na`
        - `np.array`
        - For myelinated model "MRG". Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_nap`
        - `np.array`
        - For myelinated model "MRG". Persistant Sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_k`
        - `np.array`
        - For myelinated model "MRG". Potatium channels current with time at the recorded x axis positions stored in the `x_rec` key.
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
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Persistant sodium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_k`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Potatium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `g_kf`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Fast potatium channels conductance with time at the recorded x axis positions stored in the `x_rec` key.
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
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Persistant sodium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_k`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Potatium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_kf`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Fast potatium channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_l`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". Leakage channels current with time at the recorded x axis positions stored in the `x_rec` key.
    *   - `I_q`
        - `np.array`
        - For myelinated model "Gaines_motor" and "Gaines_sensory". ??? channels current with time at the recorded x axis positions stored in the `x_rec` key.


Dictionary content reserved for post-processing
-----------------------------------------------

Some keys are also reserved for post-processing function to store results without over-writting raw results.

.. list-table:: Tests functionalities
    :widths: 10 10 150
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

