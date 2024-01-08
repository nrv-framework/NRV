==================
Developer's corner
==================

NRV is a framework designed by and for the scientific corner. Behind the the open source licence, we are also more than welcome anyone that would genuinly contribute to our effort of gathering *in-silico* models for the nervous system in general.

Here are some guidelines for clean implementation of novel functionalities and contributions.

We welcome different types of contributions:

  - **Report Bugs**: Report bugs `here:  <https://github.com/fkolbl/NRV/issues>`_. When reporting a bug, please include:

        1. Your operating system name and version.
        
        2. Any details about your local setup that might be helpful in troubleshooting.

        3. Detailed steps to reproduce the bug.

  - **Fix Bug**: Look through the GitHub issues for bugs. Anything tagged with “bug” and “help wanted” is open to whoever wants to implement it.
  - **Implement Feature**: Look through the GitHub issues for features. Anything tagged with “enhancement” and “help wanted” is open to whoever wants to implement it. Those that are tagged with “first-timers-only” is suitable for those getting started in open-source software.


Contribution - forking and Pull-Requests
----------------------------------------

Here is how to setup NRV for local development:

1. Fork the NRV repo on GitHub. Official developers are limited to members of the `Bioelectronics group at the laboratory IMS <https://www.ims-bordeaux.fr/research-groups/bioelectronics/>`_

2. Clone your fork locally:
::

    $ git clone git@github.com:your_name_here/NRV.git

3. We recommend to use a conda environnement, to ease the installation of FenicsX. However, a virtualenv should be possible. Assuming you are using a conda environnemnet this is how you set up you development configuration:
::

    $ conda activate nrv-env
    $ cd NRV
    $ source bash_nrv

4. Create a branc for local development:
::

    $ git checkout -b name-of-your-contribution

You should be able to make changes locally

5. Once changes are made, you should use the test interface (see bellow for details) to lint and test you code:
::

    $ cd tests
    $ ./NRV_test --syntax
    $ ./NRV_test --all

If you add a new functionality, you should add one or several tests, showing that your method works. The test should not raise any exception and should verify known, recognized or easely understable values to proove the scientific reasoning. If it refers to a scientific publication, the citation should be included in the test file as python comment.

6. Commit your changes and push you branch to GitHub:
::

    $ git add -A
    $ git commit -m "Your message containing a description of contribution and changes"
    $ git push origin name-of-your-contribution

In brief, commit messages should follow these conventions:
    - Always contain a subject line which briefly describes the changes made. For example “Update CONTRIBUTING.rst”.
    - Subject lines should not exceed 50 characters.
    - The commit body should contain context about the change - how the code worked before, how it works now and why you decided to solve the issue in the way you did.

7. Submit a pull request through the GitHub website.

NRV testing
-----------

NRV is build with its own custom system for testing and validating new functionalities. This choice as made since the early developpement of first version, and is kept as so to ensure scientific reproducibility of results.

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

This script can test the install and dependencies, test he syntax and trigger linters or launch unitary tests. The following options are possitle:
  - "-d", "--dependances": Check NEURON and COMSOL installation
  - "-l", "--list": Print the name of all unitary tests
  - "-u", "--unitary_tests": Launch all unitary tests, test result figures are saved in './unitary_test/figures' folder, all thest should be True, numerical values for debug only
  - "-s", "--syntax": Lint nvr syntax source code
  - "-a", "--all": launches even potentially failing tests due to third party softwares such as COMSOL
  - "-t", "--target": ID of the tests to simulate, if a digit is replaced by '_' all the tests
  - "-F", "--fenics": Launch all and only FEniCS related tests
  - "-C", "--comsol": Launch all and only COMSOL related tests
  - "-p", "--python": Forces Python as interpreted instead of *nrv2calm*

Note that runing all scripts without errors and with all prints set to 'True' (no 'False') is a neccessary condition for a PR to be accepted.

All code sources for the unitary tests can be found in the *tests/unitary_tests/* folder. Tests are organized in groups and subgroups as follows:

+------------------------+-----------------+-----------------------------+
| Starting Number        | Ending Number   | Function tested             |
+========================+=================+=============================+
| body row 1, column 1   | column 2        |                    column 3 |
+------------------------+-----------------+-----------------------------+
| body row 2             |                 |                             |
+------------------------+-----------------+-----------------------------+
