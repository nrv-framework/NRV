============
User's Guide
============

This page provide a non-exhaustive guided tour of NRV framework. The following pages give information on how to:

1. describe the content of a simulation:
    * axons, fascicles and nerves,
    * electrodes, stimuli and materials.
2. perform a simulation and first steps of post-processing
3. launch automated simulation for threshold finding
4. optimize a a generic problem

Before going furthern, it worths to mention that NRV is designed using Oriented-Oriented principles for two reasons:

* first, the description of simulation context and scenario implies the coordination of several physical objects (physiological such as fibers, fascicles, or technological such as electrodes for instance). Using a parallel to coding paradigm is a relatively natural way of easing the scripting.
* Python is by nature object oriented, and actions such as simulation, condifugration are naturally described and attached to main object.

Objects in NRV all inherit from an abstract class (called ``NRV_Class``) tha give them two spcial properties:
1. All objects can be saved as dictionary or in json files, so that any simulation, optimization problem or any implementation in general can be saved.
2. All objects can be described using a dictionary or a json file.

these two points and their consequences on syntax are described hereafter.

Note on object instantation
===========================

*to be written*

Note on object saving
=====================

*to be written*

Chapters of the User's Guide
============================

.. toctree::

   usersguide/simulables
   usersguide/stimuli
   usersguide/electrodes


