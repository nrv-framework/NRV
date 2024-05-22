============
Optimization
============
NRV has an integrated optimization layer that allows the impact of input tuning parameters on the outcome of a simulation to be optimised directly.

Optimization Problem
====================

In NRV, an optimization problem is composed of two components, as illustrated by the figure below: 
 - **An optimizer** : based on third party libraries (``scipy`` and ``pyswarms``) algorithms.
 - A cost function: a function from :math:`\mathbb{R}^n` to :math:`\mathbb{R}` that is to be minimised.

In addition, NRV introduces a way to evaluate the impact of specific parameters in simulations and final cost assessment through a `Cost_Function` class consisting of

- A filter: an optional Python ``callable'' object for vector formatting or space restriction.
- A static context: an NRV-:doc:`simulate</usersguide/simulables>` object as an axon, fascicle or nerve, set as the base for the simulation.
- A ``ContextModifier'' object: creates an updated local context from the static context and input vector.
- A ``CostEvaluation'' object: evaluates a cost from the simulation results. It's a generic ``callable'' class, allowing user-defined functions.

.. figure:: ../images/optim.png

The creation of an optimization problem is handle in NRV by the class :class:`~nrv.optim.Problems.Problem`. An instance of this class is composed of an ``optimiser`` and a ``cost_fonction`` which can be simply set as the example bellow:

::

    my_prob = nrv.Problem()
    my_prob.costfunction = my_cost
    my_prob.optimizer = my_optimizer

Once correctly set, the optimiser can be started by calling the instance as shown below. The optimization returns an :class:`~nrv.optim.optim_utils.optim_results.optim_results` object containing various information and results of the optimization.

::

    res_optim = my_prob(**kwrgs)

.. note:: 
    Key arguments can be added to modify some parameters of the ``optimizer``. All keys used for the optimizer instantiation can be reset when the optimizer is called.



Cost Function
=============


Static Context
--------------

Context Modifier
----------------



Cost Evaluation
---------------

Filter (optional)
-----------------


Saver (optional)
----------------



Optimizer
=========

Optimize is an abstract class from which inherit optimizing classes compatible with NRV formalism.

Two types optimzing classes are implemented in NRV: 
 * ``scipy_optimizer`` for heuristic optimization scipy.optim module
 * ``PSO_optimizer`` for meta-adapted heuristic optimization from pyswarms module


* scipy_optimizer: 

    *
