import nrv
import matplotlib.pyplot as plt


y = 0
z = 0
d = 10
L = 20000

########## test A : myelinated record all #############
axon1 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes')

t_start = 2
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)

results = axon1.simulate(t_sim=6)

nrv.rasterize(results,'V_mem')
plt.figure()
plt.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel('position along the axon($\mu m$)')
plt.xlim(0,results['tstop'])
plt.savefig('./unitary_tests/figures/29_A.png')

start_time, start_x_position = nrv.find_spike_origin(results)
print(start_time - t_start < 0.05)
print(start_x_position == results['x_rec'][8])

t_last_up, x_last_up = nrv.find_spike_last_occurance(results,direction='up')
print(t_last_up, x_last_up)
t_last_down, x_last_down = nrv.find_spike_last_occurance(results,direction='down')
print(t_last_down, x_last_down)

#plt.show()