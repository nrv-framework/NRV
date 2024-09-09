""" backend: code for IO, machine and classes handling

the backend sub-package is dedicated to handling the magic behind all NRV
computations. The code developed here is not meant to be used directly by the
end-user, but internally to develop new functionality or maintain other
sub-packages.

"""

from ._config import nrv_config
from ._file_handler import (
    is_iterable,
    rmv_ext,
    generate_new_fname,
    create_folder,
    check_json_fname,
    json_dump,
    json_load,
    load_dxf_file,
    NRV_Encoder,
)
from ._inouts import (
    set_attributes,
    check_function_kwargs,
    function_to_str,
    str_to_function,
)
from ._log_interface import (
    init_reporter,
    set_log_level,
    rise_error,
    rise_warning,
    pass_info,
    pass_debug_info,
    progression_popup,
    prompt_debug,
    clear_prompt_line,
    bcolors,
    pbar,
)
from ._MCore import synchronize_processes, Mcore_handler
from ._NRV_Class import (
    is_NRV_class,
    is_NRV_class_list,
    is_NRV_class_dict,
    is_NRV_dict,
    is_NRV_dict_list,
    is_NRV_dict_dict,
    is_NRV_object_dict,
    is_empty_iterable,
    load_any,
    NRV_class,
)
from ._NRV_Results import generate_results, NRV_results, sim_results
from ._NRV_Simulable import is_NRV_simulable, simulable, NRV_simulable
from ._NRV_Singleton import NRV_singleton
from ._parameters import nrv_parameters
from ._wrappers import singlecore

submodules = []

classes = [
    "nrv_config",
    "NRV_Encoder",
    "bcolors",
    "pbar",
    "Mcore_handler",
    "NRV_class",
    "NRV_results",
    "sim_results",
    "NRV_simulable",
    "NRV_singleton",
    "nrv_parameters",
]

functions = [
    "NeuronCompile",
    "is_iterable",
    "rmv_ext",
    "generate_new_fname",
    "create_folder",
    "check_json_fname",
    "json_dump",
    "json_load",
    "load_dxf_file",
    "set_attributes",
    "check_function_kwargs",
    "function_to_str",
    "str_to_function",
    "init_reporter",
    "set_log_level",
    "rise_error",
    "rise_warning",
    "pass_info",
    "pass_debug_info",
    "progression_popup",
    "prompt_debug",
    "clear_prompt_line",
    "synchronize_processes",
    "is_NRV_class",
    "is_NRV_class_list",
    "is_NRV_class_dict",
    "is_NRV_dict",
    "is_NRV_dict_list",
    "is_NRV_dict_dict",
    "is_NRV_object_dict",
    "is_empty_iterable",
    "load_any",
    "generate_results",
    "is_NRV_simulable",
    "simulable",
    "singlecore",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
