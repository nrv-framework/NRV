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

Unmyelinated axons
------------------

blablablabla

Myelinated axons
----------------

blablablabla

Fascicles
=========

blablablabla

Nerves
======

blablablabla
