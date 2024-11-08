# Version updates

All notable changes to NRV are sumed up in this file.

## [1.1.3] - XXXX-XX-XX
### Added
- improved `eval` in `_FEMResults` for serialized calls (added state variables)
- `spec_loader.py` mostly for typing

### Fixed



### Removed
- `myelinated_results.find_central_node_index`-method replaced by `axon_results.find_central_index` with, for `myelinated_results`, the argument `node` to obtain former results



## [1.1.2] - 2024-09-12

### Added
- `ui`, a subpackage for user interface to separate from `utils` which are ment to stay internal.
- Help restructuration to have an API description more user-friendly.
- nrv.CONFIG as a singleton object gathering configuration related data, parameters and methods.

### Fixed
- small fix in filter_freq to avoid filtering artefact

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
- Add ``getAPspeed`` and ``get_avg_AP_speed`` methods in ``axons_results`` to measure AP propagation velocity. Should be used instead of ``speed`` (deprecated method)
- Add ``is_blocked`` method in ``axons_results`` to detect AP propagation block. Should be used instead of ``block`` (deprecated method)
- Add ``is_recruited`` method in ``axons_results`` to detect AP in an axon. 
- Add optional ``normalize`` bool parameter in ``get_recruited_axons``, ``get_recruited_axons_greater_than``, ``get_recruited_axons_lesser_than`` methods from ``fascicle_results``
- Action potential (AP) analysis methods added in ``axons_results`` (``split_APs``, ``count_APs``, ``get_start_APs``, ``detect_AP_collisions``, etc). See usage in example 18
- Several plot functions added in ``axons_results`` (``raster_plot``, ``colormap_plot`` and ``plot_x_t``)
- ``self.save_path`` from fascicle and nerve is passed to postprocessing_function/scripts if specified and used to save data from postprocessing_function/scripts.
- Fascicles and Nerve return ``nerve_results`` and ``fascicle_results`` by default (``self.return_parameters_only`` and ``self.save_results`` are false at init)
- Updated tutorials and examples with newest features, removed use of deprecated methods/functions
- Add NRV_examples.py and NRV_tutorials.py to run all examples/tutorials
- Reorganized Example folder
- reworked ``rasterize`` method of the ``axon_result`` class
- deprecated functions of ``CL_postprocessing``
- Add the ``axon_block_threshold`` function in ``CL_simulations`` to evaluate block thresholds with arbitrary stimulation settings
- deprecated ``block_threshold_point_source`` and ``block_threshold_from_axon``from ``CL_simulations`` as they are replaced by the more generalized version ``axon_block_threshold``. 
- Add the ``axon_AP_threshold`` function in ``CL_simulations`` to evaluate activation thresholds with arbitrary stimulation settings (see Example 16)
- deprecated ``firing_threshold_point_source`` and ``firing_threshold_from_axon``from ``CL_simulations`` as they are replaced by the more generalized version ``axon_AP_threshold``. 
- Added CL simulation documentation.
- Added the ``search_threshold_dispatcher`` function to parallelize the exploration to parameter effect on threshold + doc & example (see Example 17)
- Doc gallery for examples. Examples have been relocated to ``docs/examples``

### Fixed
- issues with mcore optimization
- Fix duplicate node count in node_index of myelinated axons
- ``fit_to_size`` parameter in ``fill_with_population`` is not considered if fascicle diameter is None
- ``remove_outliers`` parameter in ``fill_with_population`` is not called if fascicle diameter is None


## [1.1.0] - 2024-05-27

### Added
- Significant improvement in the documentation
- first simulations for nerve EIT direct models -> not documented yet, technical tests pass, still under scientific tests and development
- classes for results and more
- modification of post-processing architecture
- progress bar for parallel computing with process specific toolbars
- decorator for single-core function definition

### Fixed
- issues with type hints on documentation generation
- code troubles with DOLFINx v0.8.0 now resolved, versions below are not supported anymore
- most of the parameters of fascicles (and nerve) can now also be set at the instantiation. (see doc)

## [1.0.1] - 2024-01-26

### Fixed

- issue #38:
    - Now FEMSimulation results are saved in a folder ending in .bp which can also be opened in ParaView (-5.12.0 or higher).
    - DOLFINx v0.6.0 and v0.8.0 are now suported

## [1.0.0] - 2024-01-12

- Version corresponding to preprint (https://doi.org/10.1101/2024.01.15.575628)

## [0.9.16] - 2023-12-12

### Added

- Automatic versioning for dev team
- this tracking file

### Fixed
- automated releases,
- automatic push on pypi
