:orphan:

Examples
========

Here are few example scripts to highlight possibilities toward using NRV in scientific life (for teaching about electrophysiology or biomedical research).



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script check is the logo can be found when the gallery is generated">

.. only:: html

  .. image:: /examples/images/thumb/sphx_glr_00_dummy_example_thumb.png
    :alt:

  :doc:`/examples/00_dummy_example`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Dummy example</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:

   /examples/00_dummy_example

Generic Examples
----------------

This gallery consists of introductory examples of basic usage of NRV framework.



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This code performs basic simulation showing the propagation of action potential along axons for both unmyelinated and myelinated (saltatory conduction) fibers.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_01_propagation_Vmem_thumb.png
    :alt:

  :doc:`/examples/generic/01_propagation_Vmem`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Propagation of spike along the axon</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this script, the activation function for a point source electrode is ploted to anodic and cathodic stimulation. Then two simulation are performed. The first is an example of stimulation over the threshold and a spike is initiated at the midle of the fiber and propagates. The second shows a sub-threshold stimulation with no AP produced.fibers.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_02_activation_function_thumb.png
    :alt:

  :doc:`/examples/generic/02_activation_function`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Activation function</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script investigates the activation function for a longitudinal intrafascicular electrode (LIFE). It is similar to the previous example but include geometrical consideration, and computations are evaluated with the FEM solver in background (transparent for user).">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_03_LIFE_activation_function_thumb.png
    :alt:

  :doc:`/examples/generic/03_LIFE_activation_function`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Activation function for a LIFE</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This code highlith how to retrieve particle dynamics in results.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_04_AP_particles_thumb.png
    :alt:

  :doc:`/examples/generic/04_AP_particles`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Conductance model dynamic with stimulation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we use NRV to replicate some results from the in-silico study from Bhadra et al. published in 2006. This is an example of propagation block with an mylinated axon (MRG model). ">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_05_KES_conduction_block_thumb.png
    :alt:

  :doc:`/examples/generic/05_KES_conduction_block`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Conduction block with kHz stimulation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip=" This example shows how to easily generate and save a fascicle with the following contexts:">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_06_fascicle_with_contexts_thumb.png
    :alt:

  :doc:`/examples/generic/06_fascicle_with_contexts`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Generate a fascicle with all contexts</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example provides an example of action potential propagation block using a DC stimulation. This is perfectly working in silico, but can be unsafe in vivo as long DC values are unbalanced and can damage tissues surrounding the electrode">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_07_DC_block_thumb.png
    :alt:

  :doc:`/examples/generic/07_DC_block`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">DC Propagation block</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This file shows an example of action potential propagation block with an unmyelinated fiber.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_08_KES_block_unmyelinated_thumb.png
    :alt:

  :doc:`/examples/generic/08_KES_block_unmyelinated`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">KES propagation Block of unmyelinated fiber</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Subthreshold pre-pulses change the initial state of an axon membrane and thus can be used to control its excitability. Depolarizing pre-pulse generate a transient decrease in excitability (i.e. virtually increases the fiber&#x27;s threshold). This script illustrates this principle">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_09_Prepulse_waveform_thumb.png
    :alt:

  :doc:`/examples/generic/09_Prepulse_waveform`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Prepulse waveform stimulation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="A slowly rising pulse can help in triggering small diameter axon first. This script illustrates this phenomenon, with a constant stimulus, small diameter trigger a spike while larger axons are not depolarized sufficiently. ">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_10_Slowly_rising_thumb.png
    :alt:

  :doc:`/examples/generic/10_Slowly_rising`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Slowly Rising Pulse Stimulation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how logical and arithmetical operations on NRV&#x27;s stimulus&lt;../../usersguide/stimuli.rst&gt; object can facilitate the creation of complex stimulus.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_11_combining_stimulus_thumb.png
    :alt:

  :doc:`/examples/generic/11_combining_stimulus`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Combining Stimuli in NRV</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to plot structural parameters used in NRV&#x27;s myelinated fiber models.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_12_MRG_structural_parameters_thumb.png
    :alt:

  :doc:`/examples/generic/12_MRG_structural_parameters`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Plotting myelinated fibers structural parameters</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to plot available axon diameter distributions in NRV">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_13_axon_distributions_thumb.png
    :alt:

  :doc:`/examples/generic/13_axon_distributions`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Plotting available axon diameter distributions in NRV</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script evaluates the activation function for a cuff-like electrode">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_14_activation_function_cuff_thumb.png
    :alt:

  :doc:`/examples/generic/14_activation_function_cuff`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Activation function with a cuff-like electrode</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script evaluates the activation threshold of myelinated fibers when stimulated with a cuff electrode and with a LIFE">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_15_activation_thresholds_thumb.png
    :alt:

  :doc:`/examples/generic/15_activation_thresholds`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Activation thresholds with LIFE and cuff-like electrodes</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script shows how to use the axon_AP_threshold() function to evaluate axon thresholds with various stimulation waveforms.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_16_activation_thresholds_arbitrary_thumb.png
    :alt:

  :doc:`/examples/generic/16_activation_thresholds_arbitrary`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Activation thresholds with arbitrary settings</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This script shows how to use the methods of axon_results-class to detect and analyze action potentials.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_18_Action_Potential_Analysis_thumb.png
    :alt:

  :doc:`/examples/generic/18_Action_Potential_Analysis`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Analyzing Action Potentials in Axons</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Simple example showing how to handle builtin 2D shapes. More precisely this example shows how to:     - create shape by instantiating the corresponding class     - create shape using the generic create_cshape-function     - Use basic method implemented in CShape subclasses (~nrv.utils.geom.CShape.translate, rotate, get_point_inside)">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_19_build_geometry_thumb.png
    :alt:

  :doc:`/examples/generic/19_build_geometry`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Create a CShape geometry</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Simple example showing how to create an unplaced axon population with NRV and plot an histogram of the diameters values. In this example population are either created:     - From data (tupple, numpy.ndarray, dict or pandas.DataFrame)">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_20_create_population_thumb.png
    :alt:

  :doc:`/examples/generic/20_create_population`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Create an unplaced population</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Simple example to help using axon_population placement methods.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_21_place_population_thumb.png
    :alt:

  :doc:`/examples/generic/21_place_population`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Axon Population Placement</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Example showing two method to access sub population from axon_population.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_22_access_subpopulation_thumb.png
    :alt:

  :doc:`/examples/generic/22_access_subpopulation`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Access axon sub-poplation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Example of use of subpopulation for axon species targeted current clamp.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_23_subpop_iclamp_thumb.png
    :alt:

  :doc:`/examples/generic/23_subpop_iclamp`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Intracellular stimulation of axon subpopulations</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Practical example illustrating how a nerve simulation can be distributed across multiple cores.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_24_mp_nerve_sim_thumb.png
    :alt:

  :doc:`/examples/generic/24_mp_nerve_sim`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Parallel Nerve Simulation</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Practical example illustrating how to build a realistic nerve geometry from an image and simulate it with NRV.">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_25_test_fit_fasc_thumb.png
    :alt:

  :doc:`/examples/generic/25_test_fit_fasc`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Simulation of Realistic Geometry</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Generate an animation of the propagation of impedance shift along axons&#x27; membrane">

.. only:: html

  .. image:: /examples/generic/images/thumb/sphx_glr_26_anim_propagation_thumb.gif
    :alt:

  :doc:`/examples/generic/26_anim_propagation`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Propagation animation</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Optimization Examples
---------------------

This gallery consists of introductory examples for the use of `nrv.optim` module

.. seealso::
    - :doc:`Optimization users guide <../../usersguide/optimization>`
    - :doc:`Optimization tutorial <../../tutorials/5_first_optimization>`




.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example is an extension of the Tutorial 5, the optimization formalism used in NRV is illustrated through a detailed example.">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o01_nerve_optimization_thumb.png
    :alt:

  :doc:`/examples/optim/o01_nerve_optimization`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Optimization Pulse Stimulus on Nerve</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This small example shows a way to use the built-in stimulus_CM.">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o02_stimulus_CM_thumb.png
    :alt:

  :doc:`/examples/optim/o02_stimulus_CM`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Understanding context modifiers: stimulus_CM</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This small example shows a way to use the built-in biphasic_stimulus_CM.">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o03_biphasic_stimulus_CM_thumb.png
    :alt:

  :doc:`/examples/optim/o03_biphasic_stimulus_CM`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Understanding context modifiers: biphasic_stimulus_CM</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This small example shows a way to use the built-in harmonic_stimulus_CM.">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o04_harmonic_stimulus_CM_thumb.png
    :alt:

  :doc:`/examples/optim/o04_harmonic_stimulus_CM`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Understanding context modifiers: harmonic_stimulus_CM</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This is a very small example of a way to plot the built-in context modifiers&lt;../../usersguide/optimization#context-modifier&gt;">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o05_plot_CM_thumb.png
    :alt:

  :doc:`/examples/optim/o05_plot_CM`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Ploting Optimization - context modifiers</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to set the number of processes used for optimization. The exact same scenario from Tutorial 5 is used:">

.. only:: html

  .. image:: /examples/optim/images/thumb/sphx_glr_o06_mproc_optimization_thumb.png
    :alt:

  :doc:`/examples/optim/o06_mproc_optimization`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Optimization change number of processes</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:
   :includehidden:


   /examples/generic/index.rst
   /examples/optim/index.rst

