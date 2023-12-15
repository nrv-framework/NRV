Developer's corner
==================

NRV is a framework designed by and for the scientific corner. Behind the the open source licence, we are also more than welcome anyone that would genuinly contribute to our effort of gathering *in-silico* models for the nervous system in general.

Here are some guidelines for clean implementation of novel functionalities and contributions.

Contribution - forking and Pull-Requests
----------------------------------------

blablablabla


NRV testing
-----------

NRV is build with its own custom system for testing and validating new functionalities. This choice as made since the early developpement of first version, and is kept as so to ensure scientific reproducibility of results.

In the sources of NRV, a *test* folder is dedicated to tests: 

::
    NRV/
    ├── docker/
    ├── docs/
    ├── examples/
    ├── nrv
    ├── tests
    │   ├── unitary_tests
    │   └── bboxinout.py
