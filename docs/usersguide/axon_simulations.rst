Axon Simulations
================

The ``axon_simulations`` module provides several high-level functions to facilitate simulation and exploration at the axon level.

Search Threshold Functions
--------------------------

NRV provides two main functions to estimate axon thresholds:

- :func:`~nrv.ui.axon_AP_threshold`: Finds the activation threshold.
- :func:`~nrv.ui.axon_block_threshold`: Finds the block threshold.

These functions use a binary search approach to efficiently estimate the required threshold. They require at least three arguments:

- An :class:`~nrv.nmod.axon` object (pre-configured) on which the threshold search is performed.
- ``max_amp``: A float specifying the maximum amplitude (in µA) for the search.
- A ``callable`` object to update the stimulation of the axon between each iteration. This object **must** take at least two arguments: the :class:`~nrv.nmod.axon` object and the new stimulation amplitude.

Example usage:

.. code-block:: python

    def my_update_function(axon, amp, pw, some_args):
        my_new_stim = nrv.stimulus()
        my_new_stim.any_stim(amp)
        axon.change_stimulus_from_electrode(elec_id, my_new_stim)

    my_arg_stim = {'pw': 100, 'other_param': value}

    my_threshold = nrv.axon_AP_threshold(
        axon=my_axon,
        amp_max=my_max_amp,
        update_func=my_update_function,
        args_update=my_arg_stim
    )

.. seealso::
    :doc:`Example 16 <../examples/generic/16_activation_thresholds_arbitrary>` - Practical applications of :func:`~nrv.ui.axon_AP_threshold`.

Search Threshold Dispatching Functions
----------------------------------------

NRV also includes the function :func:`~nrv.ui.search_threshold_dispatcher`, which enables parallelized execution of threshold searches over multiple CPU cores. This is useful for evaluating the effect of varying one parameter across a range of values.

This function requires:

- A ``callable`` object to be dispatched to each core. This function must take **at least one argument**, representing the parameter of interest to be varied.
- A list of parameter values to test.
- Optionally, the number of CPU cores to allocate. If not provided, all available cores will be used.

Example usage:

.. code-block:: python

    def my_process_threshold(my_param):
        my_arg['my_param'] = my_param
        return nrv.axon_AP_threshold(
            axon=my_axon,
            amp_max=my_amp_max,
            update_func=my_update_function,
            args_update=my_arg,
            verbose=False
        )

    if __name__ == '__main__':
        my_thresholds = nrv.threshold_search_dispatcher(
            my_process_threshold,
            my_param_list
        )

.. seealso::
    :doc:`Example 17 <../examples/generic/17_threshold_search_dispatcher>` - Demonstration of :func:`~nrv.utils.cell._axon_simulations.search_threshold_dispatcher`.

.. warning::
    Always enclose the call to :func:`~nrv.ui.search_threshold_dispatcher` within the ``if __name__ == '__main__':`` block. Otherwise, each core may redundantly execute the full parameter list.

.. warning::
    The function :func:`~nrv.ui.search_threshold_dispatcher` may be **unstable when executed from Jupyter notebooks**. It can hang or never return, depending on the multiprocessing backend and platform. For best results, run this function from a standalone script (e.g., ``.py`` file executed via terminal).
