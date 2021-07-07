import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 1
L = 5000

t_start = 1
duration = 0.5
amplitude = 2

# test 1: 1 section stim in middle
axon1 = nrv.unmyelinated(y,z,d,L,model='Tigerholm',dt=0.001,Nrec=100)
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
results = axon1.simulate(t_sim=10,record_I_ions=True, record_particles=True)
print(axon1.T == 37)
del axon1

if results['Simulation_state'] == 'Unsuccessful':
	print(results['Error_from_prompt'])

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/35_A.png')

plt.figure()
plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
plt.xlabel('time (ms)')
plt.ylabel('V membrane (mV)')
plt.legend()
plt.savefig('./unitary_tests/figures/35_B.png')

fig, axs = plt.subplots(3)

axs[0].plot(results['t'],results['V_mem'][25])
axs[1].plot(results['t'],results['I_na'][25],label='I_na')
axs[1].plot(results['t'],results['I_k'][25],label='I_k')
axs[1].plot(results['t'],results['I_ca'][25],label='I_ca')

axs[2].plot(results['t'], results['m_nav18'][25],label='m_nav18')
axs[2].plot(results['t'], results['h_nav18'][25],label='h_nav18')
axs[2].plot(results['t'], results['s_nav18'][25],label='s_nav18')
axs[2].plot(results['t'], results['u_nav18'][25],label='u_nav18')
axs[2].plot(results['t'], results['m_nav19'][25],label='m_nav19')
axs[2].plot(results['t'], results['h_nav19'][25],label='h_nav19')
axs[2].plot(results['t'], results['s_nav19'][25],label='s_nav19')
axs[2].plot(results['t'], results['m_nattxs'][25],label='m_nattxs')
axs[2].plot(results['t'], results['h_nattxs'][25],label='h_nattxs')
axs[2].plot(results['t'], results['s_nattxs'][25],label='s_nattxs')
axs[2].plot(results['t'], results['n_kdr'][25],label='m_kdr')
axs[2].plot(results['t'], results['m_kf'][25],label='m_kf')
axs[2].plot(results['t'], results['h_kf'][25],label='h_kf')
axs[2].plot(results['t'], results['ns_ks'][25],label='ns_ks')
axs[2].plot(results['t'], results['nf_ks'][25],label='nf_ks')
axs[2].plot(results['t'], results['w_kna'][25],label='w_kna')
axs[2].plot(results['t'], results['ns_h'][25],label='ns_h')
axs[2].plot(results['t'], results['nf_h'][25],label='nf_h')
plt.savefig('./unitary_tests/figures/35_C.png')


#plt.show()