# Version updates

All notable changes to NRV are sumed up in this file.

## [1.1.1] - XXXX
### Added
- reworked ``rasterize`` method of the ``axon_result`` class
- deprecated functions of ``CL_postprocessing``
- Add the ``axon_AP_threshold`` function in ``CL_simulations`` to evaluate activation thresholds with arbitrary stimulation settings (see Example 16)
- deprecated ``firing_threshold_point_source`` and ``firing_threshold_from_axon``from ``CL_simulations`` as they are replaced by the more generalized version ``axon_AP_threshold``. 
- Added CL simulation documentation.

### Fixed
- issues with mcore optimization

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
