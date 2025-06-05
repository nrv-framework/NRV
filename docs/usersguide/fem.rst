FEM Simulations
===============

In NRV, FEM models are represented by the :class:`~nrv.fmod.FEM_stimulation` object. This class defines the nerve’s geometry, the number and shape of fascicles, and related parameters.

If the ``model_fname`` argument is set to ``None`` during instantiation, NRV will use **FEniCSx** to solve the FEM model.  
You can find the FEniCSx documentation here: `FEniCS Project <https://docs.fenicsproject.org/>`_.

If ``model_fname`` is provided and ``comsol=True``, NRV will instead use **COMSOL** with the corresponding template.  
More information about COMSOL can be found here: `COMSOL Multiphysics <https://www.comsol.fr/>`_.

.. warning::  
    Use FEM multiprocessing with caution. We currently recommend setting ``Ncore=None`` for now.

COMSOL Support
--------------

To use COMSOL-based FEM simulations, you must provide a parametric `.mph` file. NRV currently includes three COMSOL templates:

- ``Nerve_1_Fascicle_1_CUFF.mph`` — Monofascicular nerve with a monopolar CUFF electrode
- ``Nerve_1_Fascicle_1_LIFE.mph`` — Monofascicular nerve with a single LIFE electrode
- ``Nerve_1_Fascicle_2_LIFE.mph`` — Monofascicular nerve with two LIFE electrodes

.. warning::  
    COMSOL support is limited and may be deprecated in future versions.

Geometry Manipulation
---------------------

You can modify the nerve and fascicle geometries using:

- :meth:`~nrv.fmod.FEM_stimulation.reshape_nerve` — Set the nerve diameter and length
- :meth:`~nrv.fmod.FEM_stimulation.reshape_fascicle` — Define or update fascicles
- :meth:`~nrv.fmod.FEM_stimulation.reshape_outerBox` — Set the size of the surrounding simulation box

.. note::  
    To define multiple fascicles, call :meth:`~nrv.fmod.FEM_stimulation.reshape_nerve` with different ``ID`` values:

    .. code-block:: python3

        my_FEM.reshape_fascicle(d1, y1, z1, ID=0)  # Create fascicle ID 0
        my_FEM.reshape_fascicle(d2, y2, z2, ID=1)  # Create fascicle ID 1
        my_FEM.reshape_fascicle(d3, y1, z1, ID=0)  # Modify fascicle ID 0

Electrodes
----------

Any :class:`~nrv.fmod.electrode` object can be added to the FEM model using  
:meth:`~nrv.fmod.FEM_stimulation.add_electrode`. This method also links the electrode to a corresponding stimulus object.

.. warning::  
    If using a COMSOL template, the number of fascicles and electrode model must match the template. These elements cannot be fully customized afterward.

Usage with a Simulable Object
-----------------------------

A :class:`~nrv.fmod.FEM_stimulation` object can be attached to any  
:class:`~nrv.backend.NRV_simulable` object using  
:meth:`~nrv.backend.NRV_simulable.attach_extracellular_stimulation`.

.. note::  
    Although technically possible, we do **not** recommend attaching a FEM model to a :class:`~nrv.nmod.fascicle` object.  
    Instead, use a monofascicular :class:`~nrv.nmod.nerve` object.

Example with an Axon
--------------------

.. code-block:: python3

    my_FEM = nrv.FEM_stimulation()                                          # Create FEM model
    my_FEM.reshape_nerve(nerve_d, nerve_l)                                  # Set nerve geometry
    my_FEM.reshape_outerBox(outer_d)                                        # Set simulation box size
    my_FEM.reshape_fascicle(fascicle_d1, y1, z1, ID=0)                       # Add fascicle 0
    my_FEM.reshape_fascicle(fascicle_d2, y2, z2, ID=1)                       # Add fascicle 1
    my_FEM.add_electrode(my_electrode, my_stimulus)                         # Add electrode and stimulus
    my_axon.attach_extracellular_stimulation(my_FEM)                        # Attach FEM model to axon
    my_result = my_axon(t_sim)                                              # Run simulation

Example with a Nerve
--------------------

.. code-block:: python3

    my_FEM = nrv.FEM_stimulation()                                          # Create FEM model
    my_FEM.add_electrode(my_electrode, my_stimulus)                         # Add electrode and stimulus
    my_nerve.attach_extracellular_stimulation(my_FEM)                       # Attach FEM model to nerve
    my_result = my_nerve(t_sim)                                             # Run simulation

.. note::  
    When attaching a FEM model to a :class:`~nrv.nmod.nerve`, the nerve's geometry (e.g., diameter, number of fascicles) is automatically overwritten  
    to ensure consistency with the properties of the neural model.
