[![PyPI version](https://badge.fury.io/py/nrv-py.svg)](https://badge.fury.io/py/nrv-py)
[![Documentation Status](https://readthedocs.org/projects/nrv/badge/?version=latest)](https://nrv.readthedocs.io/en/master/?badge=master)
[![License: CeCill](https://img.shields.io/badge/Licence-CeCill-blue )](https://github.com/fkolbl/NRV/blob/master/Licence.txt)
<!---[![DOI](xxxx)](xxx)-->
<!---[![Build Status](xxxx)](xxx)-->

# NRV
*Python librairy for Peripheral Nervous System stimulation modeling*

NRV (or NeuRon Virtualizer) is a pythonic framework to enable fast and user friendly simulations of the Peripheral Nervous System. Axons models are simulated with the [NEURON](http://www.neuron.yale.edu/neuron) software, and extracellular fields are computed either from analytic equations such as point source approximation or with a more detailed description of the nerve and electrode geometry and Finite Elements Method, either using [COMSOL](https://www.comsol.com) (additional commercial licence requiered) or the [FENICS project](https://fenicsproject.org). All computations are performed with the quasistatic approximation of the Maxwell equations, no ephaptic coupling. Stimulation waveform can be of random shapes, and any kinds of electrode can be combined to model complex stimulation strategies.

NRV has been optimized for large population of axons, from generating correct population following a specific diameter repartition, through automatic placement to computation and post-processing of the axons activity when a stimulus is applied. Parallel computation, interface with NEURON and COMSOL and FENICS is automatically handled by NRV. For a detailed description and full help on installation, basic usage and API documentation, please visit ou [NRV readthedocs page](https://nrv.readthedocs.io/en/latest/).

NRV has been developped by contributors from the CELL research group at the Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University, until june 2023 and is now developped and maintained by the Bioelectronics group of laboratory IMS (UMR CNRS 5218), INP Bordeaux, U. Bordeaux.