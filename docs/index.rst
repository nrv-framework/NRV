.. NeuRon Virtualizer (NRV) documentation master file, created by
   sphinx-quickstart on Sun Jul 23 14:36:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NeuRon Virtualizer (NRV)'s documentation!
====================================================


NRV (NeuRon Virtualizer) is a Python-based framework designed to enable fast and user-friendly simulations of the Peripheral Nervous System. Axon models are simulated using the NEURON software, and extracellular fields are computed either from analytical equations (e.g., point source approximation) or through a more detailed description of the nerve and electrode geometry using the Finite Element Method (FEM). FEM simulations can be performed using either COMSOL (a commercial license is required) or the open-source FEniCS project.

All computations are performed under the quasistatic approximation of Maxwell’s equations, and ephaptic coupling is not considered. Stimulation waveforms can have arbitrary shapes, and any combination of electrodes can be used to model complex stimulation strategies.

NRV is optimized for simulations involving large axon populations—from generating realistic axon populations based on specific diameter distributions, to automated spatial placement, computation, and post-processing of axonal responses to stimulation. Parallel computation and interfaces with NEURON, COMSOL, and FEniCS are seamlessly managed by NRV.

NRV was initially developed by contributors from the CELL research group at ETIS Laboratory (UMR CNRS 8051), ENSEA – CY Cergy Paris University, until June 2023. It is now maintained and further developed by the Bioelectronics group at IMS Laboratory (UMR CNRS 5218), INP Bordeaux, University of Bordeaux.

If you use **NRV** in your research, please cite the following paper:

Couppey, T., Regnacq, L., Giraud, R., Romain, O., Bornat, Y., & Kolbl, F. (2024). *NRV: An open framework for in silico evaluation of peripheral nerve electrical stimulation strategies*. PLOS Computational Biology, 20(7), e1011826.  
`https://doi.org/10.1371/journal.pcbi.1011826 <https://doi.org/10.1371/journal.pcbi.1011826>`_

BibTeX
------

.. code-block:: bibtex

    @article{couppey2024nrv,
      title={NRV: An open framework for in silico evaluation of peripheral nerve electrical stimulation strategies},
      author={Couppey, Thomas and Regnacq, Louis and Giraud, Roland and Romain, Olivier and Bornat, Yannick and Kolbl, Florian},
      journal={PLOS Computational Biology},
      volume={20},
      number={7},
      pages={e1011826},
      year={2024},
      publisher={Public Library of Science San Francisco, CA USA}
    }

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
