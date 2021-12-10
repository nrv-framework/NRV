import nrv
import matplotlib.pyplot as plt

## Axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 1						# axon diameter position, in [um]
L = 5000					# axon length along x, in [um]
model = "HH" # Rattay_Aberham if not precised

axon1 = nrv.unmyelinated(y, z, d, L, model=model)

## test pulse
t_start = 1					# AP initial time during the sim, in [ms]
duration = 0.1				# AP duration, in [ms]
amplitude = 5				# AP amplitude, in [nA]
x_start = 0					# AP initial postition along the axon, in [ms]
axon1.insert_I_Clamp(x_start, t_start, duration, amplitude)

## Simulation
t_sim = 20					# sim duration, in [ms]
results = axon1.simulate(t_sim=t_sim)
del axon1

## Processing

imid = len(results['V_mem'])//2
plt.figure()
plt.plot(results['t'],results['V_mem'][imid],color='k')
plt.savefig('figures/01_spike_center_axon.png')

# Color Map
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('figures/01_Color_Map.png')

# Raster plot
nrv.rasterize(results,'V_mem')
plt.figure()
plt.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel('position along the axon($\mu m$)')
plt.xlim(0,t_sim)
plt.ylim(0,results['L'])
plt.savefig('figures/01_Raster_Plot.png')

#plt.show()