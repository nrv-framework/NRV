import nrv
import matplotlib.pyplot as plt

# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 6						# axon diameter, in [um]
L = 10000					# axon length, along x axis, in [um]
axon1 = nrv.myelinated(y,z,d,L,rec='all')

# electrode def
x_elec = L/2				# electrode x position, in [um]
y_elec = 100				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

# load material properties
endoneurium = nrv.load_material('endoneurium_ranck')

# stimulus def
start = 1
I_cathod = 50
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
plt.savefig('./unitary_tests/figures/24_A.png')

# extracellular stimulation setup
extra_stim = nrv.stimulation(endoneurium)
extra_stim.add_electrode(E1, stim1)
axon1.attach_extracellular_stimulation(extra_stim)

# simulate the axon
results = axon1.simulate(t_sim=5)
del axon1

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/24_B.png')

plt.figure()
for k in range(len(results['node_index'])):
	index = results['node_index'][k]
	plt.plot(results['t'], results['V_mem'][index]+k*100, color = 'k')
plt.yticks([])
plt.xlim(0.9,2)
plt.xlabel(r'time ($ms$)')
plt.savefig('./unitary_tests/figures/24_C.png')
#plt.show()