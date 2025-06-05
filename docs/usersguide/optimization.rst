===============
Optimization
===============

NRV includes an integrated optimization layer, enabling direct tuning of input parameters to optimize the outcomes of simulations.

.. seealso::

    :doc:`Tutorial 5 </tutorials/5_first_optimization>` — First optimization problem using NRV

Optimization Problem
---------------------

In NRV, an optimization problem consists of two main components:

- **An optimizer**: based on algorithms from third-party libraries such as ``scipy`` and ``pyswarms``.
- **A cost function**: a function :math:`\mathbb{R}^n \rightarrow \mathbb{R}` to be minimized.

To evaluate how specific parameters affect simulations and overall cost, NRV defines a :class:`nrv.optim.cost_function` class composed of:

- A **filter** (optional): a Python ``callable`` for vector formatting or dimensionality reduction.
- A **static context**: an NRV :doc:`simulable </usersguide/simulables>` object (axon, fascicle, or nerve) used as the simulation base.
- A **context modifier**: generates a modified local context from the static context and input vector.
- A **cost evaluation**: evaluates simulation results to compute a scalar cost. This is a generic, user-definable ``callable``.
- A **saver** (optional): stores intermediate parameters or results during optimization.

.. figure:: ../images/optim.png
    :align: center
    :alt: NRV optimization structure

The optimization problem is managed in NRV using the :class:`~nrv.optim.Problem` class. A typical setup looks like:

.. code-block:: python

    my_prob = nrv.Problem()
    my_prob.costfunction = my_cost
    my_prob.optimizer = my_optimizer

Once defined, the problem can be executed by calling the instance:

.. code-block:: python

    res_optim = my_prob(**kwargs)

.. note::

    Additional keyword arguments (``kwargs``) can be passed to override optimizer parameters at runtime.

.. tip::

    Parallel execution is fully supported by :class:`~nrv.optim.Problem` and :class:`~nrv.optim.cost_function`. Optimization involving `nerve` or `fascicle` contexts can be parallelized. See the :doc:`Parallel Computation Guide </usersguide/parallel>` for more details.

Cost Function
-------------

The first component of an optimization problem is the **cost function**. NRV provides the :class:`~nrv.optim.cost_function` class, enabling users to customize cost functions using three main components:

- A **static context**
- A **context modifier**
- A **cost evaluation**

You can instantiate the cost function directly:

.. code-block:: python

    my_cost = nrv.cost_function(
        static_context=my_static_context,
        context_modifier=my_context_modifier,
        cost_evaluation=my_cost_evaluation,
        kwargs_S=kwarg_sim,
        kwargs_CM=kwarg_cm,
        kwargs_CE=kwarg_ce
    )

Or define it incrementally:

.. code-block:: python

    my_cost = nrv.cost_function()
    my_cost.set_static_context(my_static_context, **kwarg_sim)
    my_cost.set_context_modifier(my_context_modifier, **kwarg_cm)
    my_cost.set_cost_evaluation(my_cost_evaluation, **kwarg_ce)

.. warning::

    :class:`~nrv.optim.cost_function` cannot currently be saved using the ``save`` method due to the custom nature of the ``cost_evaluation`` component. This feature is planned for a future release.

Context Modifier
----------------

**Context modifiers** are callable objects that modify the static context based on the input vector. They may change stimulation parameters, electrode configurations, or other simulation features.

NRV includes several built-in context modifiers, all inheriting from :class:`~nrv.optim.optim_utils.context_modifier`.

.. list-table:: **Built-in Context Modifiers**
    :widths: 10 150 10
    :header-rows: 1
    :align: center

    * - Name
      - Description
      - See Also
    * - :class:`~nrv.optim.optim_utils.stimulus_CM`
      - Modifies electrode stimulus using interpolation or waveform generation from input vectors.
      - :doc:`o02 </examples/optim/o02_stimulus_CM>`, :doc:`T5 </tutorials/5_first_optimization>`
    * - :class:`~nrv.optim.optim_utils.biphasic_stimulus_CM`
      - Specializes stimulus_CM to configure biphasic pulses using user inputs.
      - :doc:`o03 </examples/optim/o03_biphasic_stimulus_CM>`, :doc:`T5 </tutorials/5_first_optimization>`
    * - :class:`~nrv.optim.optim_utils.harmonic_stimulus_CM`
      - Specializes stimulus_CM to configure harmonic pulses.
      - :doc:`o04 </examples/optim/o04_harmonic_stimulus_CM>`

You can also define your own modifier:

.. code-block:: python

    def homemade_context_modifier(X: np.ndarray, static_context: NRV_simulable, **kwargs) -> NRV_simulable:
        local_sim = nrv.load_any(static_context, ...)
        # Modify local_sim based on X
        return local_sim

.. note::

    Custom context modifier **classes** should implement the ``__call__`` method with the structure shown above.

Cost Evaluation
---------------

**Cost evaluations** compute a scalar metric from simulation results. These are also callable and typically subclass :class:`~nrv.utils.cost_evaluation`.

Benefits of subclassing:

1. Supports algebraic composition of multiple evaluations.
2. Integrates cleanly with NRV’s optimization framework.

.. list-table:: **Built-in Cost Evaluations**
    :widths: 10 150
    :header-rows: 1
    :align: center

    * - Name
      - Description
    * - :class:`~nrv.optim.optim_utils.raster_count_CE`
      - Counts spikes per fiber during simulation.
    * - :class:`~nrv.optim.optim_utils.recrutement_count_CE`
      - Counts activated or non-activated fibers.
    * - :class:`~nrv.optim.optim_utils.charge_quantity_CE`
      - Estimates charge injected by one or more electrodes.
    * - :class:`~nrv.optim.optim_utils.stim_energy_CE`
      - Estimates energy injected during stimulation.

.. warning::

    :class:`~nrv.utils.cost_evaluation` and its subclasses currently **cannot be saved** using the ``save`` method.

You can define a custom evaluation:

.. code-block:: python

    def homemade_cost_evaluation(results: sim_results, **kwargs) -> float:
        # Analyze `results` and return scalar cost
        return cost

Or define a class:

.. code-block:: python

    class homemade_cost_evaluation(nrv.cost_evaluation):
        def call_method(self, results: sim_results, **kwargs) -> float:
            return cost

Alternatively:

.. code-block:: python

    def __call__(self, results: sim_results, **kwargs) -> float:
        return cost

Filter (optional)
-----------------

**Filters** format the input vector before it is passed to the context modifier.

.. code-block:: python

    my_cost = nrv.cost_function(
        static_context=my_static_context,
        ...,
        filters=my_filter
    )

.. warning::

    Filters are **not recommended** and may be deprecated in future versions. Consider integrating input formatting into the context modifier instead.

Optimizer
---------

The second major component is the **optimizer**, which defines how to minimize the cost function. NRV provides two built-in optimizers, both subclasses of :class:`~nrv.optim.Optimizer`.

You can use either of the following styles:

.. code-block:: python

    res = my_optimizer.minimize(func_to_minimize, ...)
    # or simply
    res = my_optimizer(func_to_minimize, ...)

.. list-table:: **Available Optimizers**
    :widths: 10 150
    :header-rows: 1
    :align: center

    * - Name
      - Description
    * - :class:`~nrv.optim.scipy_optimizer`
      - Interface to `scipy.optimize.minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`_.
    * - :class:`~nrv.optim.PSO_optimizer`
      - Particle Swarm Optimizer using `Pyswarms <https://pyswarms.readthedocs.io/en/latest/>`_.

.. tip::

    Choose your optimizer based on problem type:

    - Use :class:`~nrv.optim.scipy_optimizer` for **continuous** problems.
    - Use :class:`~nrv.optim.PSO_optimizer` for **discontinuous** problems

.. warning::

    `Pyswarms <https://pyswarms.readthedocs.io/en/latest/>`_ support may be replaced by `scikit-opt <https://scikit-opt.github.io/scikit-opt/#/en/>`_ in future versions of NRV.
