==========
Electrodes
==========

Electrodes are related to field computation, and are by definition extracellular electrodes in NRV. 
The implementation does not require the user to worry about computational considerations.
Is is possible for experienced user to add new electrodes.

Overview of existing electrodes, classes and custom electrodes possibilities
----------------------------------------------------------------------------

There are few classes that handle the electrodes in NRV. 
Currently, NRV handles 3 electrode families for simulations: Point Source electrodes, LIFE and CUFF.
The last one can have one or more electrical contacts for simulation only.

A class diagramm is given hereafter:

.. image:: ../images/electrodes_classdiagram.png

Two class are abstract and not accessible by the end user:

* ``electrodes``: this class is used the interface for simulable object to get simulation performed automatically. Even experienced user should not interface this class.

* ``FEM_electrodes``: this class is used for automated FEM simulation setup and computations. New electrodes should all be declared as class that inherit from FEM_electrodes.

The last class enables experienced user to define other families of electrodes. 
It is worth considering that such process implies to dive into the FEM definition of NRV to add electrode geometry to simulations. 
This process is not described in detail here, and developper should refer to `API documentation <#modules>`_.

Four classes are directly accessible by the end user:

* ``point_source_electrodes``,

* ``LIFE_electrodes``,

* ``CUFF_electrodes``, for CUFF electrodes with one circular contact

* ``CUFF_MP_electrodes``, for CUFF electrodes with more than one electrical contacts.

These class are further detailed bellow.

Few methods are generic to all electrodes:

* as all electrodes have inidividual identifiers (ID), there are getter and setter methods: `get_ID_number`, `set_ID_number`,

* as all electrodes have a footprint (see scientific foundation chapter), there are getter and setter methods: `get_footprint`, `set_footprint`. This last method should be avoided by non-experienced users;

* a method to force footprint computation by clearing the existing one: `clear_footprint`,

* a method to perform geometrical translation `translate` with the following parameters: `

    * x (float) x axis value for the translation in um

    * y (float) y axis value for the translation in um
    
    * z (float) z axis value for the translation in um

Point Source Electrodes
-----------------------

These electrodes are non-geometrical monopole punctual sources of current. 
**There is no model for a current return electrode**, and this electrode is only a theoretical model based on Point Source Approximation.
The usage is simple and the advantage is that the computational cost is very low as no finite elements computation step is required. 
Only one material can constutute the extracellular medium.
However, such electrodes should be limited to simple investigations or very first approximation simulations. 
The geometry of the electrodes is schematized in the figure bellow:

.. image:: ../images/electrodes_PSA.png

Point Source Electrode can be declared with the following parameters:

* x (float) x position of the electrode, in um

* y (float) y position of the electrode, in um

* z (float) z position of the electrode, in um

* ID (int) electrode identification number, set to 0 by default. 

**The user should take care of having cohere ID for electrodes.**


LIFE
----

LIFE stands for Longitudinal IntrFascicular Electrodes. 
These electrodes are usually inserted by a **thin wire that is not taken into account in simulations yet**.
We assume that these electrode are parallel to fibers. 
When setup inside a fascicle,or more generally in a nerve, a test to exclue overlapping fibers from the simulation is automatically performed.
LIFE and the associated geometrical parameters is illustrated bellow:

.. image:: ../images/electrodes_LIFE.png

LIFE can be declared with the following parameters:

* label (str) name of the electrode in the COMSOL file

* D (float) diameter of the electrode, in um

* length (float) length of the electrode, in um

* x_shift (float) geometrical offset from the start (x=0) of the simulation

* y_c (float) y-coordinate of the center of the electrode, in um

* z_c (float) z-coordinate of the center of the electrode, in um

* ID (int) electrode identification number, set to 0 by default. 

CUFF electrodes
---------------

CUFF electrodes are ring electrodes setup outide of the nerve and directly in contact with the epineurium. 
The schematized description of these electrodes is provided here bellow:

.. image:: ../images/electrodes_CUFF.png

* Mono-contact CUFF electrodes: Only one contact surround the nerve. The `CUFF_electrode` can be declared with the following parameters:

    * label (str): name of the electrode in the COMSOL file

    * x_center (float): x-position of the CUFF center in um, by default 0 

    * contact_length (float): length along x of the contact site in um, by default 100

    * is_volume (bool): if True the contact is kept on the mesh as a volume, by default True

    * contact_thickness (float): thickness of the contact site in um, by default 5

    * insulator(bool): remove insulator ring from the mesh (no conductivity), by default True

    * insulator_thickness (float): thickness of the insulator ring in um, by default 20

    * insulator_length (float): length along x of the insulator ring in um, by default 1000

* Multi-contact CUFF electrodes: this class directly inherit from the monocontact CUFF. There is one additional parameter for instanciation:

    *  N_contact (int): Number of contact site of the electrode, by default 4.
