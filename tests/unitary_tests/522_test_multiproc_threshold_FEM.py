import nrv
import numpy as np
from time import perf_counter
nrv.parameters.set_nrv_verbosity(2)


def biphasic_pulse_update(axon,amp, pw, start_p = 1, elec_id = 0,t_inter=50e-3):
    stim_1 = nrv.stimulus()
    stim_1.biphasic_pulse(start = start_p, s_anod=amp,t_stim=pw,s_cathod=amp,t_inter=t_inter)
    axon.change_stimulus_from_electrode(elec_id, stim_1)

def process_threshold(diam):
    arg_stim = {'pw':50e-3, 'elec_id':0, 'start_p':1}
    #binary search parameters
    amp_max = 200                   #maximum stimulation amplitude, in µs
    amp_tol = 5                   #binary search tolerance, in %

    model= 'MRG'
    n_node = 20     #20 Node of Ranvier for each axon

    # axon location
    z_axon = 0    # axon z position, in [um]
    y_axon = 100  # axon z position, in [um]

    ### Simulation box size
    Outer_D = 6     # in in [mm]

    #### Nerve and fascicle geometry
    Nerve_D = 1000      # in [um]
    fasc_geom = nrv.create_cshape(diameter=800)    # in [um]
    perineurium_thickeness = 25 # in [um]

    #binary search parameters
    amp_max = 150                   #maximum stimulation amplitude, in µs

    #LIFE
    LIFE_length = 1000             #electrode active site length
    y_elect = 0
    z_elect = 0
    D_1 = 25                    #electrode diam
    L=nrv.get_length_from_nodes(diam,n_node)
    #set the FEM parameters
    extra_stim = nrv.FEM_stimulation()
    extra_stim.reshape_outerBox(Outer_D)
    extra_stim.reshape_nerve(Nerve_D, L)
    extra_stim.reshape_fascicle(fasc_geom)
    #axon creation
    axon1 = nrv.myelinated(y_axon,z_axon,diam,L,rec='nodes',model=model)
    n_node = len(axon1.x_nodes)
    x_elec = axon1.x_nodes[n_node//2]       # electrode y position, in [um]
    y_c = 0
    x_1_offset = x_elec - (LIFE_length/2)
    LIFE = nrv.LIFE_electrode('LIFE_1', D_1, LIFE_length, x_1_offset, y_elect, z_elect)

    # extracellular stimulation setup
    extra_stim.add_electrode(LIFE, nrv.stimulus())
    axon1.attach_extracellular_stimulation(extra_stim)

    axon1.get_electrodes_footprints_on_axon()
    threshold = nrv.axon_AP_threshold(axon = axon1,amp_max = amp_max,tol = 1,
                                      update_func = biphasic_pulse_update, args_update=arg_stim, 
                                      verbose = False)
    del extra_stim,axon1 #to prevent meshing error (known bug)
    return(threshold)

#Axon ranges from 2µm to 20µm
d_min = 2
d_max = 20
n_diam = 10
diam_list = np.round(np.linspace(d_min,d_max,num=n_diam))

if __name__ == '__main__':
    threshold_out = []
    start = perf_counter()
    for diam in diam_list:
        th = process_threshold(diam)
        threshold_out.append(th)
    stop = perf_counter()
    print(threshold_out)
    print(stop-start)
    start_mp = perf_counter()
    thresholds_MP = nrv.search_threshold_dispatcher(process_threshold,diam_list)
    stop_mp = perf_counter()

    print(thresholds_MP)
    print(threshold_out)
    print(thresholds_MP==threshold_out)
    print(f"without multiprocc: {np.round(stop-start,2)}s")
    print(f"with multiprocc: {np.round(stop_mp-start_mp,2)}s")