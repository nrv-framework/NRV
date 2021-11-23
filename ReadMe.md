# NRV
*Python librairy for Peripheral Nervous System stimulation modeling*

NRV is a Python module for simple description of electrical stimulation of the peripheral neural system modeling. Axons models are simulated with the [NEURON](http://www.neuron.yale.edu/neuron) software, and extracellular fields are computed either from analytic equations such as point source approximation or with a more detailed description of the nerve and electrode geometry and Finite Elements Method using [COMSOL](https://www.comsol.com). All computations are performed with the quasistatic approximation of the Maxwell equations, no ephaptic coupling. Stimulation waveform can be of random shapes, and any kinds of electrode can be combined to model complex stimulation strategies.

NRV has been optimized for large population of axons, from generating correct population following a specific diameter repartition, through automatic placement to computation and post-processing of the axons activity when a stimulus is applied. Parallel computation, interface with NEURON and COMSOL is automatically handled by NRV.

NRV is developped in the CELL research group at the Laboratory ETIS (UMR CNRS 8051), ENSEA - CY Cergy Paris University.

# Requirements

Third party softwares (NEURON and COMSOL) have to be installed before NRV installation. NRV has been developped for python 3. Recommended packages:
- numpy, scipy and matplotlib
- mpi4py
- numba
- mph
- ezdxf

for the third party softwares, please visit:
[NEURON]: http://www.neuron.yale.edu/neuron
[COMSOL]: https://www.comsol.com

# Todo
Update CL_simulation with nseg parameter everywhere
