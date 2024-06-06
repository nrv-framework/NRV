==============
CL simulations
==============

``CL_simulation`` (Cellular level) provides several useful functions to facilitate simulation at the axon level.

Search threshold functions
==========================

NRV provides a function to search the activation threshold of axon (:func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold`) 
and its block threshold (:func:`~nrv.utils.cell.CL_simulations.axon_block_threshold`). Those functions use a binary search approach to efficiently
estimate the threshold. :func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold` and :func:`~nrv.utils.cell.CL_simulations.axon_block_threshold` require at least two arguments:

- :class:`~nrv.nmod.axons.axon` object, pre-configured, on which is the search is applied.
- ``max_amp``, a float which sets the maximum search amplitude, in µA.
- A ``callable`` object which is used to update the axon stimulation between each iteration of the search. This can be any callable object (a class, a function, etc) but *must* have at least to arguments (in order): :class:`~nrv.nmod.axons.axon` object to update, and a new stimulation amplitude to update with. 

The following snippet shows one possible usage of the :func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold`:
::

    def my_update_function(axon,amp, pw, some_args):
        my_new_stim = nrv.stimulus()
        my_new_stim.any_stim(amp)
        axon.change_stimulus_from_electrode(elec_id, my_new_stim)

    my_arg_stim = {some_args}

    my_threshold = nrv.axon_AP_threshold(axon = my_axon,amp_max = my_max_amp,
                                            update_func = my_update_function, args_update=my_arg_stim)

.. tip::
    Some usage examples of :func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold` are provided in :doc:`Example 16 <../examples/generic/example_16>`.