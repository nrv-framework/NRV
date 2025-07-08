from ..backend._log_interface import rise_warning
from ..nmod._nerve import nerve
from ..nmod._fascicles import fascicle
from ..utils._misc import get_MRG_parameters
from ..fmod._electrodes import *
from ..fmod._extracellular import is_FEM_extra_stim, FEM_stimulation
from ..fmod.FEM.mesh_creator._NerveMshCreator import *
from ._spec_loaders import load_axon, load_fascicle, load_nerve


def mesh_from_electrode(
    elec: FEM_electrode,
    mesh: NerveMshCreator = None,
    Length: float = 10000,
    Outer_D: float = 5,
    Nerve_D: float = 4000,
    y_c: float = 0,
    z_c: float = 0,
    res: float | str = "default",
) -> NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    elec = load_any(elec)
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
    extracel_context: FEM_stimulation,
    mesh: NerveMshCreator | None = None,
    Length: float = 10000,
    Outer_D: float = 5,
    Nerve_D: float = 4000,
    y_c: float = 0,
    z_c: float = 0,
    res_elec: list[float] | float | str = "default",
) -> NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    extracel_context = load_any(extracel_context)
    if not is_FEM_extra_stim(extracel_context):
        rise_warning("Only FEM electrode can be added to a mesh")
    else:
        N_contact = 0
        if np.iterable(res_elec) and not isinstance(res_elec, str):
            if len(res_elec) == len(extracel_context.electrodes):
                res = res_elec
            else:
                rise_warning(
                    "length of res_elec and fascicle.extra_stim.electrodes does not match",
                    "only first value kept",
                )
                res = [res_elec[0] for k in range(len(extracel_context.electrodes))]
        else:
            res = [res_elec for k in range(len(extracel_context.electrodes))]
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
    fasc: fascicle,
    mesh: NerveMshCreator | None = None,
    Length: float = 10000,
    Outer_D: float = 5,
    Nerve_D: float = 4000,
    y_c: float = 0,
    z_c: float = 0,
    add_axons: bool = True,
    x_shift: float | None = None,
    add_context: bool = False,
    res_nerve: float | str = "default",
    res_fasc: float | str = "default",
    res_ax: list[float] | float | str = "default",
    res_elec: list[float] | float | str = "default",
) -> NerveMshCreator:
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    fasc = load_fascicle(fasc, extracel_context=True)
    if mesh is None:
        mesh = NerveMshCreator(
            Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c
        )
        if res_nerve != "default":
            mesh.reshape_nerve(res=res_nerve)

    mesh.reshape_fascicle(geometry=fasc.geom)
    if add_axons:
        if fasc.axons.has_node_shift:
            node_shift = fasc.axons["node_shift"]
        else:
            node_shift = np.zeros(fasc.n_ax)
        if x_shift is not None:
            i_myel = fasc.axons["types"].astype(bool)
            __deltaxs = get_MRG_parameters(fasc.axons["diameters"][i_myel])[5]
            __l1_ = fasc.NoR_relative_position[i_myel] * __deltaxs
            __x_l = (__l1_ - x_shift) % __deltaxs
            node_shift[i_myel] = __x_l / __deltaxs

        for i_ax in range(fasc.n_ax):
            ax_d = round(fasc.axons["diameters"][i_ax], 3)
            ax_y = round(fasc.axons["y"][i_ax], 3)
            ax_z = round(fasc.axons["z"][i_ax], 3)
            mye = bool(fasc.axons["types"][i_ax])
            res_ax_ = res_ax
            if isinstance(res_ax, str) and res_ax != "default":
                res_ax_ = eval(str(fasc.axons["diameters"][i_ax]) + res_ax)
            elif np.iterable(res_ax) and not isinstance(res_ax, str):
                res_ax_ = res_ax[i_ax]
            mesh.reshape_axon(
                d=ax_d,
                y=ax_y,
                z=ax_z,
                myelinated=mye,
                node_shift=node_shift[i_ax],
                res=res_ax_,
            )
    if add_context and fasc.extra_stim is not None:
        mesh = mesh_from_extracellular_context(
            fasc.extra_stim, mesh=mesh, res_elec=res_elec
        )
    return mesh


def mesh_from_nerve(
    nerve: nerve,
    length: float | None = None,
    add_axons: bool = True,
    x_shift: float | None = None,
    res_nerve: float | str = "default",
    res_fasc: list[float] | float | str = "default",
    res_ax: list[float] | float | str = "default",
    res_elec: list[float] | float | str = "default",
) -> NerveMshCreator:
    """
    Build a mesh nerve mesh from an ``nrv.mesh`` instance

    Parameters
    ----------
    nerve : nerve
        nerve to use for meshing mesh
    length : float | None, optional
        if not None, length to use to resize the nerve, by default None
    add_axons : bool, optional
        if True axons are added to the nerve, by default True
    x_shift : float | None, optional
        if not None, add a node shift in um to mesh the myelinated axons by default None
    res_nerve : float | str, optional
        nerve resolution in the epineurium domain, by default "default"
    res_fasc : list[float] | float | str, optional
        fascicle reoulution in the endoneurium domain, by default "default"
    res_ax : list[float] | float | str, optional
        axon resolution in the epneurium domain,, by default "default"
    res_elec : list[float] | float | str, optional
        electrode resolution, by default "default"

    Returns
    -------
    NerveMshCreator
    """
    nerve = load_any(nerve, extracel_context=True)
    if length is not None:
        length = length
    else:
        length = nerve.L
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
            x_shift=x_shift,
            res_ax=res_ax,
            res_fasc=res[i_fasc],
        )
    if nerve.extracel_status():
        mesh = mesh_from_extracellular_context(
            nerve.extra_stim, mesh=mesh, res_elec=res_elec
        )
    return mesh
