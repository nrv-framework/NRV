==============
CL simulations
==============

``CL_simulation`` (Cellular level) provides several useful higher-level functions to facilitate simulation and exploration at the axon level.

Search threshold functions
==========================

NRV provides a function to search the activation threshold of axon (:func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold`) 
and its block threshold (:func:`~nrv.utils.cell.CL_simulations.axon_block_threshold`). Those functions use a binary search approach to efficiently
estimate the threshold. :func:`~nrv.utils.cell.CL_simulations.axon_AP_threshold` and :func:`~nrv.utils.cell.CL_simulations.axon_block_threshold` require at least three arguments:

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


Search threshold dispatching functions
======================================


NRV provides the :func:`~nrv.utils.cell.CL_simulations.search_threshold_dispatcher` function that dispatches search threshold 
functions on multiple CPU cores with specific simulation parameters. This function is particularly useful for efficiently exploring the effect of one parameter of the 
model on threshold, by leveraging on multiprocessing capabilities of the CPU instead of serialization. This function requires at least two arguments:

- A ``callable`` object which will be called on each requested core. This ``callable`` must take *at least* one parameter, corresponding to the parameter of interest, which value must be updated on each CPU core. 
- A list of values of the parameter of interest for which we want to evaluate the threshold.
- Optionally, we can specify the number of CPU core we want to allocate to the function. If not specified, the function will use every CPU cores available or required.

The following snippet shows one possible usage of the :func:`~nrv.utils.cell.CL_simulations.search_threshold_dispatcher`:
::

    def my_process_threshold(my_param):
        my_arg['my_param'] = my_param
        return(nrv.axon_AP_threshold(axon = my_axon,amp_max = my_amp_max,update_func = my_update_function, args_update=my_arg, verbose = False))

    if __name__ == '__main__':        
        my_thresholds = nrv.threshold_search_dispatcher(my_process_threshold,my_param_list)

.. tip::
    Some usage examples of :func:`~nrv.utils.cell.CL_simulations.search_threshold_dispatcher` are provided in :doc:`Example 17 <../examples/generic/example_17>`.


.. warning::
    This function must be executed in the ``'__main__'`` guard. If not, each CPU core will execute the search threshold function for the entire list. 