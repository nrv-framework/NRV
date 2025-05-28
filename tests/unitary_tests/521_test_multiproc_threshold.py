import nrv
import numpy as np
from time import perf_counter
nrv.parameters.set_nrv_verbosity(2)


# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 10						# axon diameter, in [um]
L = 50_000					# axon length, along x axis, in [um]
axon1 = nrv.myelinated(y,z,d,L,T=37,rec='nodes',dt=0.005)

#electrode
n_node = len(axon1.x_nodes)
x_elec = axon1.x_nodes[n_node//2]
y_elec = 1000
z_elec = 0
PSA = nrv.point_source_electrode(x_elec,y_elec,z_elec)
stim1 = nrv.stimulus() #dummy stim

### define extra cellular stimulation
extra_stim = nrv.stimulation('endoneurium_bhadra')
extra_stim.add_electrode(PSA, stim1)
axon1.attach_extracellular_stimulation(extra_stim)

#Update function for biphasic pulse
def biphasic_pulse_update(axon,amp, pw, start_p = 1, elec_id = 0,t_inter=50e-3):
    stim_1 = nrv.stimulus()
    stim_1.biphasic_pulse(start = start_p, s_anod=amp,t_stim=pw,s_cathod=amp,t_inter=t_inter)
    axon.change_stimulus_from_electrode(elec_id, stim_1)

#parameters for the waveforms
arg_stim = {'pw':50e-3, 'elec_id':0, 'start_p':1}
max_amp = 300 #maximum search boundary

pw_l = [50e-3,100e-3,150e-3,200e-3,250e-3,300e-3,350e-3,400e-3]



def process_threshold(pw):
    arg_stim['pw'] = pw
    return(nrv.axon_AP_threshold(axon = axon1,amp_max = max_amp,update_func = biphasic_pulse_update, args_update=arg_stim, verbose = False))

if __name__ == '__main__':
    start = perf_counter()

    thresholds = []

    for pw in pw_l:
        th = process_threshold(pw)
        thresholds.append(th)    
    
    stop = perf_counter()
    
    start_mp = perf_counter()
    thresholds_MP = nrv.search_threshold_dispatcher(process_threshold,pw_l,ncore=4)
    stop_mp = perf_counter()

    print(thresholds_MP)
    print(thresholds)
    print(thresholds_MP==thresholds)
    print(f"without multiproc: {np.round(stop-start,2)}s")
    print(f"With multiproc: {np.round(stop_mp-start_mp,2)}s")


