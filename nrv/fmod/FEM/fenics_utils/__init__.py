"""NeuRon Virtualizer, large scale modeling of Peripheral Nervous System with random stimulation waveforms"""

""" FMOD-FEM-FENICS_UTILS librairy"""

from ._f_materials import (
    f_material,
    is_f_mat,
    mat_from_interp,
    mat_from_csv,
    load_f_material,
)

from ._FEMParameters import (
    is_sim_param,
    FEMParameters,
)

from ._FEMResults import (
    is_sim_res,
    save_sim_res_list,
    read_gmsh,
    domain_from_meshfile,
    V_from_meshfile,
    closest_point_in_mesh,
    FEMResults,
)

from ._FEMSimulation import FEMSimulation

from ._fenics_materials import fenics_material

from ._layered_materials import (
    is_lay_mat,
    get_sig_ap,
    layered_material,
)

submodules = []

classes = [
    "f_material",
    "FEMParameters",
    "FEMResults",
    "FEMSimulation",
    "fenics_material",
    "layered_material",
]

functions = [
    "is_f_mat",
    "mat_from_interp",
    "mat_from_csv",
    "load_f_material",
    "is_sim_res",
    "save_sim_res_list",
    "read_gmsh",
    "domain_from_meshfile",
    "V_from_meshfile",
    "closest_point_in_mesh",
    "is_lay_mat",
    "get_sig_ap",
]

__all__ = []

__all__ += submodules
__all__ += classes
__all__ += functions
