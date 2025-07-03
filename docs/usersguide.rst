============
User's Guide
============

This page provides a non-exhaustive guided tour of NRV framework. The following pages give information on how to:

1. describe the content of a simulation:
    * axons, fascicles and nerves,
    * electrodes, stimuli and materials.
2. perform a simulation and first steps of post-processing
3. launch automated simulation for threshold finding
4. optimize a generic problem

Before going further, it is worth noting that NRV is designed using Oriented-Oriented principles for two reasons:

* First, the description of simulation context and scenario implies the coordination of several physical objects (physiological such as fibers, fascicles, or technological such as electrodes for instance). Using a parallel to coding paradigm is a relatively natural way of easing the scripting.
* Python is by nature object-oriented, and actions such as simulation, configuration are naturally described and attached to main object.

Objects in NRV all inherit from an abstract class (the :class:`~nrv.backend._NRV_Class.NRV_class`) that gives them two special properties:



1. All objects can be saved as dictionary or in `json` files, so that any simulation, optimization problem or any implementation in general can be saved.
2. All objects can be described using a dictionary or a `json` file.

These two points and their consequences on syntax are described hereafter the link on chapters of the user's guide.

.. note::
    As a good practice, and especially when using multiprocessing, it is necessary to place code execution inside a Python main guard:

    .. autolink-skip::
    .. code-block:: python3

        if __name__ == "__main__":
            # your code here

    This ensures compatibility across platforms and prevents unexpected behavior when spawning subprocesses.

Chapters of the User's Guide
============================

.. toctree::

   usersguide/simulables
   usersguide/populations
   usersguide/geometry
   usersguide/stimuli
   usersguide/electrodes
   usersguide/materials
   usersguide/fem
   usersguide/postproc
   usersguide/parallel
   usersguide/optimization
   usersguide/axon_simulations


Note on object saving
=====================

As introduced above, classes inheriting from the :class:`~nrv.backend._NRV_Class.NRV_class` can be saved and loaded in python dictionary or `json` files. 
Let's see bellow a first example showing how to save a simple :class:`~nrv.nmod._unmyelinated.unmyelinated` axon object.

.. autolink-concat:: on
.. code-block:: python3

    import nrv
    y = 0                       # axon y position, in [um]
    z = 0                       # axon z position, in [um]
    d = 1                       # axon diameter, in [um]
    L = 5000                    # axon length, along x axis, in [um]
    axon1 = nrv.unmyelinated(y,z,d,L)

    ax_dict = axon1.save()

This code snippet first creates an unmyelinated axon as seen in :doc:`tutorials/1_intracellular_stimulation`. Then a python dictionary containing all this axon properties is generated in ``ax_dict``. To prevent the creation of unwanted files, the save method of most of :class:`~nrv.backend._NRV_Class.NRV_class` object does not save this dictionary into a `.json` file by defaults. 

To actually save the axon properties in a `.json` file, a `save`argument has to be set to ``True`` as shown bellow.

.. code-block:: python

    filename = "ax_file.json"
    ax_dict = axon1.save(save=True, fname=filename)

Note that the ``save`` method impose the extension of the file to be `json`. It is then not necessary to precise it in the filename and in the case where the filename does not and with `json`, this suffix is automatically added.

This ``save`` method comes together with a ``load`` method which allow to load the data of the instance from a python dictionary or a `json` file.

In the example below the axon is respectively generated from the dictionary and the file saved earlier.

.. code-block:: python

    del axon1

    axon2 = nrv.unmyelinated()
    axon2.load(ax_dict)
    print(axon2.L == L)

    del axon2
    axon3 = nrv.unmyelinated()
    axon3.load(filename)
    print(axon3.L == L)


Note on object instantiation
============================

The save/load generic methods allow the possibility to instantiate a :class:`~nrv.backend._NRV_Class.NRV_class` object from different ways.

- From the class (the python way):

.. code-block:: python

    axon1 = nrv.unmyelinated(y,z,d,L)
    assert axon1.L == L
    del axon1

- From the class (the dictionary way):

.. code-block:: python

    axon1 = nrv.unmyelinated(**ax_dict)
    assert axon1.L == L
    del axon1

- From a `json` file (the json way):

.. code-block:: python

    axon1 = nrv.unmyelinated()
    axon1.load(filename)
    assert axon1.L == L
    del axon1

- From anything (the easy way):

.. code-block:: python

    axon1 = nrv.load_any(ax_dict)
    assert axon1.L == L
    del axon1

    axon1 = nrv.load_any(filename)
    assert axon1.L == L
    del axon1



