"""User Interface - ui: end user pre- or post processing code

ui provides classes and functions for pre- (meshing for instance) or
post-processing computations. Basic or recurent simulation encapuslated
as function are also accessible.

"""

from ._axon_simulations import (
    search_threshold_dispatcher,
    axon_AP_threshold,
    axon_block_threshold,
    firing_threshold_point_source,
    firing_threshold_from_axon,
    blocking_threshold_point_source,
    blocking_threshold_from_axon,
)

from ._axon_postprocessing import (
    remove_key,
    remove_non_NoR_zones,
    generate_axon_from_results,
    filter_freq,
    rasterize,
    AP_detection,
    speed,
    block,
    max_spike_position,
    count_spike,
    check_test_AP,
    detect_start_extrastim,
    extra_stim_properties,
    axon_state,
    get_index_myelinated_sequence,
    find_central_node_index,
    compute_f_mem,
    get_myelin_properties,
    plot_Nav_states,
    default_PP,
    rmv_keys,
    is_recruited,
    is_blocked,
    sample_keys,
    sample_g_mem,
    vmem_plot,
    raster_plot,
)

from ._fascicle_postprocessing import (
    ls_axons_results,
    ls_csv,
    rm_file,
    rm_sim_dir,
    rm_sim_dir_from_results,
    CAP_time_detection,
    fascicular_state,
    plot_fasc_state,
)

from ._NRV_Msh import (
    mesh_from_electrode,
    mesh_from_extracellular_context,
    mesh_from_fascicle,
    mesh_from_nerve,
)

submodules = []

classes = []

functions = [
    "search_threshold_dispatcher",
    "axon_AP_threshold",
    "axon_block_threshold",
    "firing_threshold_point_source",
    "firing_threshold_from_axon",
    "blocking_threshold_point_source",
    "blocking_threshold_from_axon",
    "remove_key",
    "remove_non_NoR_zones",
    "generate_axon_from_results",
    "filter_freq",
    "rasterize",
    "AP_detection",
    "speed",
    "block",
    "max_spike_position",
    "count_spike",
    "check_test_AP",
    "detect_start_extrastim",
    "extra_stim_properties",
    "axon_state",
    "get_index_myelinated_sequence",
    "find_central_node_index",
    "compute_f_mem",
    "get_myelin_properties",
    "plot_Nav_states",
    "default_PP",
    "rmv_keys",
    "is_recruited",
    "is_blocked",
    "sample_keys",
    "sample_g_mem",
    "vmem_plot",
    "raster_plot",
    "ls_axons_results",
    "ls_csv",
    "rm_file",
    "rm_sim_dir",
    "rm_sim_dir_from_results",
    "CAP_time_detection",
    "fascicular_state",
    "plot_fasc_state",
    "mesh_from_electrode",
    "mesh_from_extracellular_context",
    "mesh_from_fascicle",
    "mesh_from_nerve",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
