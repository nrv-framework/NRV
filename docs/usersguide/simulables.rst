=================
Simulable objects
=================

In NRV, all simulations can be launched by objects that have a physiological meaning:

1. **axons** or individual fibers. These fibers can be mylinated or unmyelinated and few models are already implemented.
2. **fascicles**: containing one or several axons. 
3. **nerves**: containing one or several fascicles.

All these object have in common a method called ``simulate`` that automatically performs the simulation, handle computation of extracellular fields if needed, process the stimuli, record internal variables. For fascicles and nerves, if the script is launched on several CPU cores, the parallelization is automatically handled transparently for the user.

Axons
=====

The ``axon`` class is abstract, meaning that the end user cannot directly instanciate an axon. Instead, two class exists and are accessible for the end-user for mylinated and unmylinated fibers.

However, for the end-user, some usefull methods are innherited by both unmylinated and mylinated fibers:
* bla1
* bla2

Unmyelinated axons
------------------

Unmyelinated axons implements automatically in Neuron the simple cable Hodgkin-Heuxley formalism. Axons are oriented along the x-axis as depicted bellow. The user can specify the y and z coordinates, directly in microns.

.. image:: ../images/unmyelinated.png

The main property of the axon is the diameter, that the user specifies in microns, and the length of the fiber, also specified in microns. Different models are pre-implemented in NRV:

.. list-table:: Available models for unmylinated axons
   :widths: 15 25 50
   :header-rows: 1

   * - Name
     - Instanciation string
     - Comment
   * - Hodgkin-Huxley
     - ``"HH"``
     - model from Hodgkin and Huxley 1952
   * - Rattay-Aberham
     - ``"Rattay_Aberham"``
     - Comment
   * - Sundt
     - ``"Sundt"``
     - Comment
   * - Tigerholm
     - ``"Tigerholm"``
     - Comment
   * - Schild 1994
     - ``"Schild_94"``
     - Comment
   * - Schild 1997
     - ``"Schild_97"``
     - Comment

A scientific review of these models is available in the the following paper:
Pelot, N. A., Catherall, D. C., Thio, B. J., Titus, N. D., Liang, E. D., Henriquez, C. S., & Grill, W. M. (2021). Excitation properties of computational models of unmyelinated peripheral axons. Journal of neurophysiology, 125(1), 86-104.

The complete list of tunable parameters for unmyelinated axons is:

.. list-table:: Public attributes of unmyelinated axons
   :widths: 10 10 10 50
   :header-rows: 1

   * - Property
     - type
     - default
     - Comment

   * - y 
     - float
     - 0
     - y coordinate for the axon, in um
   * - z
     - float
     - 0
     - z coordinate for the axon, in um
   * - d
     - float
     - 1
     - axon diameter, in um
   * - L
     - float
     - 1000
     - axon length along the x axins, in um
   * - model
     - str
     - "Rattay_Aberham"
     - choice of conductance based model (table above)
   * - dt
     - float
     - 0.001
     - computation step for simulations, in ms. By default equal to 1 us
   * - Nrec
     - int
     - 0
     - Number of points along the axon to record for simulation results. Between 0 and the number of segment, if set to 0, all segments are recorded
   * - Nsec
     - int
     - 1
     - Number of sections in the axon, by default 1. Usefull to create umnyelinated axons with a variable segment density
   * - Nseg_per_sec
     - int
     - 0
     - Number of segment per section in the axon. If set to 0, the number of segment is automatically computed using d-lambda rule and following paramters. If set by user, please use odd numbers
   * - freq
     - float
     - 100
     - Frequency used for the d-lmbda rule, corresponding to the maximum membrane current frequency, by default set to 100 Hz
   * - freq_min
     - float
     - 0
     - Minimal frequency fot the d-lambda rule when using an irregular number of segment along the axon, if set to 0, all sections have the same frequency determined by the previous parameter
   * - mesh_shape
     - str
     - "plateau_sigmoid"
     - Shape of the frequencial distribution for the dlmabda rule along the axon, pick between:
   * - alpha_max
     - float
     - 0.3
     - Proportion of the axon set to the maximum frequency for plateau shapes, by default set to 0.3
   * - d_lambda
     - float
     - 0.1
     - value of d-lambda for the dlambda rule,
   * - v_init
     - float
     - None
     - Initial value of the membrane voltage in mV, set None to get an automatically model attributed value
   * - T
     - float
     - None
     - temperature in C, set None to get an automatically model attributed value
   * - ID
     - int
     - 0
     - axon ID, by default set to 0,
   * - threshold
     - float
     - -40
     - voltage threshold in mV for further spike detection in post-processing, by defautl set to -40mV, see post-processing files for further help

For the end-user, two specific methods for intracellular stimulation of unmylinated axons are available:

* ``insert_I_Clamp`` to perform current clamp stimulation. For the moment this restric to a single pulse waveform

    .. list-table:: Arguments of current clamp method
       :widths: 15 25 50
       :header-rows: 1

       * - Parameter
         - Type
         - Comment
       * - position
         - float
         - relative position over the axon
       * - t_start
         - float
         - starting time, in ms
       * - duration
         - float
         - duration of the pulse, in ms
       * - amplitude
         - float
         - amplitude of the pulse (nA)


* ``insert_V_Clamp`` to perform voltage clamp stimulation.

    .. list-table:: Arguments of voltage clamp method
       :widths: 15 25 50
       :header-rows: 1

       * - Parameter
         - Type
         - Comment
       * - position
         - float
         - relative position over the axon
       * - stimulus
         - ``Stimulus object``
         - stimulus for the clamp, see corresponding page for more information


Myelinated axons
----------------

blablablabla

Fascicles
=========

blablablabla

Nerves
======

blablablabla
