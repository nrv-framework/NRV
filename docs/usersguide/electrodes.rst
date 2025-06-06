==========
Electrodes
==========

Electrodes in NRV are associated with field computation and are, by definition, extracellular.  
The implementation is designed to abstract away numerical and computational details, allowing the user to focus on modeling.  
However, advanced users can implement and integrate custom electrode types if needed.

Overview of Existing Electrodes, Classes, and Custom Electrode Capabilities
---------------------------------------------------------------------------

Several classes are available in NRV to handle electrode behavior.  
Currently, NRV supports three main electrode families for simulation:

- **Point Source electrodes**
- **LIFE electrodes**
- **CUFF electrodes** (which may contain one or more electrical contacts)

These electrodes are implemented specifically for simulation use.

A class diagram showing the structure and relationships of electrode classes is provided below:

.. image:: ../images/electrodes_classdiagram.png

Abstract Base Classes
~~~~~~~~~~~~~~~~~~~~~

Two classes are abstract and not intended for direct use by end users:

* :class:`~nrv.fmod.electrode`: this class serves as the interface between electrodes and simulable objects to automate the simulation process.  
  Even advanced users should not interact with this class directly.

* :class:`~nrv.fmod.FEM_electrode`: this class is responsible for automated FEM simulation setup and execution.  
  Custom electrodes must inherit from this base class.  
  Implementing new electrodes at this level requires knowledge of NRV's FEM architecture and simulation internals.  
  For such advanced usage, refer to the :ref:`API documentation <modules>`.

Accessible Electrode Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Four classes are directly accessible to end users:

* :class:`~nrv.fmod.point_source_electrode`
* :class:`~nrv.fmod.LIFE_electrode`
* :class:`~nrv.fmod.CUFF_electrode` – for single-contact CUFF electrodes
* :class:`~nrv.fmod.CUFF_MP_electrode` – for multipolar CUFF electrodes

Each class provides specific features and customization options described in detail below.

Common Methods Across All Electrodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All electrode classes share a set of common methods:

Common Methods Across All Electrodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All electrode classes share a set of common methods:

* **ID management**:
  
  - :meth:`~nrv.fmod.electrode.get_ID_number` – Retrieves the electrode's ID.
  - :meth:`~nrv.fmod.electrode.set_ID_number` – Assigns a new ID to the electrode.

* **Footprint access** (see *Scientific Foundation* section for more details):
  
  - :meth:`~nrv.fmod.electrode.get_footprint` – Retrieves the current footprint of the electrode.
  - :meth:`~nrv.fmod.electrode.set_footprint` – Sets a custom footprint (advanced users only).

* **Footprint clearing**:
  
  - :meth:`~nrv.fmod.electrode.clear_footprint` – Forces recalculation by clearing the existing footprint.

* **Geometrical translation**:
  
  - :meth:`~nrv.fmod.electrode.translate` – Translates the electrode in 3D space (in µm).


Point Source Electrodes
-----------------------

These electrodes are non-geometrical monopolar punctual sources of current. 
**There is no model for a current return electrode**, and this electrode is only a theoretical model based on Point Source Approximation.
The usage is simple, and the advantage is that the computational cost is very low as no finite element computation step is required. 
Only one material can constitute the extracellular medium.
However, such electrodes should be limited to simple investigations or very first approximation simulations. 
The geometry of the electrodes is schematized in the figure bellow:

.. image:: ../images/electrodes_PSA.png

Point Source Electrode can be declared with the following parameters:

* x (float) x-position of the electrode, in µm

* y (float) y-position of the electrode, in µm

* z (float) z-position of the electrode, in µm

* ID (int) electrode identification number, set to 0 by default. 

LIFE Electrodes
---------------

LIFE stands for **Longitudinal Intra-Fascicular Electrodes**.  
These electrodes are typically inserted into a nerve fascicle using a **thin wire**, which is *not currently modeled* in the simulation. The electrode is assumed to be **aligned longitudinally with the nerve fibers**.

When a LIFE electrode is placed inside a fascicle—or more generally within a nerve—NRV automatically performs a check to **exclude overlapping fibers** from the simulation to ensure anatomical realism.

The geometry and configuration of a LIFE electrode is illustrated below:

.. image:: ../images/electrodes_LIFE.png

A LIFE electrode can be instantiated using the following parameters:

* ``label`` (*str*, optional) – name of the electrode (e.g., from the COMSOL geometry)
* ``D`` (*float*) – diameter of the electrode, in µm
* ``length`` (*float*) – length of the electrode, in µm
* ``x_shift`` (*float*) – longitudinal offset from the origin of the simulation domain, in µm
* ``y_c`` (*float*) – y-coordinate of the electrode center, in µm
* ``z_c`` (*float*) – z-coordinate of the electrode center, in µm
* ``ID`` (*int*, optional) – unique identifier of the electrode (default: ``0``)


CUFF Electrodes
---------------

CUFF electrodes are **ring-shaped electrodes** implanted **externally around the nerve**, in direct contact with the **epineurium**.  
They are often used for non-penetrating stimulation or recording. A schematic representation is shown below:

.. image:: ../images/electrodes_CUFF.png

There are two types of CUFF electrodes handled in NRV:

**Mono-contact CUFF electrodes**  
This type includes a single contact encircling the nerve.  
The :class:`~nrv.fmod.CUFF_electrode` class can be instantiated using the following parameters:

* ``label`` (*str*, optional) – name of the electrode (e.g., from the COMSOL geometry)
* ``x_center`` (*float*) – x-position of the center of the CUFF, in µm (default: ``0``)
* ``contact_length`` (*float*) – length of the contact site along the x-axis, in µm (default: ``100``)
* ``is_volume`` (*bool*) – if ``True``, the contact is retained in the mesh as a volume (default: ``True``)
* ``contact_thickness`` (*float*) – thickness of the contact, in µm (default: ``5``)
* ``insulator`` (*bool*) – if ``True``, an insulating ring surrounds the contact (default: ``True``)
* ``insulator_thickness`` (*float*) – thickness of the insulator ring, in µm (default: ``20``)
* ``insulator_length`` (*float*) – length of the insulating ring along the x-axis, in µm (default: ``1000``)

**Multi-contact CUFF electrodes**  
These electrodes extend the mono-contact CUFF configuration to include multiple, evenly spaced contacts.  
The :class:`~nrv.fmod.CUFF_MP_electrode` class inherits from :class:`~nrv.fmod.CUFF_electrode` and introduces an additional parameter:

* ``N_contact`` (*int*) – number of contact sites on the CUFF (default: ``4``)

.. note::

   CUFF electrodes are suitable for simulations involving external stimulation or recording interfaces. As with other electrode types, proper assignment of ``ID`` values is important when using multiple electrodes in a simulation.


.. note::

   As with all electrode types in NRV, it is the **user's responsibility** to assign consistent and unique ``ID`` values when defining multiple electrodes in a simulation.

