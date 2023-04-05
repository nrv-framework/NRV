from cmath import phase

from .NerveMshCreator import *
from ...electrodes import *
from ....nmod.fascicles import *
from ....backend.log_interface import rise_error, rise_warning, pass_info
from ....utils.units import *



def mesh_from_electrode(elec, mesh=None, Length=10000, Outer_D=5,  Nerve_D=4000, y_c=0, z_c=0):
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    if not is_FEM_electrode(elec):
        rise_warning('Only FEM electrode can be added to a mesh')
    else:
        if mesh is None:
            mesh = NerveMshCreator(Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c)
        elec.parameter_model(mesh)
    return mesh

def mesh_from_fascicle(fascicle, mesh=None, Length=10000, Outer_D=5,  Nerve_D=4000, y_c=0, z_c=0):
    """
    returns the corresponding mesh from a nrv.facsicle
    """
    if mesh is None:
        mesh = NerveMshCreator(Length=Length, Outer_D=Outer_D, Nerve_D=Nerve_D, y_c=y_c, z_c=z_c)
    
    mesh.reshape_fascicle(D=fascicle.D, y_c=fascicle.y_grav_center, z_c=fascicle.z_grav_center)
    
    for i_ax in range(fascicle.N):
        ax_d=round(fascicle.axons_diameter[i_ax], 3)
        ax_y_c=round(fascicle.axons_y[i_ax], 3)
        ax_z_c=round(fascicle.axons_z[i_ax], 3)
        mesh.reshape_axon(D=ax_d, y_c=ax_y_c, z_c=ax_z_c)
    
    if fascicle.extra_stim is not None:
        N_contact = 0
        for elec in fascicle.extra_stim.electrodes:
            if (not elec.is_multipolar) or N_contact<=0:
                mesh = mesh_from_electrode(elec, mesh=mesh)
                if elec.is_multipolar:
                    N_contact = elec.N_contact
                print('elec added')
            else:
                N_contact -= 1

                

    return mesh

def mesh_from_nerve(nerve, mesh=None):
    rise_warning('not implemented yet')