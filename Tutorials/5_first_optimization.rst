First optimization problem using NRV
====================================

In this tutorial, the optimization formalism used in NRV is illustrated
through a detailed example.

The very first step is, as usual, to import NRV and the required
packages and to generate an outputs’ repository.

.. code:: ipython3

    import matplotlib.pyplot as plt
    import numpy as np
    import os
    import sys
    sys.path.append("../")
    import nrv
    
    test_name = "Tutorial_5"
    dir_res = f"./{test_name}/"
    if not os.path.isdir(dir_res):
        os.mkdir(dir_res)

Principle
---------

In NRV, an optimization problem is composed of two components, as
illustrated by the figure below: - **An optimizer** : based on third
party libraries (``scipy`` and ``pyswarms``) algorithms. - **A cost
function**: a function from :math:`\real^n` to :math:`\real` that should
be minimized.

The framework introduces an easy way to evaluate the impact of specific
parameters in simulations and final cost assessment through a
``Cost_Function``-class consisting in:

-  A filter: an optional Python ``callable``-object for vector
   formatting or space restriction.
-  A static context: the initial point of the simulation, often a
   NRV-nmod object like axon, fascicle, or nerve, with a
   ``simulate``-method.
-  A ``ContextModifier``-object: creates an updated local context from
   the static context and input vector.
-  A ``CostEvaluation``-object: evaluates a cost from simulation
   results. It’s a generic Python ``callable``-class, allowing
   user-defined functions.

.. figure:: ../docs/images/optim.png
   :alt: alt text


Context
-------

To ease the understanding of this tutorial, two static contexts will be
considerate with an increasing level of complexity:

-  **Context 1.** The stimulation is applied on a single fibre
   (:math:`N_{axon}=1`).

-  **Context 2.** A monofasciclar nerve filled with 98 myelinated fibres
   (:math:`N_{axon}=98`).

Finally, to introduce various ``context_modifiers``, two
``cost_functions`` will be presented in this tutorial.

First optimization: Single axon
-------------------------------

The objective of the first optimization problem is to minimize a
stimulus energy required by a LIFE-electrode to trigger a single
myelinated fibre.

Static context
~~~~~~~~~~~~~~

The first step to implement the optimization is to define the static
context. This can be done the same way as for standard simulations as
shown in previous tutorials.

Here a

.. code:: ipython3

    axon_file = dir_res + "myelinated_axon.json"
    
    ax_l = 10000 # um
    ax_d=10
    ax_y=50
    ax_z=0
    axon_1 = nrv.myelinated(L=ax_l, d=ax_d, y=ax_y, z=ax_z)
    
    
    LIFE_stim0 = nrv.FEM_stimulation()
    LIFE_stim0.reshape_nerve(Length=ax_l)
    life_d = 25 # um
    life_length = 1000 # um
    life_x_0_offset = (ax_l-life_length)/2
    life_y_c_0 = 0
    life_z_c_0 = 0
    elec_0 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_0_offset, life_y_c_0, life_z_c_0)
    
    dummy_stim = nrv.stimulus()
    dummy_stim.pulse(0, 0.1, 1)
    LIFE_stim0.add_electrode(elec_0, dummy_stim)
    
    axon_1.attach_extracellular_stimulation(LIFE_stim0)
    axon_1.get_electrodes_footprints_on_axon()
    _ = axon_1.save(save=True, fname=axon_file, extracel_context=True)
    
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    axon_1.plot(ax)
    ax.set_xlim((-1.2*ax_y, 1.2*ax_y))
    ax.set_ylim((-1.2*ax_y, 1.2*ax_y))
    
    del axon_1


.. parsed-literal::

    NRV INFO: Mesh properties:
    NRV INFO: Number of processes : 3
    NRV INFO: Number of entities : 36
    NRV INFO: Number of nodes : 11380
    NRV INFO: Number of elements : 80964
    NRV INFO: Static/Quasi-Static electrical current problem
    NRV INFO: FEN4NRV: setup the bilinear form
    NRV INFO: FEN4NRV: setup the linear form
    NRV INFO: Static/Quasi-Static electrical current problem
    NRV INFO: FEN4NRV: solving electrical potential
    NRV INFO: FEN4NRV: solved in 4.02306056022644 s



.. image:: 5_first_optimization_files/5_first_optimization_6_1.png


Optimization
------------

.. code:: ipython3

    ## Cost function definition
    static_context = axon_file
    
    fname0 = dir_res + "/energy_optim_pso_biphasic.json"
    #fname2 = dir_res + "/energy_optim_pso_spline2pts.json"
    
    costfname0 = dir_res + "/energy_cost_biphasic.csv"
    #costfname2 = dir_res + "/energy_cost_spline2pts.csv"
    
    t_sim = 5
    t_start = 1
    t_end = 0.5
    I_max_abs = 100
    t_bound = (0, t_end)
    I_bound = (-I_max_abs, 0)
    duration_bound = (0.01, 0.5)




.. code:: ipython3

    costR = nrv.recrutement_count_CE(reverse=True)
    costC = nrv.stim_energy_CE()
    
    cost_evaluation = costR + 0.01 * costC

Context modifier
^^^^^^^^^^^^^^^^

The ``context_modifier`` is a function or a callable class instance
which modifies the static context

.. code:: ipython3

    context_modifier0 = nrv.biphasic_stimulus_CM(start=t_start, I_cathod="0", T_cathod=0.1*t_end, I_anod=0)



.. code:: ipython3

    kwarg_sim = {
        
        "dt":0.002,
    }
    
    my_cost0 = nrv.CostFunction(
        static_context=static_context,
        context_modifier=context_modifier0,
        cost_evaluation=cost_evaluation,
        kwargs_S=kwarg_sim,
        t_sim=t_sim,
        file_name=costfname0,
    )



.. code:: ipython3

    # Problem definition
    test_prob = nrv.Problem(save_problem_results=False)
    test_prob.optimizer = nrv.PSO_optimizer()
    
    bounds0 = (
        (0, I_max_abs),
    )
    pso_kwargs0 = {
        "maxiter" : 50,
        "n_particles" : 20,
        "opt_type" : "local",
        "options": {'c1': 0.45, 'c2': 0.45, 'w': 0.75, 'k': 5, 'p': 1},
        "bh_strategy": "reflective",
        "dimensions" : 1,
        "bounds" : bounds0,
        "comment":"pulse"}
    
    test_prob.costfunction = my_cost0
    
    res0 = test_prob(problem_fname=fname0, **pso_kwargs0)



::


    ---------------------------------------------------------------------------

    KeyboardInterrupt                         Traceback (most recent call last)

    File ~/_offline/Codes/Libraries/NRV/Tutorials/../nrv/optim/Optimizers.py:393, in PSO_optimizer.minimize(self, f_swarm, **kwargs)
        392 t0 = perf_counter()
    --> 393 cost, pos = optimizer.optimize(
        394     f_swarm,
        395     iters=self.maxiter,
        396     n_processes=self.n_processes,
        397     verbose=verbose,
        398 )
        399 t_opt = perf_counter() - t0


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/pyswarms/single/general_optimizer.py:244, in GeneralOptimizerPSO.optimize(self, objective_func, iters, n_processes, verbose, **kwargs)
        243 ftol_history = deque(maxlen=self.ftol_iter)
    --> 244 for i in self.rep.pbar(iters, self.name) if verbose else range(iters):
        245     # Compute cost for current position and personal best
        246     # fmt: off
        247     self.swarm.current_cost = compute_objective_function(self.swarm, objective_func, pool=pool, **kwargs)


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/pyswarms/utils/reporter/reporter.py:217, in Reporter.pbar(self, iters, desc)
        191 """Create a tqdm iterable
        192 
        193 You can use this method to create progress bars. It uses a set
       (...)
        215     A tqdm iterable
        216 """
    --> 217 self.t = trange(iters, desc=desc, bar_format=self._bar_fmt)
        218 return self.t


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/tqdm/std.py:1524, in trange(*args, **kwargs)
       1523 """Shortcut for tqdm(range(*args), **kwargs)."""
    -> 1524 return tqdm(range(*args), **kwargs)


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/tqdm/std.py:665, in tqdm.__new__(cls, *_, **__)
        664 instance = object.__new__(cls)
    --> 665 with cls.get_lock():  # also constructs lock if non-existent
        666     cls._instances.add(instance)


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/tqdm/std.py:764, in tqdm.get_lock(cls)
        763 if not hasattr(cls, '_lock'):
    --> 764     cls._lock = TqdmDefaultWriteLock()
        765 return cls._lock


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/tqdm/std.py:97, in TqdmDefaultWriteLock.__init__(self)
         96     root_lock.acquire()
    ---> 97 cls.create_mp_lock()
         98 self.locks = [lk for lk in [cls.mp_lock, cls.th_lock] if lk is not None]


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/site-packages/tqdm/std.py:121, in TqdmDefaultWriteLock.create_mp_lock(cls)
        120     from multiprocessing import RLock
    --> 121     cls.mp_lock = RLock()
        122 except (ImportError, OSError):  # pragma: no cover


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/multiprocessing/context.py:73, in BaseContext.RLock(self)
         72 from .synchronize import RLock
    ---> 73 return RLock(ctx=self.get_context())


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/multiprocessing/synchronize.py:194, in RLock.__init__(self, ctx)
        193 def __init__(self, *, ctx):
    --> 194     SemLock.__init__(self, RECURSIVE_MUTEX, 1, 1, ctx=ctx)


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/multiprocessing/synchronize.py:79, in SemLock.__init__(self, kind, value, maxvalue, ctx)
         75 if self._semlock.name is not None:
         76     # We only get here if we are on Unix with forking
         77     # disabled.  When the object is garbage collected or the
         78     # process shuts down we unlink the semaphore name
    ---> 79     from .resource_tracker import register
         80     register(self._semlock.name, "semaphore")


    File /opt/homebrew/Caskroom/miniforge/base/envs/nrvdev/lib/python3.12/multiprocessing/resource_tracker.py:38
         37 import _multiprocessing
    ---> 38 import _posixshmem
         40 # Use sem_unlink() to clean up named semaphores.
         41 #
         42 # sem_unlink() may be missing if the Python build process detected the
         43 # absence of POSIX named semaphores. In that case, no named semaphores were
         44 # ever opened, so no cleanup would be necessary.


    KeyboardInterrupt: 

    
    During handling of the above exception, another exception occurred:


    KeyboardInterrupt                         Traceback (most recent call last)

    File ~/_offline/Codes/Libraries/NRV/Tutorials/../nrv/optim/Problems.py:131, in Problem.__call__(self, **kwargs)
        128     self._SwarmCostFunction = cost_function_swarm_from_particle(
        129         self._CostFunction
        130     )
    --> 131     results = self._Optimizer(self._SwarmCostFunction, **kwargs)
        132 MCH.master_broadcasts_to_all({"status": "Completed"})


    File ~/_offline/Codes/Libraries/NRV/Tutorials/../nrv/optim/Optimizers.py:45, in Optimizer.__call__(self, f, **kwargs)
         44 def __call__(self, f, **kwargs: Any) -> optim_results:
    ---> 45     return self.minimize(f, **kwargs)


    File ~/_offline/Codes/Libraries/NRV/Tutorials/../nrv/optim/Optimizers.py:441, in PSO_optimizer.minimize(self, f_swarm, **kwargs)
        440         json.dump(results, outfile)
    --> 441 raise KeyboardInterrupt
        442 sys.exit(1)


    KeyboardInterrupt: 

    
    During handling of the above exception, another exception occurred:


    KeyboardInterrupt                         Traceback (most recent call last)

    Cell In[12], line 20
          8 pso_kwargs0 = {
          9     "maxiter" : 50,
         10     "n_particles" : 20,
       (...)
         15     "bounds" : bounds0,
         16     "comment":"pulse"}
         18 test_prob.costfunction = my_cost0
    ---> 20 res0 = test_prob(problem_fname=fname0, **pso_kwargs0)


    File ~/_offline/Codes/Libraries/NRV/Tutorials/../nrv/optim/Problems.py:134, in Problem.__call__(self, **kwargs)
        132     MCH.master_broadcasts_to_all({"status": "Completed"})
        133 except KeyboardInterrupt:
    --> 134     raise KeyboardInterrupt
        135 except:
        136     MCH.master_broadcasts_to_all({"status": "Error"})


    KeyboardInterrupt: 


.. code:: ipython3

    res0.plot_cost_history(generatefigure=True)
    stim = context_modifier0(res0.x, static_context).extra_stim.stimuli[0]
    fig, ax = plt.subplots()
    stim.plot(ax)
    
    print(bounds0, res0.x)



.. parsed-literal::

    ((0, 100),) [10.14695342695113]



.. image:: 5_first_optimization_files/5_first_optimization_17_1.png



.. image:: 5_first_optimization_files/5_first_optimization_17_2.png


Second optimization
-------------------

.. code:: ipython3

    nerve_file = dir_res + "nerve.json"
    
    outer_d = 5 # mm
    nerve_d = 300 # um
    nerve_l = 10000 # um
    
    fasc1_d = 250 # um
    fasc1_y = 0
    fasc1_z = 0
    n_ax1 = 100
    
    
    nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)
    
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax1, percent_unmyel=0, M_stat="Ochoa_M", U_stat="Ochoa_U",)
    
    fascicle_1 = nrv.fascicle(ID=0)      #we can add diameter here / no need to call define_circular_contour (not tested)
    fascicle_1.define_circular_contour(fasc1_d)
    fascicle_1.fill_with_population(axons_diameters, axons_type, fit_to_size=True,delta=5)
    fascicle_1.generate_random_NoR_position()
    nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)
    
    # LIFE in neither of the two fascicles
    LIFE_stim0 = nrv.FEM_stimulation()
    life_x_0_offset = (nerve_l-life_length)/2
    elec_0 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_0_offset, life_y_c_0, life_z_c_0)
    
    stim0 = nrv.stimulus()
    stim0.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    LIFE_stim0.add_electrode(elec_0, stim0)
    nerve_1.attach_extracellular_stimulation(LIFE_stim0)
    
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_1.plot(ax)
    
    nerve_1.compute_electrodes_footprints()
    nerve_1.set_parameters(postproc_script="is_excited")
    _ = nerve_1.save(fname=nerve_file, extracel_context=True)


.. parsed-literal::

    NRV INFO: On 100 axons to generate, there are 100 Myelinated and 0 Unmyelinated
    NRV INFO: Axon packing initiated. This might take a while...


.. parsed-literal::

    100%|██████████| 20000/20000 [00:01<00:00, 15418.33it/s]


.. parsed-literal::

    NRV INFO: Packing done!
    NRV INFO: From Fascicle 0: Electrode/Axons overlap, 2 axons will be removed from the fascicle
    NRV INFO: 100 axons remaining
    NRV INFO: Mesh properties:
    NRV INFO: Number of processes : 3
    NRV INFO: Number of entities : 36
    NRV INFO: Number of nodes : 13638
    NRV INFO: Number of elements : 97211
    NRV INFO: Static/Quasi-Static electrical current problem
    NRV INFO: FEN4NRV: setup the bilinear form
    NRV INFO: FEN4NRV: setup the linear form
    NRV INFO: FEN4NRV: solving electrical potential
    NRV INFO: FEN4NRV: solved in 4.748852252960205 s



.. image:: 5_first_optimization_files/5_first_optimization_19_3.png

