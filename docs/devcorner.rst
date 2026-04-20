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

1. Fork the NRV repo on GitHub. If you want to be part of the NRV team contact us on `the forum NRV <https://nrv-framework.org/forum>`_ or `Github <https://github.com/nrv-framework/NRV>`_

2. Clone your fork locally:

.. code:: bash

    git clone git@github.com:your_name_here/NRV.git

3. We recommend using a conda environment, to ease the installation of FenicsX. However, a virtualenv should be possible. Assuming you are using a conda environment this is how you set up you development configuration:

.. code:: bash

    conda activate nrv-env
    cd NRV
    source bash_nrv

4. Create a branch for local development:

.. code:: bash

    git checkout -b name-of-your-contribution

You should be able to make changes locally

5. Once changes are made, you should use the test interface (see bellow for details) to lint and test your code.

The historical scientific test launcher remains available:

.. code:: bash

    cd tests
    ./NRV_test --syntax
    ./NRV_test --all

In parallel, the automation-friendly pytest suite can be used from the repository root:

.. code:: bash

    pytest test
    pytest tests/unit
    pytest tests/e2e
    pytest tests/deployment

If you add a new functionality, you should add one or several tests, showing that your method works. The test should not raise any exception and should verify known, recognized or easily understable values to demonstrate the scientific reasoning. If it refers to a scientific publication, the citation should be included in the test file as python comment.

6. Please do not forget to update the documentation if your changes imply knowledge from the end user. The requirements for documentation compilation are listed in the `following section <devcorner.html#nrv-documentation>`_.

7. Commit your changes and push your branch to GitHub:

.. code:: bash

    git add -A
    git commit -m "Your message containing a description of contribution and changes"
    git push origin name-of-your-contribution

In brief, commit messages should follow these conventions:
    - Always contain a subject line which briefly describes the changes made. For example “Update CONTRIBUTING.rst”.
    - Subject lines should not exceed 50 characters.
    - The commit body should contain context about the change - how the code worked before, how it works now and why you decided to solve the issue in the way you did.

8. Submit a pull request through the GitHub website.


NRV documentation
=================

.. important::

    To ensure the usability of NRV, it is important to make sure that all changes made to the source code are documented before any merge.


NRV documentation is built using `Sphinx <https://www.sphinx-doc.org/fr/master/>`_. For consistent documentation, three main parts must be updated:
    1. **Generic explanations**: `.rst` files gathered in ``NRV/docs``.
    2. **Tutorials and Examples**: `.py` files stored in ``NRV/tutorials`` and ``NRV/examples``. *Generated with* `sphinx_gallery <https://sphinx-gallery.github.io/stable/index.html>`_
    3. **API documentation**: Docstrings in all source files, classes, and functions. *Generated with* `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_


To compile the full documentation (1, 2, and 3), use a conda/mamba environment where you can `import nrv`.

.. seealso::
    Two method can be used to install such environment:
       - :doc:`Standard installation <./installation>`.
       - `Developer installation <devcorner.html#contribution-forking-and-pull-requests>`_.

Additionally, a few dependencies must be installed:

.. code:: bash

    pip install sphinx sphinx-rtd-theme furo Pygments sphinx-mdinclude sphinx_copybutton sphinx_gallery sphinx_codeautolink


Once installed, you can build the documentation with the following command from the base repository ``NRV/``:

.. code:: bash

    python3 -m sphinx.cmd.build -b html docs/ docs/_build/

.. warning::

    Building the full documentation can take a long time, mainly due to `2. Tutorials and Examples` and `3. API documentation`.

If you want to rebuild the full documentation, you should first manually remove the generated files. This can be done by deleting the folders ``NRV/docs/_build/``, ``NRV/docs/_nrv/``, ``NRV/docs/exemple/``, and ``NRV/docs/tutorial/``.

.. tip::

    You can considerably speed up documentation generation by only rebuilding the required parts.
        - To skip rebuilding `2. Tutorials and Examples`, keep the folders ``NRV/docs/exemple/`` and ``NRV/docs/tutorial/``.
        - To skip rebuilding `3. API documentation`, keep the folder ``NRV/docs/_nrv/``.

.. note::
    ``NRV/docs/exemple/`` and ``NRV/docs/tutorial/`` are included by default in the git repository. If you want to rebuild `2. Tutorials and Examples`, you need to manually remove these folders before compiling.

    If your change does not involve tutorials or examples, you do not need to be in an environment able to `import nrv`. You only need the pip-installable dependencies listed in `NRV/docs/requirements.txt <https://github.com/nrv-framework/NRV/blob/master/docs/requirements.txt>`_:

    .. code:: bash

        pip install sphinx sphinx_rtd_theme furo Pygments sphinx_mdinclude sphinx_copybutton sphinx_gallery ipython sphinx_codeautolink numpy matplotlib


NRV testing
===========

NRV currently relies on two complementary testing systems.
In the sources of NRV, both testing folders are present:

.. code:: bash

    NRV/
    ├── docker/
    ├── docs/
    ├── examples/
    ├── nrv/
    ├── tests/
    │   ├── deployment/
    │   ├── e2e/
    │   ├── unit/
    │   ├── unitary_tests/
    │   └── NRV_test

Scientific testing
------------------

NRV is build with its own custom system for testing and validating new functionalities. This choice was made during the early development of the framework and is kept to ensure scientific reproducibility of results.

The ``tests/NRV_test`` file is a script that acts as a test launcher. It should be called from the command line using:

.. code:: bash

    cd tests
    ./NRV_test

This script can test the installation and dependencies, test the syntax and trigger linters or launch unitary tests. The following options are possible:
  - "-d", "--dependances": Check NEURON and COMSOL installation
  - "-l", "--list": Print the name of all unitary tests, an optional integer can be added to arguments to specify the number of columns used to print
  - "-f", "--find": Select only tests containing one or multiple substrings
  - "-u", "--unitary_tests": Launch all unitary tests, test result figures are saved in './unitary_test/figures' folder, all the tests should be True, numerical values for debug only
  - "-s", "--syntax": Lint nrv syntax source code
  - "-a", "--all": launches even potentially failing tests due to third party softwares such as COMSOL
  - "-t", "--target": ID of the tests to simulate, if a digit is replaced by '_' all the tests
  - "-F", "--fenics": Launch all and only FEniCS related tests
  - "-C", "--comsol": Launch all and only COMSOL related tests

Note that running all scripts without errors and with all prints set to 'True' (no 'False') is a necessary condition for a PR to be accepted.
If errors occurred, the list of failed tests will be saved in the file *tests/unitary_tests/log_NRV_test.txt*.

All code sources for the unitary tests can be found in the ``tests/unitary_tests/`` folder. Additional development scripts are stored in ``tests/dev_tests/`` and deprecated scripts are kept in ``tests/deprecated_tests/``. Tests are organized in groups and subgroups as follows:

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
        - 349
        - Nerve functions
    *   - 350
        - 399
        - Geometries and axon population
    *   - 500
        - 550
        - Various functions
    *   - 900
        - 950
        - Machine and autoconfig

Pytest testing for CI/CD
------------------------

In parallel with the scientific validation suite, NRV now includes a pytest-based structure in ``test/``.
This second suite is intended for automation and continuous integration. Its role is to check that representative workflows run without error and produce results, while keeping the computational cost moderate enough for repeated execution.

The pytest suite is organized into three families:

  - ``unit``: short API-focused tests, object construction checks, save/load smoke tests, and lightweight helper validation
  - ``e2e``: strategic end-to-end workflows such as axon, fascicle, nerve, stimulation, threshold, FEniCS, and EIT smoke simulations
  - ``deployment``: runtime, import, backend, and multiprocessing sanity checks

This suite intentionally excludes COMSOL and focuses on NEURON- and FEniCS-compatible workflows.

Typical commands are:

.. code:: bash

    pytest tests/unit
    pytest tests/e2e
    pytest tests/deployment

Tests can also be selected with markers:

.. code:: bash

    pytest -m unit
    pytest -m e2e
    pytest -m deployment
    pytest -m fenics
    pytest -m "not slow"

The pytest markers are registered in ``tests/conftest.py``. This makes it possible to select one family of tests in isolation, which is especially useful for future CI/CD workflows and local debugging.

CI/CD delivery pipeline
=======================

The NRV repository now uses a branch-driven delivery model designed to keep day-to-day development simple while making releases repeatable and auditable.

The target flow is the following:

.. code:: text

    feature branch
         |
         v
        dev  --PR-->  staging  --auto promotion PR-->  master
                                     |
                                     v
                           TestPyPI + deployment test

The three long-lived branches have distinct roles:

- ``dev``: integration branch used by developers and feature pull requests
- ``staging``: release-candidate branch used to validate a build before public publication
- ``master``: publication branch used only for official releases and deployment artefacts

This organization reflects the intended process previously summarized in the internal workflow diagrams:

- on ``dev``: version bump, linting, and routine development validation
- on ``staging``: unit tests, end-to-end tests, TestPyPI publication, and deployment validation
- on ``master``: PyPI publication, documentation publication, Docker image build, and GitHub release creation

Workflow architecture
---------------------

The pipeline is split into two categories of GitHub Actions workflows.

Reusable step workflows
^^^^^^^^^^^^^^^^^^^^^^^

Reusable workflows perform one technical operation and are called through ``workflow_call``. They are meant to stay small and focused.

Current reusable steps are:

- ``step_linter.yml``
- ``step_bump_version.yml``
- ``step_pytest-unit.yml``
- ``step_pytest-e2e.yml``
- ``step_testpypi_release.yml``
- ``step_pytest-deployment.yml``
- ``step_pypi_release.yml``
- ``step_prebuild_docs.yml``
- ``step_publish_staging_docs.yml``
- ``step_docker-image.yml``
- ``step_create_release.yml``

Branch orchestration workflows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Coordination workflows are the only workflows directly triggered by GitHub events at branch level. They call the reusable steps in the correct order.

The coordination workflows are:

- ``coordination_dev.yml``
- ``coordination_staging.yml``
- ``coordination_master.yml``

This split has two benefits:

- the delivery logic stays readable
- each technical step can be reused or tested independently

Pipeline behavior by branch
---------------------------

``dev``
^^^^^^^

The ``dev`` branch is the integration branch for everyday development.

Expected usage:

1. each developer works on a short-lived feature branch
2. a pull request is opened toward ``dev``
3. the ``coordination_dev`` workflow runs
4. linting and unit tests must pass before merge

A manual version bump can also be triggered on ``dev`` through ``workflow_dispatch`` when the team decides that the next integration cycle should target a new semantic version.

Typical checks on ``dev``:

- black formatting check
- pytest unit suite
- optional manual semantic version bump

``staging``
^^^^^^^^^^^

The ``staging`` branch is the release-candidate qualification branch.

Expected usage:

1. once the team considers ``dev`` ready, open a PR from ``dev`` to ``staging``
2. the PR to ``staging`` runs the qualification checks
3. after merge to ``staging``, the full release-candidate pipeline is triggered automatically

The post-merge pipeline on ``staging`` is:

1. run the pytest unit suite
2. run the pytest e2e suite
3. build and publish the package to TestPyPI
4. install that candidate package from TestPyPI
5. run deployment tests against the published candidate
6. create or update a promotion PR from ``staging`` to ``master``
7. enable auto-merge on that promotion PR if repository policy allows it

This branch is intentionally protected but still allows intervention from a core maintainer if the pipeline stops after publication to TestPyPI and a fix is needed.

``master``
^^^^^^^^^^

The ``master`` branch is the publication branch. Humans should not work there directly.

Expected usage:

1. ``staging`` is promoted into ``master``
2. the ``coordination_master`` workflow computes the release tag from ``pyproject.toml``
3. the release tag is created if missing
4. the package is published to PyPI
5. the documentation for ``latest`` is rebuilt and published
6. a GitHub release is created
7. the Read the Docs ``staging`` and tagged versions are activated and built
8. Docker images are built and pushed

This means that all public artefacts originate from the same validated code state.

How to use the pipeline as a developer
--------------------------------------

For most contributors, the expected process is straightforward:

1. create a branch from ``dev``
2. implement the change
3. add or update tests in ``tests/e2e``, ``tests/unit`` and, when relevant, in ``tests/science``
4. update the documentation
5. open a PR to ``dev``
6. fix lint or unit failures if the workflow reports any problem

Only release managers or core maintainers usually need to interact with ``staging`` and ``master``.

For a release cycle, the team should:

1. decide that ``dev`` is ready
2. open a PR from ``dev`` to ``staging``
3. let the ``staging`` pipeline publish and validate the candidate
4. review the automatically created promotion PR to ``master``
5. allow the publication pipeline to complete

Local reproduction of CI steps
------------------------------

The CI workflows mirror commands that can also be run locally.

Linting:

.. code:: bash

    black --check --verbose ./nrv

Unit tests:

.. code:: bash

    pytest test/unit -q

End-to-end tests:

.. code:: bash

    pytest test/e2e -q

Deployment tests:

.. code:: bash

    pytest test/deployment -q

Documentation build:

.. code:: bash

    python -m sphinx.cmd.build -b html docs/ docs/html/

A release manager may also inspect the package locally before publication:

.. code:: bash

    python -m pip install --upgrade build
    python -m build

Rulesets and protections
------------------------

The repository should define GitHub rulesets consistent with the branch model.

Recommended protections are:

- ``dev``:
    - pull request required
    - at least one approval
    - required checks: ``lint`` and ``unit``
    - no force push
    - no direct human push

- ``staging``:
    - pull request required
    - one or two approvals depending on team policy
    - required checks on PR: ``unit`` and ``e2e``
    - restricted direct push for release managers only
    - no force push
    - no branch deletion

- ``master``:
    - pull request required
    - no direct human push
    - linear history
    - no force push
    - release and deployment only

- tags ``v*``:
    - protected creation
    - no deletion
    - no retagging

Secrets, environments, and runners
----------------------------------

The pipeline depends on a small set of external credentials:

- ``TEST_PYPI_API_TOKEN``
- ``PYPI_API_TOKEN``
- ``RTD_TOKEN``
- ``DOCKER_USERNAME``
- ``DOCKER_PASSWORD``

Recommended GitHub environments are:

- ``testpypi``
- ``pypi``
- ``dockerhub``

The e2e and documentation steps rely on a self-hosted runner because they are heavier and depend on the NRV scientific stack.

That runner must remain healthy, updated, and able to provision the conda environments used by the workflows.

Operational notes
-----------------

A few practical points are important for maintainers:

- ``staging`` must exist as a long-lived branch before enabling the pipeline
- all ``step_*`` workflows are reusable and should remain event-agnostic
- branch logic belongs in ``coordination_*`` workflows only
- the package version in ``pyproject.toml`` is the source of truth for release tags
- a failed promotion from ``staging`` to ``master`` should be fixed on ``staging`` and rerun, not patched on ``master``

This architecture is intentionally conservative: it favors reproducibility, explicit promotion steps, and clean traceability of release artefacts.


Make a release
==============

The release process is now branch-driven and largely automated.

For maintainers, the practical sequence is:

1. Make sure ``dev`` contains the intended changes.
2. Trigger a version bump on ``dev`` if a new semantic version is required.
3. Open and merge a PR from ``dev`` to ``staging``.
4. Let the ``staging`` pipeline qualify the candidate through unit tests, e2e tests, TestPyPI publication, and deployment checks.
5. Review the automatically created promotion PR from ``staging`` to ``master``.
6. Let the ``master`` pipeline publish the final artefacts.

The public artefacts generated from ``master`` are:

- a release tag ``vX.Y.Z``
- a package on PyPI
- a GitHub release
- updated Read the Docs versions
- Docker images tagged with ``latest`` and ``vX.Y.Z``


Public roadmap
==============

NRV is developed for the research and education community. We hope to provide a tool for biomedical engineering, and provide a framework that is as open as possible, to ensure scientific communication and reproducibility.

NRV is certainly not perfect, and we hope that the open-science approach can contribute to improve the framework, however ensuring retrocompatilibty. There is a continuous effort from the Bioelectronics group of the IMS Laboratory (U. Bordeaux, Bordeaux INP, CNRS UMR 5218) to continue to develop NRV, and some purely scientific objectives are linked to this project. Here is a list of non-scientific and mostly technical objectives, that we intend to develop and on which we are also extremely happy to get help or guiding if you want to contribute:

- **Improving geometry:**
    - Enable axon tortuosity for axons.
    - Enable elliptical shapes for fascicles and nerves (with automatized population filling and basic operations as already developed for round shapes fascicles/nerves).
    - Integrate mode complex shapes based on histology and image segmentation (with automatized population filling).
    - Extend FenicsX computation with curvilinear coordinates, to enable non-extruded 3D models of fascicles.
    - Add electrode daughter-classes for more specific electrode geometries.

- **Improving recordings:** current recording simulation is based on analytical field computation, thus restricting to one material between fibers and recording points. Such computations have already been performed with FEM and should be integrated in NRV

- **Objects for fiber-populations:** generation and packing are based on functions, we hope to change to objects to ease the way of script ex-novo population production

- **Post-processing options:**
    - provide automatic link between FEM computation results and *Paraview*
    - provide basic integration of *Pyvista* and *Matplotlib* to ease results exploration
    - design wrapper and decorators with simulations to ease systematic tasks in results post-processing

- **Compatibility and marking of results:** provide automated tagging of objects with version and develop routines for versions checking.
