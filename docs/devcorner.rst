==================
Developer's corner
==================

NRV is a framework designed by and for the scientific corner. Behind the open source license, we are also more than welcome anyone that would genuinely contribute to our effort of gathering *in-silico* models for the nervous system in general.

Here are some guidelines for clean implementation of novel functionalities and contributions.

We welcome different types of contributions:
  - **Report Bugs**: Report bugs `here:  <https://github.com/fkolbl/NRV/issues>`_. When reporting a bug, please include:
        1. Your operating system name and version.
        2. Any details about your local setup that might be helpful in troubleshooting.
        3. Detailed steps to reproduce the bug.
  - **Fix Bug**: Look through the GitHub issues for bugs. Anything tagged with “bug” and “help wanted” is open to whoever wants to implement it.
  - **Implement Feature**: Look through the GitHub issues for features. Anything tagged with “enhancement” and “help wanted” is open to whoever wants to implement it. Those that are tagged with “first-timers-only” is suitable for those getting started in open-source software.


Contribution - forking and Pull-Requests
========================================

Here is how to setup NRV for local development:

1. Fork the NRV repo on GitHub. Official developers are limited to members of the `Bioelectronics group at the laboratory IMS <https://www.ims-bordeaux.fr/research-groups/bioelectronics/>`_

2. Clone your fork locally:
::

    $ git clone git@github.com:your_name_here/NRV.git

3. We recommend using a conda environment, to ease the installation of FenicsX. However, a virtualenv should be possible. Assuming you are using a conda environment this is how you set up you development configuration:
::

    $ conda activate nrv-env
    $ cd NRV
    $ source bash_nrv

4. Create a branch for local development:
::

    $ git checkout -b name-of-your-contribution

You should be able to make changes locally

5. Once changes are made, you should use the test interface (see bellow for details) to lint and test you code:
::

    $ cd tests
    $ ./NRV_test --syntax
    $ ./NRV_test --all

If you add a new functionality, you should add one or several tests, showing that your method works. The test should not raise any exception and should verify known, recognized or easily understable values to demonstrate the scientific reasoning. If it refers to a scientific publication, the citation should be included in the test file as python comment.

6. Please do not forget to update the documentation if your changes imply knowledge from the end user. To be able to compile the documentation, few dependancies have to be considered:
::

    $ pip install sphinx sphinx-rtd-theme furo Pygments sphinx-mdinclude

Once installed, you should be able to build the documentation with the following command:
::

    python3 -m sphinx.cmd.build -b html docs/ docs/_build/

.. tip::
    To document new features, example should be added as `.rst <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_ file in the folder ``NRV.docs.examples``. It can be more convenient to write the example in a *jupiter notebook* to check the code and then convert it in using `nbconvert <https://nbconvert.readthedocs.io/en/latest/>`_ and this command line:
        ::

            jupyter nbconvert --to rst your_fname.ipynb

7. Commit your changes and push you branch to GitHub:
::

    $ git add -A
    $ git commit -m "Your message containing a description of contribution and changes"
    $ git push origin name-of-your-contribution

In brief, commit messages should follow these conventions:
    - Always contain a subject line which briefly describes the changes made. For example “Update CONTRIBUTING.rst”.
    - Subject lines should not exceed 50 characters.
    - The commit body should contain context about the change - how the code worked before, how it works now and why you decided to solve the issue in the way you did.

8. Submit a pull request through the GitHub website.

NRV testing
===========

NRV is build with its own custom system for testing and validating new functionalities. This choice as made since the early development of first version, and is kept as so to ensure scientific reproducibility of results.

In the sources of NRV, a *test* folder is dedicated to tests: 

::

    NRV/
    ├── docker/
    ├── docs/
    ├── examples/
    ├── nrv/
    ├── tests/
    │   ├── unitary_tests/
    │   └── NRV_test

The *NRV_test* file is a script that act as a test launcher. It should be called from the command line using:

::

    ./NRV_test

This script can test the installation and dependencies, test the syntax and trigger linters or launch unitary tests. The following options are possible:
  - "-d", "--dependances": Check NEURON and COMSOL installation
  - "-l", "--list": Print the name of all unitary tests, an optional integerr can be added to arguments to specify the number of columns used to print
  - "-u", "--unitary_tests": Launch all unitary tests, test result figures are saved in './unitary_test/figures' folder, all the tests should be True, numerical values for debug only
  - "-s", "--syntax": Lint nrv syntax source code
  - "-a", "--all": launches even potentially failing tests due to third party softwares such as COMSOL
  - "-t", "--target": ID of the tests to simulate, if a digit is replaced by '_' all the tests
  - "-F", "--fenics": Launch all and only FEniCS related tests
  - "-C", "--comsol": Launch all and only COMSOL related tests
  - "-p", "--python": Forces Python as interpreted instead of *nrv2calm*

Note that running all scripts without errors and with all prints set to 'True' (no 'False') is a necessary condition for a PR to be accepted.
If errors occurred, the list of failed tests will be saved in the file *tests/unitary_tests/log_NRV_test.txt*.

All code sources for the unitary tests can be found in the *tests/unitary_tests/* folder. Tests are organized in groups and subgroups as follows:

.. list-table:: Tests functionalities
    :widths: 10 10 50
    :header-rows: 1
    :align: center

    *   - Starting Number
        - Ending Number
        - Function tested
    *   - 001
        - 001
        - General architecture
    *   - 002
        - 041
        - Basic functionalities: axon models simulation intracellular contextual and analytical extracellular context
    *   - 050
        - 059
        - Fascicular related functions and basic multiprocessing functionalities
    *   - 060
        - 065
        - COMSOL FEM model
    *   - 066
        - 071
        - Various
    *   - 072
        - 079
        - Save and load functionalities: electrode footprints, axon, fascicle
    *   - 080
        - 083
        - Analytical recorders
    *   - 084
        - 087
        - Save and load contexts and recorders
    *   - 088
        - 089
        - Various functions
    *   - 090
        - 099
        - Conductivity recorders
    *   - 100
        - 145
        - FEniCS FEM models and GMSH meshes creator functions
    *   - 150
        - 151
        - Compare FEniCS and COMSOL FEM models
    *   - 200
        - 225
        - Optimization functions
    *   - 250
        - 275
        - Wrappers and decorators
    *   - 300
        - 306
        - Nerve functions
    *   - 500
        - 509
        - Various functions


Public roadmap
==============
NRV is developed for the research and education community. We hope to provide a tool for biomedical engineering, and provide a framework that is as open as possible, to ensure scientific communication and reproducibility.

NRV is certainly not perfect, and we hope that the open-science approach can contribute to improve the framework, however ensuring retrocompatilibty. There is a continuous effort from the Bioelectronics group of the IMS Laboratory (U. Bordeaux, Bordeaux INP, CNRS UMR 5218) to continue to develop NRV, and some purely scientific objectives are linked to this project. Here is a list of non-scientific and mostly technical objectives, that we intend to develop and on which we are also extremely happy to get help or guiding if you want to contribute:

- **Improving geometry:**
    - enable axon tortuosity for axons,
    - enable elliptical shapes for fascicles and nerves (with automatized population filling and basic operations as already developed for round shapes fascicles/nerves).
    - integrate mode complex shapes based on histology and image segmentation (with automatized population filling).
    - extend FenicsX computation with curvilinear coordinates, to enable non-extruded 3D models of fascicles
    - add electrode daughter-classes for more specific electrode geometries.

- **Improving recordings:** current recording simulation is based on analytical field computation, thus restricting to one material between fibers and recording points. Such computations have already been performed with FEM and should be integrated in NRV

- **Objects for fiber-populations:** generation and packing are based on functions, we hope to change to objects to ease the way of script ex-novo population production

- **Post-processing options:**
    - provide automatic link between FEM computation results and *Paraview*
    - provide basic integration of *Pyvista* and *Matplotlib* to ease results exploration
    - design wrapper and decorators with simulations to ease systematic tasks in results post-processing

- **Compatibility and marking of results:** provide automated tagging of objects with version and develop routines for versions checking.

- **Parallel computing**
    - migrate to *multiprocessing* (Python core library)
    - parallel version of axon population generation and axon packing
    - design further decorators to clean scripting and make syntax more pythonic