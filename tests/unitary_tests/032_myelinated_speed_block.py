import nrv
import matplotlib.pyplot as plt

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 10						# axon diameter, in [um]
L = 58000					# axon length, along x axis, in [um]
axon1 = nrv.myelinated(y,z,d,L,T=37,rec='nodes',dt=0.002)

# load material properties
epineurium = nrv.load_material('endoneurium_bhadra')

# test pulse
t_start = 20
duration = 0.1
amplitude = 3
axon1.insert_I_Clamp(0, t_start, duration, amplitude)

#print(axon1.axonnodes)
#stimulus Block
block_start=3 #ms
block_duration=20 #ms
block_amp=200 #µA
block_freq=10 #kHz

# Block electrode
x_elec = axon1.x_nodes[25]
y_elec = 1000
z_elec = 0
E = nrv.point_source_electrode(x_elec,y_elec,z_elec)
stim1 = nrv.stimulus()
stim1.sinus(block_start, block_duration, block_amp, block_freq,dt=1/(block_freq*40))

### define extra cellular stimulation
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E, stim1)
extra_stim.synchronise_stimuli()
axon1.attach_extracellular_stimulation(extra_stim)


results = axon1.simulate(t_sim=30, record_particles=True,record_I_ions=True,)
del axon1
print('Simulation performed in '+str(results['sim_time'])+' s')

nrv.filter_freq(results,'V_mem',10)
nrv.rasterize(results,'V_mem_filtered')
speed=nrv.speed(results,t_start=18,t_stop=22,x_start=20,x_stop=25000)
block=nrv.block(results)#,t_start=3,t_stop=5)
print('speed='+str(speed)+'m/s')
print(block == False) # the spike should pass
plt.figure()
plt.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel('position along the axon($\mu m$)')
plt.xlim(0,results['tstop'])
plt.savefig('./unitary_tests/figures/32_A.png')

### test 2
block_amp=700 #µA
axon1 = nrv.myelinated(y,z,d,L,dt=0.002)
axon1.insert_I_Clamp(0, t_start, duration, amplitude)
stim2 = nrv.stimulus()
stim2.sinus(block_start, block_duration, block_amp, block_freq,dt=1/(block_freq*40))
### define extra cellular stimulation
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E, stim2)
extra_stim.synchronise_stimuli()
axon1.attach_extracellular_stimulation(extra_stim)


results2 = axon1.simulate(t_sim=30)
del axon1

nrv.filter_freq(results2,'V_mem',10)
nrv.rasterize(results2,'V_mem_filtered')
speed=nrv.speed(results2)
block=nrv.block(results2)
print('speed='+str(speed)+'m/s')
print(block == True) # should block
plt.figure()
plt.scatter(results2['V_mem_filtered_raster_time'],results2['V_mem_filtered_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel('position along the axon($\mu m$)')
plt.xlim(0,results2['tstop'])
plt.ylim(0,results2['L'])
plt.savefig('./unitary_tests/figures/32_B.png')


#plt.show()

