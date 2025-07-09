# Version updates

All notable changes to NRV are summed up in this file.

## [1.2.2] - 2025-07-09

### Added
- Added `utils.geom`-subpackage to gather geometry related functions and classes.
- Added elliptic and polygonal geometry for fascicles.
- Added `nmod.utils`-subpackage to gather population creation and placement methods and classes.
- Added `axon_population`-class to handle creation of population and interface with fascicle.
- Added angle untis: rad (default) and degree
- Added file: `backend._extlib_interface` to gather interfacing function with external libraries
- Added `MshCreator.add_from_cshape` to generate cylinder with custom base. 
- Fascicle are now added from their full geometry instead of only their diameter and center
- New method used to generated example and tutorial docs using [sphinxs_gallery](https://sphinx-gallery.github.io/stable/index.html).
- New directory for [NRV/examples](examples) and [NRV/tutorials](tutorials).
- New dependency: [shapely](https://shapely.readthedocs.io/en/stable/).


### Fixed
- Impose deepcopy in load_any to prevent issue when loading multiple times a same `dict`.
- Prevent to use more processes than axon number in `fascicle.simulate`.
- Various Bug with tests

### Removed
- Removed `fascicle.save_fascicle_configuration` and `fascicle.load_fascicle_configuration` Deprecated since `fascicle.save` and `fascicle.load` arrived.


### Depreciated
- arguments `Fascicle_D`, `y_c` and `z_c` from `FEM_stimulation.reshape_fascicle`, now `geometry` is used instead
- Attributes `fascicle.A`, `fascicle.y_grav_center` and `fascicle.z_grav_center`, now `fascicle.geom.area`, `fascicle.y` and `fascicle.z`
- tests `513` to `517`: axon pop related test are now with geometry tests between `350` and `400`.


## [1.2.1] - 2025-06-06

### Added
- Added `backend._NRV_Mproc` to handle parallel processing in NRV.
- Added Github Action `Build and Push Docker Image on Release` to automatically push docker image to Docker Hub on release.
- [Example o06](docs/examples/optim/o06_nerve_optimization.ipynb).
- Added Command "-f" in NRV_test to find specific tests

### Fixed
- Cleaned doc Makefile
- Fixing [Tutorial 5](docs/tutorials/5_first_optimization.ipynb).
- Cleaning and refreshing of the docs

### Removed
- Remove `backend.Mcore_handler`.
- Remove `nrv2calm`.

## [1.2.0] - 2025-05-30

### Added
- improved `eval` in `_FEMResults` for serialized calls (added state variables).
- `spec_loader.py` mostly for typing.
- progress bars are now handled with [rich.progress](https://rich.readthedocs.io/en/stable/progress.html).
- Added automatic translation of Tutorials to the docs in docs/tutorials.
- automated parallel processing using ``multiprocessing``. All parallelization are handled as a blind process for the end-user, this change has been performed with taking care for the most on backward compatibility. Documentation has been changed in consequence.

### Fixed
- ``axon.__init__``'s ``kwargs``: all parameters can now be set at the instantiation of the axon.
- Fixed ``search_threshold_dispatcher`` for use in notebooks.
- Remove deprecated function in tutorials and examples.

### Removed
- `myelinated_results.find_central_node_index`-method replaced by `axon_results.find_central_index` with, for `myelinated_results`, the argument `node` to obtain former results.
- MCore and explicit use of ``mpi4py`` are removed, as parallel processing is handled by Python standard API.


## [1.1.2] - 2024-09-12

### Added
- `ui`, a subpackage for user interface to separate from `utils` which are ment to stay internal.
- Help restructuration to have an API description more user-friendly.
- nrv.CONFIG as a singleton object gathering configuration related data, parameters and methods.

### Fixed
- small fix in filter_freq to avoid filtering artefact.

### Removed
- methods such as load_any_axon, load_any_electrode... (``load_any_`` + something) are deprecated, though not removed for backward compatibility. Please only use ``load_any`` function.


## [1.1.1] - 2024-08-05

### Added
- Updated the way axons post-processing is handled during fascicle and nerve simulation:
    - These must now be defined as functions instead of external Python scripts.
    - For backward compatibility, some built-in postprocessing functions can be called using str (see ``builtin_postproc_functions``).
    - The ``postproc_script`` attribute has been retained to set the postprocessing as either ``str`` or ``function`` regardless of the type.
    - The postproc function must at least take an ``axon_results`` as argument and return an ``axon_results``, evantual key arguments can be added to the ``postproc_kwargs`` attribute.
- Add ``block_summary`` method in ``axons_results`` which returns axon block characteristics: blocked, onset response, number of onset APs.
- Add ``getAPspeed`` and ``get_avg_AP_speed`` methods in ``axons_results`` to measure AP propagation velocity. Should be used instead of ``speed`` (deprecated method).
- Add ``is_blocked`` method in ``axons_results`` to detect AP propagation block. Should be used instead of ``block`` (deprecated method).
- Add ``is_recruited`` method in ``axons_results`` to detect AP in an axon. 
- Add optional ``normalize`` bool parameter in ``get_recruited_axons``, ``get_recruited_axons_greater_than``, ``get_recruited_axons_lesser_than`` methods from ``fascicle_results``.
- Action potential (AP) analysis methods added in ``axons_results`` (``split_APs``, ``count_APs``, ``get_start_APs``, ``detect_AP_collisions``, etc). See usage in [example 18](docs/examples/generic/18_Action_Potential_Analysis.ipynb).
- Several plot functions added in ``axons_results`` (``raster_plot``, ``colormap_plot`` and ``plot_x_t``).
- ``self.save_path`` from fascicle and nerve is passed to postprocessing_function/scripts if specified and used to save data from postprocessing_function/scripts.
- Fascicles and Nerve return ``nerve_results`` and ``fascicle_results`` by default (``self.return_parameters_only`` and ``self.save_results`` are false at init).
- Updated tutorials and examples with newest features, removed use of deprecated methods/functions.
- Add NRV_examples.py and NRV_tutorials.py to run all examples/tutorials.
- Reorganized Example folder.
- reworked ``rasterize`` method of the ``axon_result`` class.
- deprecated functions of ``CL_postprocessing``.
- Add the ``axon_block_threshold`` function in ``CL_simulations`` to evaluate block thresholds with arbitrary stimulation settings.
- deprecated ``block_threshold_point_source`` and ``block_threshold_from_axon``from ``CL_simulations`` as they are replaced by the more generalized version ``axon_block_threshold``. 
- Add the ``axon_AP_threshold`` function in ``CL_simulations`` to evaluate activation thresholds with arbitrary stimulation settings (see [Example 16](docs/examples/generic/16_activation_thresholds_arbitrary.ipynb)).
- deprecated ``firing_threshold_point_source`` and ``firing_threshold_from_axon``from ``CL_simulations`` as they are replaced by the more generalized version ``axon_AP_threshold``. 
- Added CL simulation documentation.
- Added the ``search_threshold_dispatcher`` function to parallelize the exploration to parameter effect on threshold + doc & example (see [Example 17](docs/examples/generic/17_threshold_search_dispatcher.ipynb)).
- Doc gallery for examples. Examples have been relocated to ``docs/examples``.

### Fixed
- issues with mcore optimization.
- Fix duplicate node count in node_index of myelinated axons.
- ``fit_to_size`` parameter in ``fill_with_population`` is not considered if fascicle diameter is None.
- ``remove_outliers`` parameter in ``fill_with_population`` is not called if fascicle diameter is None.


## [1.1.0] - 2024-05-27

### Added
- Significant improvement in the documentation.
- first simulations for nerve EIT direct models -> not documented yet, technical tests pass, still under scientific tests and development.
- classes for results and more.
- modification of post-processing architecture.
- progress bar for parallel computing with process specific toolbars.
- decorator for single-core function definition.

### Fixed
- issues with type hints on documentation generation.
- code troubles with DOLFINx v0.8.0 now resolved, versions below are not supported anymore.
- most of the parameters of fascicles (and nerve) can now also be set at the instantiation. (see doc).

## [1.0.1] - 2024-01-26

### Fixed

- issue #38:
    - Now FEMSimulation results are saved in a folder ending in .bp which can also be opened in ParaView (-5.12.0 or higher).
    - DOLFINx v0.6.0 and v0.8.0 are now supported.

## [1.0.0] - 2024-01-12

- Version corresponding to preprint (https://doi.org/10.1101/2024.01.15.575628).

## [0.9.16] - 2023-12-12

### Added

- Automatic versioning for dev team.
- this tracking file.

### Fixed
- automated releases,.
- automatic push on pypi.
