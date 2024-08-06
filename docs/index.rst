.. NeuRon Virtualizer (NRV) documentation master file, created by
   sphinx-quickstart on Sun Jul 23 14:36:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NeuRon Virtualizer (NRV)'s documentation!
====================================================


NRV (or NeuRon Virtualizer) is a pythonic framework to enable fast and user-friendly simulations of the Peripheral Nervous System. Axons models are simulated with the NEURON software, and extracellular fields are computed either from analytic equations such as point source approximation or with a more detailed description of the nerve and electrode geometry and Finite Elements Method, either using COMSOL (additional commercial license required) or the FENICS project. All computations are performed with the quasi-static approximation of the Maxwell equations, no ephaptic coupling. Stimulation waveform can be of random shapes, and any kinds of electrode can be combined to model complex stimulation strategies.

NRV is optimized for large population of axons, from generating correct population following a specific diameter distribution, through automatic placement to computation and post-processing of the axons' activity when a stimulus is applied. Parallel computation, interface with NEURON and COMSOL and FENICS is automatically handled by NRV.

NRV was developed by contributors from the CELL research group at the Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University, until june 2023 and is now developed and maintained by the Bioelectronics group of laboratory IMS (UMR CNRS 5218), INP Bordeaux, U. Bordeaux.

.. SeeAlso::
   - **General information**: `nrv-framework.org <https://nrv-framework.org>`_
   - **Discussions and queries**: `Forum NRV <https://nrv-framework.org/forum>`_
   - **Full code**: `Github repository <https://github.com/nrv-framework/NRV>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   installation
   scientific
   tutorials
   usersguide
   examples
   modules
   changelog
   devcorner


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
