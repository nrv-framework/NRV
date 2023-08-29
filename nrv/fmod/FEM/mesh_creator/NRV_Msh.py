from ....backend.log_interface import rise_warning
from ....nmod.fascicles import *
from ....utils.units import *
from ...electrodes import *
from .NerveMshCreator import *


def mesh_from_electrode(
    elec,
    mesh=None,
    Length=10000,
    Outer_D=5,
    Nerve_D=4000,
    y_c=0,
    z_c=0,
    res="default",
):
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


def mesh_from_fascicle(
    fascicle,
    mesh=None,
    Length=10000,
    Outer_D=5,
    Nerve_D=4000,
    y_c=0,
    z_c=0,
    res_nerve="default",
    res_fasc="default",
    res_ax="default",
    res_elec="default",
):
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
        D=fascicle.D,
        y_c=fascicle.y_grav_center,
        z_c=fascicle.z_grav_center,
        res=res_fasc,
    )

    for i_ax in range(fascicle.N):
        ax_d = round(fascicle.axons_diameter[i_ax], 3)
        ax_y_c = round(fascicle.axons_y[i_ax], 3)
        ax_z_c = round(fascicle.axons_z[i_ax], 3)
        if isinstance(res_ax, str) and res_ax != "default":
            res_ax = eval(str(fascicle.axons_diameter[i_ax]) + res_ax)
        mesh.reshape_axon(D=ax_d, y_c=ax_y_c, z_c=ax_z_c, res=res_ax)

    if fascicle.extra_stim is not None:
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
        for i_elec, elec in enumerate(fascicle.extra_stim.electrodes):
            if (not elec.is_multipolar) or N_contact <= 0:
                mesh = mesh_from_electrode(elec, mesh=mesh, res=res[i_elec])
                if elec.is_multipolar:
                    N_contact = elec.N_contact
            else:
                N_contact -= 1
    return mesh


def mesh_from_nerve(nerve, mesh=None):
    rise_warning("not implemented yet")
