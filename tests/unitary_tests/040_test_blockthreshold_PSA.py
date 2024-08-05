import nrv
import matplotlib.pyplot as plt
from pathlib import Path

t_sim = 10

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 10						# axon diameter, in [um]
L = 25_000					# axon length, along x axis, in [um]
axon1 = nrv.myelinated(y,z,d,L,T=37,rec='nodes',dt=0.001,Nseg_per_sec=3)

#electrode
n_node = len(axon1.x_nodes)
x_elec = axon1.x_nodes[n_node//2]
y_elec = 500
z_elec = 0
PSA = nrv.point_source_electrode(x_elec,y_elec,z_elec)
stim1 = nrv.stimulus() #dummy stim
stim1.sinus(1,t_sim,100,10)

### define extra cellular stimulation
extra_stim = nrv.stimulation('endoneurium_bhadra')
extra_stim.add_electrode(PSA, stim1)
axon1.attach_extracellular_stimulation(extra_stim)

### Test pulse
test_start = 4
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp(0.05, test_start, duration, amplitude)

#Update function for KES sine block
def KES_update(axon,amp, freq_KES, t_KES, start_KES = 1, elec_id = 0):
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,amp,freq_KES)
    axon.change_stimulus_from_electrode(elec_id, stim_KES)
    del stim_KES

#parameters for the waveforms
arg_stim = {'freq_KES':10, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}
arg_stim2 = {'freq_KES':20, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}
max_amp = 1000 #maximum search boundary

save_path='./unitary_tests/figures/test_40A/'
save_path2='./unitary_tests/figures/test_40B/'

Path(save_path).mkdir(parents=True, exist_ok=True)
Path(save_path2).mkdir(parents=True, exist_ok=True)


threshold_10khz = nrv.axon_block_threshold(axon = axon1,amp_max = max_amp,update_func = KES_update, args_update=arg_stim,
                                           AP_start = test_start, freq = arg_stim['freq_KES'], t_sim = t_sim, save_path=save_path)
threshold_20khz = nrv.axon_block_threshold(axon = axon1,amp_max = max_amp,update_func = KES_update, args_update=arg_stim2,
                                           AP_start = test_start, freq = arg_stim2['freq_KES'], t_sim = t_sim, save_path=save_path2)

del axon1


#unmyelianted fibers
save_path3='./unitary_tests/figures/test_40C/'
save_path4='./unitary_tests/figures/test_40D/'
Path(save_path3).mkdir(parents=True, exist_ok=True)
Path(save_path4).mkdir(parents=True, exist_ok=True)

t_sim = 25

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 1						# axon diameter, in [um]
L = 5_000					# axon length, along x axis, in [um]
axon1 = nrv.unmyelinated(y,z,d,L)

x_elec = 5_000//2
y_elec = 100
z_elec = 0
PSA = nrv.point_source_electrode(x_elec,y_elec,z_elec)

extra_stim = nrv.stimulation('endoneurium_bhadra')
extra_stim.add_electrode(PSA, stim1)
axon1.attach_extracellular_stimulation(extra_stim)

test_start = 12
axon1.insert_I_Clamp(0.05, test_start, duration, amplitude)

arg_stim = {'freq_KES':10, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}
arg_stim2 = {'freq_KES':20, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}

max_amp = 1_000 #maximum search boundary
threshold_10khz = nrv.axon_block_threshold(axon = axon1,amp_max = max_amp,update_func = KES_update, args_update=arg_stim,
                                           AP_start = test_start, freq = arg_stim['freq_KES'], t_sim = t_sim, save_path=save_path3)

threshold_20khz = nrv.axon_block_threshold(axon = axon1,amp_max = max_amp,update_func = KES_update, args_update=arg_stim2,
                                           AP_start = test_start, freq = arg_stim2['freq_KES'], t_sim = t_sim, save_path=save_path4)