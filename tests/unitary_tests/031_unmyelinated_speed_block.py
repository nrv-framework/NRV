import nrv
import matplotlib.pyplot as plt

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 1						# axon diameter, in [um]
L = 5000					# axon length, along x axis, in [um]
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.002)

# load material properties
epineurium = nrv.load_material('endoneurium_bhadra')

# test pulse
t_start = 10
duration = 0.1
amplitude = 3
axon1.insert_I_Clamp(0.2, t_start, duration, amplitude)

#print(axon1.axonnodes)
#stimulus Block
block_start=3 #ms
block_duration=15 #ms
block_amp=100 #µA
block_freq=10 #kHz

# Block electrode
x_elec = L/2
y_elec = 100
z_elec = 0
E = nrv.point_source_electrode(x_elec,y_elec,z_elec)
stim1 = nrv.stimulus()
stim1.sinus(block_start, block_duration, block_amp, block_freq,dt=1/(block_freq*40))

### define extra cellular stimulation
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E, stim1)
extra_stim.synchronise_stimuli()
axon1.attach_extracellular_stimulation(extra_stim)


results = axon1.simulate(t_sim=20, record_particles=True,record_I_ions=True,)
del axon1
print('Simulation performed in '+str(results['sim_time'])+' s')



results.filter_freq('V_mem',10)
results.rasterize(vm_key='V_mem_filtered')
speed = results.get_avg_AP_speed("V_mem_filtered")


block=results.is_blocked(t_start,block_freq)
print('speed='+str(speed)+'m/s')
print(block == False) # the spike should pass
#print(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'])
plt.figure()
plt.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel(r'position along the axon($\mu m$)')
plt.xlim(0,results['tstop'])
plt.ylim(0,results['L'])
plt.savefig('./unitary_tests/figures/31_A.png')


### test 2
block_amp=700 #µA
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.002)
axon1.insert_I_Clamp(0.2, t_start, duration, amplitude)
stim2 = nrv.stimulus()
stim2.sinus(block_start, block_duration, block_amp, block_freq,dt=1/(block_freq*40))
### define extra cellular stimulation
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E, stim2)
extra_stim.synchronise_stimuli()
axon1.attach_extracellular_stimulation(extra_stim)


results2 = axon1.simulate(t_sim=20, record_particles=True,record_I_ions=True,)
del axon1

results2.filter_freq('V_mem',10)
results2.rasterize(vm_key='V_mem_filtered')
speed = results2.get_avg_AP_speed("V_mem_filtered")
block=results2.is_blocked(t_start,block_freq)
print('speed='+str(speed)+'m/s')
print(block == True) # should block
plt.figure()
plt.scatter(results2['V_mem_filtered_raster_time'],results2['V_mem_filtered_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel(r'position along the axon($\mu m$)')
plt.xlim(0,results2['tstop'])
plt.ylim(0,results2['L'])
plt.savefig('./unitary_tests/figures/31_B.png')

#plt.show()

