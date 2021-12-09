import nrv
import matplotlib.pyplot as plt

## Axon def
y = 0
z = 0
d = 1
L = 5000
model = "HH" # Rattay_Aberham if not precised

axon1 = nrv.unmyelinated(y, z, d, L, model=model)

## test pulse
t_start = 1
duration = 0.1
amplitude = 5
axon1.insert_I_Clamp(0, t_start, duration, amplitude)

## Simulation
t_sim = 20
results = axon1.simulate(t_sim=t_sim)
del axon1

## Processing
# Color Map
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
plt.show()
