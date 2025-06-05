=================
Simulable objects
=================

In NRV, all simulations can be launched by objects that have a physiological meaning:

1. **axons** or individual fibers. These fibers can be myelinated or unmyelinated and few models are already implemented.
2. **fascicles**: containing one or several axons. 
3. **nerves**: containing one or several fascicles.

All these object have in common a method called :meth:`~nrv.nmod.axon.simulate` that automatically performs the simulation, handles computation of extracellular fields if needed, processes the stimuli, records internal variables. For fascicles and nerves, if the script is launched on several CPU cores, the parallelization is automatically handled transparently for the user.


.. note::
  Simulable objects are callable. Calling any simulable object will call the :meth:`~nrv.nmod.axon.simulate` -method. In other words:

  .. code:: python3

      my_simulable.simulate(*myargs)
        
  is equivalent to:

  .. code:: python3

      my_simulable(*myargs)


Axons
=====

The :class:`~nrv.nmod._axons.axon` is abstract, meaning that the end user cannot directly instantiate an axon. Instead, two daughter classes are accessible for the end-user for :class:`~nrv.nmod._myelinated.myelinated` and :class:`~nrv.nmod._unmyelinated.unmyelinated` fibers.

Generic parameters for all axons are defined by default and can be changed, as both unmyelinated and myelinated axons inherit from them.

Some useful methods are inherited by both unmyelinated and myelinated fibers:

* The :meth:`~nrv.nmod.axon.simulate` method that solves the neural model.

  .. list-table:: Arguments of simulate method
      :widths: 15 25 50
      :header-rows: 1

      * - Parameter
        - Type
        - Comment
      * - t_sim
        - float
        - total simulation time (ms), by default 20 ms

  The simulate method is also controlled by axon attributes as described in the next table:

  .. list-table:: Attributes of axon involved in simulate
      :widths: 15 15 15 50
      :header-rows: 1

      * - Attribute
        - Type
        - default
        - Comment
      * - record_V_mem
        - bool
        - ``True``
        - if true, the membrane voltage is recorded
      * - record_I_mem
        - bool
        - ``False``
        - f true, the membrane current is recorded
      * - record_I_mem
        - bool
        - ``False``
        - if true, the ionic currents are recorded
      * - record_particules
        - bool
        - ``False``
        - if true, the particle states are recorded
      * - loaded_footprints
        - dictionary
        - None
        - Dictionary composed of extracellular footprint array, the keys are int value of the corresponding electrode ID, if None, footprints calculated during the simulation,

  The simulate method for axons generate results are stored and returned in a :class:`~nrv.nmod.results._axons_results.axon_results` object.

* A method to link an axon to an **extracellular stimulation**. This object provides the description of the extracellular context. It is required for computing the external fields and footprint used to evaluate the axon response. A chapter of this user's guide s dedicated to :doc:`extracellular stimulation <fem>`. This method, called :meth:`~nrv.nmod.axon.attach_extracellular_stimulation` has a single parameter, the :meth:`~nrv.fmod.extracellular_context.attach_extracellular_stimulation` object instance.

* A method to change the stimulation waveform from a specific electrode already linked to the axon with the :meth:`~nrv.nmod.axon.attach_extracellular_stimulation` method. This method is called :meth:`~nrv.nmod.axon.change_stimulus_from_electrode` and has for arguments:
    .. list-table:: Arguments of the :meth:`~nrv.nmod._axons.axon.change_stimulus_from_electrode` method
       :widths: 15 25 50
       :header-rows: 1

       * - Parameter
         - Type
         - Comment
       * - ID_elec
         - int
         - ID of the electrode which should be changed
       * - stimulus
         - :class:`~nrv.utils._stimulus.stimulus`
         - New stimulus to set


Unmyelinated axons
------------------

Unmyelinated axons object implements automatically Hodgkin-Huxley-like cable formalism in NEURON. Axons are oriented along the x-axis as depicted bellow. The user can specify the y and z coordinates, directly in microns.

.. image:: ../images/unmyelinated.png

The main property of the axon is the diameter, that the user specifies in microns, and the length of the fiber, also specified in microns. Different models are pre-implemented in NRV:

.. list-table:: Available models for unmyelinated axons
   :widths: 15 25 50
   :header-rows: 1

   * - Name
     - Instantiation string
     - Comment
   * - Hodgkin-Huxley
     - ``"HH"``
     - Model from Hodgkin and Huxley 1952
   * - Rattay-Aberham
     - ``"Rattay_Aberham"``
     - Model from Rattay and Aberham 1993
   * - Sundt
     - ``"Sundt"``
     - Comment
   * - Tigerholm
     - ``"Tigerholm"``
     - Model from Tigerholm et al. 2014
   * - Schild 1994
     - ``"Schild_94"``
     - Model from Schild et al. 1994
   * - Schild 1997
     - ``"Schild_97"``
     - Model from Schild et al. 1997

A scientific review of these models is available in the following paper:
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
     - y coordinate for the axon, in µm
   * - z
     - float
     - 0
     - z coordinate for the axon, in µm
   * - d
     - float
     - 1
     - axon diameter, in um
   * - L
     - float
     - 1000
     - axon length along the x axons, in µm
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
     - Number of sections in the axon, by default 1. Useful to create umnyelinated axons with a variable segment density
   * - Nseg_per_sec
     - int
     - 0
     - Number of segment per section in the axon. If set to 0, the number of segment is automatically computed using d-lambda rule and following parameters. If set by user, please use odd numbers
   * - freq
     - float
     - 100
     - Frequency used for the d-lambda rule, corresponding to the maximum membrane current frequency, by default set to 100 Hz
   * - freq_min
     - float
     - 0
     - Minimal frequency for the d-lambda rule when using irregular number of segments along the axon, if set to 0, all sections have the same frequency determined by the previous parameter
   * - mesh_shape
     - str
     - "plateau_sigmoid"
     - Shape of the frequencies' distribution for the d-lmabda rule along the axon, pick between:
   * - alpha_max
     - float
     - 0.3
     - Proportion of the axon set to the maximum frequency for plateau shapes, by default set to 0.3
   * - d_lambda
     - float
     - 0.1
     - value of d-lambda for the d-lambda rule,
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
     - voltage threshold in mV for further spike detection in post-processing, by default set to -40mV, see the :doc:`post-processing section <postproc>` for further help

For the end-user, two specific methods for intracellular stimulation of unmyelinated axons are available:

* :meth:`~nrv.nmod.unmyelinated.insert_I_Clamp` to perform current clamp stimulation. For the moment only single pulse waveform are available.

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
         - amplitude of the pulse, in nA


* :meth:`~nrv.nmod.unmyelinated.insert_V_Clamp` to perform voltage clamp stimulation.

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
         - :class:`~nrv.utils._stimulus.stimulus`
         - stimulus for the clamp, see corresponding page for more information


Myelinated axons
----------------

Similarly, myelinated axons implements the double cable fiber description in NEURON. Axons are oriented along the x-axis as depicted bellow. The user can specify the y and z coordinates, directly in microns.

.. image:: ../images/myelinated.png

The main property of the axon is the diameter, that the user specifies in microns, and the length of the fiber, also specified in microns. The succession of myelinated regions and Nodes-of-Ranvier is automatically computed, and the axon can be shifted along its axes so that for similar diameter fibers, nodes-of-Ranvier are not aligned. Different models are pre-implemented in NRV:

.. list-table:: Available models for myelinated axons
   :widths: 15 25 50
   :header-rows: 1

   * - Name
     - Instantiation string
     - Comment
   * - MacIntyre-Grill-Richardson
     - ``"MRG"``
     - First model of double cable axon described in [1], ionic channels on NoR and passive myelin
   * - Gaines motor fibers
     - ``"Gaines_motor"``
     - Double cable described in [2], ionic channels on NoR and adjacent myelinated regions for **motor** fibers
   * - Gaines sensory fibers
     - ``"Gaines_sensory"``
     - Double cable described in [2], ionic channels on NoR and adjacent myelinated regions for **sensory** fibers

Details of model can be found in the following scientific contributions:

[1] McIntyre CC, Richardson AG, and Grill WM. Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle. Journal of Neurophysiology 87:995-1006, 2002.

[2] Gaines, J. L., Finn, K. E., Slopsema, J. P., Heyboer, L. A.,  Polasek, K. H. (2018). A model of motor and sensory axon activation in the median nerve using surface electrical stimulation. Journal of computational neuroscience, 45(1), 29-43.

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
     - axon length along the x axis, in um
   * - model
     - str
     - "MRG"
     - choice of conductance based model (table above)
   * - dt
     - float
     - 0.001
     - computation step for simulations, in ms. By default equal to 1 µs
   * - node_shift
     - float
     - 0
     - shift of the first node of Ranvier to zeros, as a fraction of internode length (0<= node_shift < 1)
   * - Nseg_per_sec
     - int
     - 0
     - Number of segment per section in the axon. If set to 0, the number of segment is automatically computed using d-lambda rule and following parameters. If set by user, please use odd numbers
   * - freq
     - float
     - 100
     - Frequency used for the d-lambda rule, corresponding to the maximum membrane current frequency, by default set to 100 Hz
   * - freq_min
     - float
     - 0
     - Minimal frequency for the d-lambda rule when using irregular number of segment along the axon, if set to 0, all sections have the same frequency determined by the previous parameter
   * - mesh_shape
     - str
     - "plateau_sigmoid"
     - Shape of the frequencies distribution for the d-lmabda rule along the axon, pick between:
   * - alpha_max
     - float
     - 0.3
     - Proportion of the axon set to the maximum frequency for plateau shapes, by default set to 0.3
   * - d_lambda
     - float
     - 0.1
     - value of d-lambda for the d-lambda rule,
   * - rec
     - str
     - ``"nodes"``
     - recording zones for the membrane potential, eiter:
        "nodes": record only at the nodes of Ranvier
        "all": all computation points in nodes of Ranvier and over myelin
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
     - voltage threshold in mV for further spike detection in post-processing, by default set to -40mV, the :doc:`post-processing section <postproc>` for further help

Again, for the end-user, four specific methods for intracellular stimulation myelinated axons are available:


* :meth:`~nrv.nmod.myelinated.insert_I_Clamp_node`, for which the current clamp is directly applied at a node-of-Ranvier, given its number
  
  .. list-table:: Arguments of current clamp at a node method
      :widths: 15 25 50
      :header-rows: 1

      * - Parameter
        - Type
        - Comment
      * - index
        - int
        - node number of the node to stimulate
      * - t_start
        - float
        - starting time, in ms
      * - duration
        - float
        - duration of the pulse, in ms
      * - amplitude
        - float
        - amplitude of the pulse in nA

* :meth:`~nrv.nmod.myelinated.insert_I_Clamp`, for which the current clamp is applied in the fiber with a normalized position

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
        - amplitude of the pulse, in nA

* :meth:`~nrv.nmod.myelinated.insert_V_Clamp_node`, for which the voltage clamp is directly applied at a node-of-Ranvier, given its number

  .. list-table:: Arguments of voltage clamp method
      :widths: 15 25 50
      :header-rows: 1

      * - Parameter
        - Type
        - Comment
      * - index
        - int
        - node number of the node to stimulate
      * - stimulus
        - :class:`~nrv.utils._stimulus.stimulus`
        - stimulus for the clamp, see corresponding page for more information

* :meth:`~nrv.nmod.myelinated.insert_V_Clamp`, for which the voltage clamp is applied in the fiber with a normalized position

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
        - :class:`~nrv.utils._stimulus.stimulus`
        - stimulus for the clamp, see corresponding page for more information


Fascicles
=========

In NRV, fascicles consist in an aggregation of axon objects, on which we can perform logical/arithmetical operations, specify properties, and simulate. Fascicle constructor takes two initialization parameters:

.. list-table:: Fascicle initialization parameters list
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - d 
    - float
    - None
    - fascicle diameter, in um
  * - ID
    - int
    - 0
    - fascicle unique identifier 

Once created, the fascicle can be filled with a population of axon. The axon population can be either generated with NRV (see :doc:`Generate axons populations <populations>`), or by any external means. Axons are added to the fascicle with the :meth:`~nrv.nmod.fascicle.fill_with_population` method.

.. list-table:: fill_with_population parameters
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - axons_diameter 
    - np.array[float]
    - 
    - Array of axon diameter, in um
  
  * - axons_type
    - np.array[bool]
    - 
    - Array of axon type. True means myelinated, False means unmyelinated

  * - delta
    - float
    - 1um
    - axon-to-axon and axon to fascicle border minimal distance

  * - y_axons
    - np.array[float]
    - None
    - Optional, y-position of each axon

  * - z_axons
    - np.array[float]
    - None
    - Optional, z-position of each axon

  * - fit_to_size
    - bool
    - False
    - If true, axons position will be dilated to fit the entire fascicle area

  * - n_iter
    - int
    - 20 000
    - Optional, number of iteration of the packing algorithm 

.. note::
  If the ``y_axons`` and ``z_axons`` parameters are not specified, the :meth:`~nrv.nmod.fascicle.fill_with_population`-method will automatically called the NRV's packing algorithm to place them.


Axon simulation parameters can be specified in a dictionary and pass to the fascicle object with the :meth:`~nrv.nmod.fascicle.set_axons_parameters` method:


.. list-table:: set_axons_parameters parameters
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - unmyelinated_only 
    - bool
    - False
    - Parameters are for unmyelinated axons only

  * - myelinated_only 
    - bool
    - False
    - Parameters are for myelinated axons only

  * - kwargs 
    - kwargs
    - 
    - kwargs for axon parameters


To stimulate the fascicle, one option is to use the :meth:`~nrv.nmod.fascicle.insert_I_Clamp` method. 

.. list-table:: insert_I_Clamp parameters
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - position 
    - float
    - 
    - Clamp position along the axon's x-axis

  * - t_start 
    - float
    - 
    - Pulse start time, in ms

  * - duration 
    - float
    - 
    - Pulse duration, in ms

  * - amplitude 
    - float
    - 
    - Pulse amplitude, in nA

  * - ax_list 
    - np.array[int]
    - None
    - Array to filter axon for I clamp. If None, I clamp is applied to all axons.


Extracellular context is attached to a fascicle with the :meth:`~nrv.nmod.fascicle.attach_extracellular_stimulation` method, as for the axon (see above). Stimulus can also be changed with the :meth:`~nrv.nmod.fascicle.change_stimulus_from_electrode` method. NRV also provides several other methods to manipulate fascicle objects, such as :meth:`~nrv.nmod.fascicle.remove_myelinated_axons`, :meth:`~nrv.nmod.fascicle.remove_axons_size_threshold`, :meth:`~nrv.nmod.fascicle.rotate_fascicle`, :meth:`~nrv.nmod.fascicle.translate_fascicle`, :meth:`~nrv.nmod.fascicle.plot`, etc. 
Before running simulation, some flags can be set: :attr:`~nrv.nmod.fascicle.save_results`, :attr:`~nrv.nmod.fascicle.return_parameters_only`, :attr:`~nrv.nmod.fascicle.save_path`:

- If :attr:`~nrv.nmod.fascicle.save_results` is `True`, then fascicle simulation results are saved on the hard-drive. 
- :attr:`~nrv.nmod.fascicle.save_path` specifies where to save the results
- :attr:`~nrv.nmod.fascicle.return_parameters_only` removes results from the returned :class:`~nrv.nmod.fascicle` object.

Setting correctly those flags are particularly useful for large simulations. It relaxes RAM memory usage and facilities heavy post-processing. Additionally, post-processing scripts can be run during fascicle simulation. Post-processing scripts are set in the fascicle :meth:`~nrv.nmod.fascicle.simulate` method with the ``postproc_script`` parameter. 
Available post-processing scripts and how to make a custom one is described in the :doc:`post-processing section <postproc>`. 

.. warning::
  We do not recommend attaching extracellular context and running simulation of fascicle directly. Instead, we recommend using nerve object (see below), even for monofascicular nerve.

Nerves
======

A :class:`~nrv.nmod.nerve` object in NRV serves two purposes:

- Gathering one or multiple :class:`~nrv.nmod.fascicle` objects
- Ensuring consistency between the FEM model and the neural model

The :class:`~nrv.nmod.nerve` object is initialized with the following list of parameters:

.. list-table:: nerve object initialization parameters list
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - length 
    - float
    - 10_000
    - nerve length, in µm

  * - diameter 
    - float
    - 100
    - nerve diameter, in µm

  * - Outer_D 
    - float
    - 5
    - outer saline box diameter, in mm

  * - ID
    - int
    - 0
    - nerve unique identifier


:class:`~nrv.nmod.fascicle` objects are incorporated to the nerve with the :meth:`~nrv.nmod.nerve.add_fascicle` method:


.. list-table:: add_fascicle parameters list
  :widths: 10 10 10 50
  :header-rows: 1

  * - Property
    - type
    - default
    - Comment

  * - fascicle
    - :class:`~nrv.nmod.fascicle`
    - 
    - fascicle object to add to the nerve

  * - ID 
    - int
    - None
    - optional, forces new fascicle unique identifier

  * - y 
    - float
    - None
    - optional, forces fascicle new y coordinate

  * - z 
    - float
    - None
    - optional, forces fascicle new z coordinate

.. warning::
  Aggregation of :class:`~nrv.nmod.fascicle` objects in the :class:`~nrv.nmod.nerve` object uses the Python's deep-copy mechanism. Any modification of one
  of the fascicle after adding them to the :class:`~nrv.nmod.nerve` will also affect the copy added in the latter.

The :class:`~nrv.nmod.nerve` class includes most of the method available in the :class:`~nrv.nmod.fascicle` class: :meth:`~nrv.nmod.nerve.set_axons_parameters`, :meth:`~nrv.nmod.nerve.plot`, :meth:`~nrv.nmod.nerve.insert_I_Clamp`, :meth:`~nrv.nmod.nerve.attach_extracellular_stimulation`, etc.
The :meth:`~nrv.nmod.nerve.simulate` method runs the simulation and returns a :meth:`~nrv.nmod.results.nerve_results` object (see the :doc:`post-processing section <postproc>`). 