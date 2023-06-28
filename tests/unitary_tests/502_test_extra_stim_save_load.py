
import nrv
import matplotlib.pyplot as plt

nrv.parameters.set_nrv_verbosity(4)
# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 1						# axon diameter, in [um]
L = 5000					# axon length, along x axis, in [um]
axon1 = nrv.unmyelinated(y,z,d,L)
# electrode def
x_elec = L/2				# electrode x position, in [um]
y_elec = 100				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

# load material properties
epineurium = nrv.load_material('endoneurium_bhadra')

# stimulus def
start = 1
I_cathod = 500
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
#stim1.pulse(start, -I_cathod, duration = T_cathod)

plt.figure()
plt.step(stim1.t, stim1.s,where='post',label='1')
plt.xlabel('time (s)')
plt.ylabel('stimulation current (uA)')
plt.grid()
plt.savefig('./unitary_tests/figures/502_A.png')

# extracellular stimulation setup
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E1, stim1)
axon1.attach_extracellular_stimulation(extra_stim)

# simulate the axon
axon1.save(True, "./unitary_tests/figures/502_ax.json", extracel_context=True)
results = axon1.simulate(t_sim=5)
print(type(axon1))

del axon1

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/502_B.png')
#plt.show()

axon2 = nrv.load_any('./unitary_tests/figures/502_ax.json', extracel_context=True)
results = axon2.simulate(t_sim=5)
del axon2

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/502_C.png')
