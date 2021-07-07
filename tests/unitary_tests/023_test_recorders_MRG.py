import nrv
import matplotlib.pyplot as plt


y = 0
z = 0
d = 10
L = 27000


axon1 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

t_start = 2
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)

results = axon1.simulate(t_sim=10,record_I_mem=True,record_I_ions=True,record_particles=True)
del axon1

if results['Simulation_state'] == 'Unsuccessful':
	print(results['Error_from_prompt'])

fig, axs = plt.subplots(4)
axs[0].plot(results['t'],results['V_mem'][10])
axs[0].set_xlabel('time (ms)')
axs[0].set_ylabel('voltage (mV)')

axs[1].plot(results['t'],results['I_mem'][10])
axs[1].set_xlabel('time (ms)')
axs[1].set_ylabel('current (mA/cm^2)')


axs[2].plot(results['t'],results['I_na'][10],label='I_na')
axs[2].plot(results['t'],results['I_nap'][10],label='I_nap')
axs[2].plot(results['t'],results['I_k'][10],label='I_k')
axs[2].plot(results['t'],results['I_l'][10],label='I_l')
axs[2].set_xlabel('time (ms)')
axs[2].legend()

axs[3].plot(results['t'],results['m'][10],label='m')
axs[3].plot(results['t'],results['s'][10],label='s')
axs[3].plot(results['t'],results['h'][10],label='h')
axs[3].plot(results['t'],results['mp'][10],label='mp')
axs[3].set_xlabel('time (ms)')
axs[3].legend()
plt.savefig('./unitary_tests/figures/23_A.png')


axon2 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='all')
axon2.insert_I_Clamp_node(2, t_start, duration, amplitude)

results2 = axon2.simulate(t_sim=10,record_I_mem=True)
del axon2

plt.figure()
map = plt.pcolormesh(results2['t'], results2['x_rec'], results2['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/23_B.png')

plt.figure()
map = plt.pcolormesh(results2['t'], results2['x_rec'], results2['I_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane current (mA/cm^2)')
plt.savefig('./unitary_tests/figures/23_C.png')

#plt.show()