import nrv
import matplotlib.pyplot as plt

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 10						# axon diameter, in [um]
L = 50_000					# axon length, along x axis, in [um]
axon1 = nrv.myelinated(y,z,d,L,T=37,rec='nodes',dt=0.001)

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

#Update function for cathodic (monopolar) pulse
def cath_pulse_update(axon,amp, pw, start_p = 1, elec_id = 0):
    stim_1 = nrv.stimulus()
    stim_1.pulse(start=start_p, duration=pw, value = -amp)
    axon.change_stimulus_from_electrode(elec_id, stim_1)

#Update function for biphasic pulse
def biphasic_pulse_update(axon,amp, pw, start_p = 1, elec_id = 0,t_inter=50e-3):
    stim_1 = nrv.stimulus()
    stim_1.biphasic_pulse(start = start_p, s_anod=amp,t_stim=pw,s_cathod=amp,t_inter=t_inter)
    axon.change_stimulus_from_electrode(elec_id, stim_1)

#Update function for cathodic sine pulse
def cath_sine_pulse_update(axon,amp, pw, start_p = 1, elec_id = 0):
    stim_1 = nrv.stimulus()
    freq = 1/(2*pw)
    stim_1.sinus(start_p, pw, amp, freq, offset=0, phase=180, dt=0)
    axon.change_stimulus_from_electrode(elec_id, stim_1)

#parameters for the waveforms
arg_stim = {'pw':50e-3, 'elec_id':0, 'start_p':1}
max_amp = 300 #maximum search boundary

threshold_pulse = nrv.axon_AP_threshold(axon = axon1,amp_max = max_amp,update_func = cath_pulse_update, args_update=arg_stim)
threshold_biphasic = nrv.axon_AP_threshold(axon = axon1,amp_max = max_amp,update_func = biphasic_pulse_update, args_update=arg_stim)
threshold_sine = nrv.axon_AP_threshold(axon = axon1,amp_max = max_amp,update_func = cath_sine_pulse_update, args_update=arg_stim)