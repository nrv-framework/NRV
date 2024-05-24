============
Optimization
============
NRV has an integrated optimization layer that allows the impact of input tuning parameters on the outcome of a simulation to be optimized directly.

Optimization Problem
====================

In NRV, an optimization problem is composed of two components, as illustrated by the figure below: 
 - **An optimizer** : based on third party libraries (``scipy`` and ``pyswarms``) algorithms.
 - A cost function: a function from :math:`\mathbb{R}^n` to :math:`\mathbb{R}` that is to be minimised.

In addition, NRV introduces a way to evaluate the impact of specific parameters in simulations and final cost assessment through a `Cost_Function` class consisting of

- A filter: an optional Python ``callable`` object for vector formatting or space restriction.
- A static context: an NRV-:doc:`simulate</usersguide/simulables>` object as an axon, fascicle or nerve, set as the base for the simulation.
- A ``context_modifier`` object: creates an updated local context from the static context and input vector.
- A ``cost_evaluation`` object: evaluates a cost from the simulation results. It's a generic ``callable`` class, allowing user-defined functions.
- A saver: an optional Python ``callable`` object saving specific parameters and results during the optimization

.. figure:: ../images/optim.png

The creation of an optimization problem is handle in NRV by the class :class:`~nrv.optim.Problems.Problem`. An instance of this class is composed of an ``optimizer`` and a ``cost_fonction`` which can be simply set as the example bellow:

::

    my_prob = nrv.Problem()
    my_prob.costfunction = my_cost
    my_prob.optimizer = my_optimizer

Once correctly set, the optimizer can be started by calling the instance as shown below. The optimization returns an :class:`~nrv.optim.optim_utils.optim_results.optim_results` object containing various information and results of the optimization.

::

    res_optim = my_prob(**kwrgs)

.. note:: 
    Key arguments can be added to modify some parameters of the ``optimizer``. All keys used for the optimizer instantiation can be reset when the optimizer is called.




Cost Function
=============

As mentioned above, cost_functions are composed of the following components:
 - A static context
 - A context modifier
 - A cost evaluation
 - An optional filter

It can be either defined from the instantiation
::

    my_cost = nrv.cost_function(
    static_context=my_static_context,
    context_modifier=my_context_modifier,
    cost_evaluation=my_cost_evaluation,
    kwargs_S=kwarg_sim
    kwargs_CM=kwarg_cm
    kwargs_CE=kwarg_ce)

Or be generated empty and filled afterward:

::

    my_cost = nrv.cost_function()
    [...]
    my_cost.set_static_context(my_static_context, **kwarg_sim)
    my_cost.set_context_modifier(my_context_modifier, **kwarg_cm)
    my_cost0.set_cost_evaluation(my_cost_evaluation, **kwarg_ce)


Context Modifier
----------------

Context modifiers are functions or callable classes adapting the static context to 


Several context modifiers have been implemented in NRV for general uses. All of them inherit from a generic context modifier class: :class:`~nrv.optim.optim_utils.ContextModifiers.context_modifier`. A list of existing context is given bellow:

.. list-table:: **List of built-in context modifiers**
    :widths: 10 150
    :header-rows: 1
    :align: center

    *   - Name
        - description
    *   - :class:`~nrv.optim.optim_utils.ContextModifiers.stimulus_CM`
        - Generic context modifiers targeting the modification of an electrode stimulus. This modification can either be done by interpolation the input vector or by generating a specific stimulus from this vector.
    *   - :class:`~nrv.optim.optim_utils.ContextModifiers.biphasic_stimulus_CM`
        - Context modifier, inheriting from :class:`~nrv.optim.optim_utils.ContextModifiers.stimulus_CM`, which adds use inputs parameters to tune a :class:`~nrv.fmod.stimulus.stimulus.harmonic_pulse` to an electrode of the static context.
    *   - :class:`~nrv.optim.optim_utils.ContextModifiers.harmonic_stimulus_CM`
        - Context modifier, inheriting from :class:`~nrv.optim.optim_utils.ContextModifiers.stimulus_CM`, which adds use inputs parameters to tune a :class:`~nrv.fmod.stimulus.stimulus.harmonic_pulse` to an electrode of the static context.
    *   - :class:`~nrv.optim.optim_utils.ContextModifiers.harmonic_stimulus_with_pw_CM`
        - 


Cost Evaluation
---------------

.. list-table:: **List of built-in context modifiers**
    :widths: 10 150
    :header-rows: 1
    :align: center

    *   - Name
        - description
    *   - :class:`~nrv.optim.optim_utils.CostEvaluation.charge_quantity_CE`
        - 
    *   - :class:`~nrv.optim.optim_utils.CostEvaluation.stim_energy_CE`
        - 
    *   - :class:`~nrv.optim.optim_utils.CostEvaluation.recrutement_count_CE`
        - 



Filter (optional)
-----------------


Optimizer
=========

Optimizer is an abstract class from which inherit optimizing classes compatible with NRV formalism.

Two types optimizing classes are implemented in NRV: 
 * ``scipy_optimizer`` for heuristic optimization scipy.optim module
 * ``PSO_optimizer`` for meta-adapted heuristic optimization from pyswarms module


 * scipy_optimizer: 

.. list-table:: **List of optimizers in NRV**
    :widths: 10 150
    :header-rows: 1
    :align: center

    *   - Name
        - description
    *   - :class:`~nrv.optim.Optimizers.scipy_optimizer`
        - 
    *   - :class:`~nrv.optim.Optimizers.PSO_optimizer`
        - 

