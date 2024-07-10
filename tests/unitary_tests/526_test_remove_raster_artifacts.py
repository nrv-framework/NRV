import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 0.5
L = 2000

# stimulus
start = 1
I_pulse = 500
T_pulse= 100e-3
stim1 = nrv.stimulus()
stim1.pulse(start, -I_pulse, T_pulse)

start = 3
I_pulse = 285
T_pulse= 100e-3
stim2 = nrv.stimulus()
stim2.pulse(start, -I_pulse, T_pulse)

start = 5
I_pulse = 500
T_pulse= 100e-3
stim3 = nrv.stimulus()
stim3.pulse(start, -I_pulse, T_pulse)

start = 7.5
I_pulse = 270
T_pulse= 100e-3
stim4 = nrv.stimulus()
stim4.pulse(start, -I_pulse, T_pulse)

stim = stim1 + stim2 + stim3 + stim4

#No APs
axon0 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')

# electrode
x_elec = L/2                # electrode x position, in [um]
y_elec = 100                # electrode y position, in [um]
z_elec = 0                  # electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

extra_stim = nrv.stimulation("endoneurium_ranck")
extra_stim.add_electrode(E1, stim)
axon0.attach_extracellular_stimulation(extra_stim)
results = axon0.simulate(t_sim=7)
results.rasterize(clear_artifacts=False)
plt.figure()
plt.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'],s=80)

results.rasterize(clear_artifacts=True)
plt.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'],s=30)


x_APs,_,t_APs,_ = results.split_APs()
print(f"Number of APs detected: {results.count_APs()}")
print(f"APs reached end: {results.APs_reached_end()}")
print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
print(f"InterAP collision detected: {results.detect_AP_collisions()}")

for x_AP,t_AP in zip(x_APs,t_APs):
    plt.scatter(t_AP,x_AP,s=10)
    x_start,t_start = results.get_start_AP(x_AP,t_AP)
    x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
    x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
    plt.scatter(t_start,x_start,s=10,c = 'k')
    plt.scatter(t_xmax,x_max,s=10,c = 'g')
    plt.scatter(t_xmin,x_min,s=10,c = 'b')

if results.detect_AP_collisions():
    x_coll,t_coll = results.get_collision_pts()
    plt.scatter(t_coll,x_coll,s=50,c = 'k')
    
plt.xlabel('time (ms)')
plt.ylabel(r'position along the axon($\mu m$)')
plt.xlim(0,results['tstop'])

plt.savefig('./unitary_tests/figures/526.png')

#plt.show()