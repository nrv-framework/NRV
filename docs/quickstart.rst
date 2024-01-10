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

Setting up the stimulation
--------------------------
**Intrcellular stimulation** is a method defined for axons (as well as bundles of fibers in NRV: fascicles and nerve). By default, it allows to setup a pulse defined by a starting time in ms, a duration in ms and an amplitude in nA. It is placed allong the axon in *relative position* (as the axon is 1D-defined along the x axis). This convention is not different from Neuron. Note that there is no restriction on how much clamp you can insert by axon.

Here is the code that setup the intracellular stimulation for the targeted context:

::

    ## Intracellular stimulation definition
    t_start = 0.5               # starting time, in [ms]
    duration = 0.25             # duration, in [ms]
    amplitude = 5               # amplitude, in [nA]
    relative_position = 0.5
    axon1.insert_I_Clamp(relative_position, t_start, duration, amplitude)

**Extracellular stimulation** is defined by different elements:
- one or more electrode(s), here we will use a point source approximated electrode which is a comon first approximation in neuroscience. Extra cellular potential are computed analytically and no geometry has to be specified. More complex or realistic electrodes will be introduced later,
- one or mode material(s), here we will use endoneurium with a typical value
- one or mode stimulus(-i), here we will use a biphasic waveshape typically used on implants.

Below is the code to place the electrode at the mid distance of the axon length, 100 microns away from the fiber:

::
    # electrode
    x_elec = L/2                # electrode x position, in [um]
    y_elec = 100                # electrode y position, in [um]
    z_elec = 0                  # electrode y position, in [um]
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

Here is how to import a material:

::

    # material properties
    epineurium = nrv.load_material('endoneurium_bhadra')



Simulating everything
---------------------

blablablablabla

Postprocessing and few comments
-------------------------------

blablablabla