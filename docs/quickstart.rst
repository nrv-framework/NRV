==========
Quickstart
==========

First steps into NRV: a simple axon
===================================

Context
-------

As a very first step, let us consider a simple unmyelinated axon stimulated by an intra and then a extra-cellular electrode. We should initiate 1 action potential per stimulation, that we will place in the center of the axon. We should also be able to observe action potential propagation, in the to directions. The figure bellow illustrate this 

FIGURE

As expected, we will need to use NRV for axonal simulation. We will also use matplotlib to look at results:

::

    import nrv
    import matplotlib.pyplot as plt

Axon declaration
----------------

Axon declaration is pretty straight forward : 

::

    y = 0                       # axon y position, in [um]
    z = 0                       # axon z position, in [um]
    d = 1                       # axon diameter, in [um]
    L = 5000                    # axon length, along x axis, in [um]
    axon1 = nrv.unmyelinated(y,z,d,L)

All axons are alond the x axis, so y and z positions have to be specified. An axon is also defined with a diameter and length. All spacial units in NRV are in micro-metters.