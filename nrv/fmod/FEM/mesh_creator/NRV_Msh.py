from ....backend.log_interface import rise_warning
from ....nmod.nerve import nerve
from ....nmod.fascicles import fascicle
from ....utils.units import *
from ...electrodes import *
from ...extracellular import is_FEM_extra_stim, FEM_stimulation
from .NerveMshCreator import *


def mesh_from_electrode(
    elec:FEM_electrode,
    mesh:NerveMshCreator=None,
    Length:float=10000,
    Outer_D:float=5,
    Nerve_D:float=4000,
    y_c:float=0,
    z_c:float=0,
    res:float | str="default",
)->NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    if not is_FEM_electrode(elec):
        rise_warning("Only FEM electrode can be added to a mesh")
    else:
        if mesh is None:
            mesh = NerveMshCreator(
                Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c
            )
        elec.parameter_model(mesh, res=res)
    return mesh

def mesh_from_extracellular_context(
    extracel_context:FEM_stimulation,
    mesh:NerveMshCreator|None=None,
    Length:float=10000,
    Outer_D:float=5,
    Nerve_D:float=4000,
    y_c:float=0,
    z_c:float=0,
    res_elec:list[float]|float|str="default",
)->NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    if not is_FEM_extra_stim(extracel_context):
        rise_warning("Only FEM electrode can be added to a mesh")
    else:
        N_contact = 0
        if np.iterable(res_elec) and not isinstance(res_elec, str):
            if len(res_elec) == len(fascicle.extra_stim.electrodes):
                res = res_elec
            else:
                rise_warning(
                    "length of res_elec and fascicle.extra_stim.electrodes does not match",
                    "only first value kept",
                )
                res = [res_elec[0] for k in range(len(fascicle.extra_stim.electrodes))]
        else:
            res = [res_elec for k in range(len(fascicle.extra_stim.electrodes))]
        if mesh is None:
            mesh = NerveMshCreator(
                Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c
            )
        for i_elec, elec in enumerate(extracel_context.electrodes):
            if (not elec.is_multipolar) or N_contact <= 0:
                mesh = mesh_from_electrode(elec, mesh=mesh, res=res[i_elec])
                if elec.is_multipolar:
                    N_contact = elec.N_contact
            else:
                N_contact -= 1
    return mesh


def mesh_from_fascicle(
    fascicle:fascicle,
    mesh:NerveMshCreator|None=None,
    Length:float=10000,
    Outer_D:float=5,
    Nerve_D:float=4000,
    y_c:float=0,
    z_c:float=0,
    add_axons:bool=True,
    add_context:bool=False,
    res_nerve:float|str="default",
    res_fasc:float|str="default",
    res_ax:list[float]|float|str="default",
    res_elec:list[float]|float|str="default",
)->NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    if mesh is None:
        mesh = NerveMshCreator(
            Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c
        )
        if res_nerve != "default":
            mesh.reshape_nerve(res=res_nerve)

    mesh.reshape_fascicle(
        d=fascicle.D,
        y_c=fascicle.y_grav_center,
        z_c=fascicle.z_grav_center,
        res=res_fasc,
    )
    if add_axons:
        is_NoR_relative_position = len(fascicle.NoR_relative_position) != 0
        for i_ax in range(fascicle.n_ax):
            if is_NoR_relative_position:
                node_sift = fascicle.NoR_relative_position[i_ax]
            else:
                node_sift = 0
            ax_d = round(fascicle.axons_diameter[i_ax], 3)
            ax_y = round(fascicle.axons_y[i_ax], 3)
            ax_z = round(fascicle.axons_z[i_ax], 3)
            mye = bool(fascicle.axons_type[i_ax])
            if isinstance(res_ax, str) and res_ax != "default":
                res_ax = eval(str(fascicle.axons_diameter[i_ax]) + res_ax)
            mesh.reshape_axon(d=ax_d, y=ax_y, z=ax_z, myelinated=mye, node_sift=node_sift, res=res_ax)
    if add_context and fascicle.extra_stim is not None:
        mesh = mesh_from_extracellular_context(
            fascicle.extra_stim,
            mesh=mesh,
            res_elec=res_elec
        )
    return mesh


def mesh_from_nerve(
    nerve:nerve,
    length:float=None,
    add_axons:bool=True,
    res_nerve:float|str="default",
    res_fasc:list[float]|float|str="default",
    res_ax:list[float]|float|str="default",
    res_elec:list[float]|float|str="default",
)->NerveMshCreator:
    """
    
    """
    length = length or nerve.L
    mesh = NerveMshCreator(
        Length=length,
        Outer_D=nerve.Outer_D,
        Nerve_D=nerve.D,
        y_c=nerve.y_grav_center,
        z_c=nerve.z_grav_center,
    )
    mesh.reshape_nerve(res=res_nerve)
    if np.iterable(res_fasc) and not isinstance(res_fasc, str):
        if len(res_fasc) == len(nerve.fascicles):
            res = res_fasc
        else:
            rise_warning(
                "length of res_fasc and nerve.fascicles does not match",
                "only first value kept",
            )
            res = [res_fasc[0] for k in range(len(nerve.fascicles))]
    else:
        res = [res_fasc for k in range(len(nerve.fascicles))]
    for i_fasc, fasc in enumerate(nerve.fascicles.values()):
        mesh = mesh_from_fascicle(
            fasc,
            mesh=mesh,
            add_context=False,
            add_axons=add_axons,
            res_ax=res_ax,
            res_fasc=res[i_fasc],
        )
    if nerve.extra_stim is not None:
        mesh = mesh_from_extracellular_context(
            nerve.extra_stim,
            mesh=mesh,
            res_elec=res_elec
            )
    return mesh
