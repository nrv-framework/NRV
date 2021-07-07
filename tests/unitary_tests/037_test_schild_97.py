import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 1
L = 5000

t_start = 1
duration = 0.5
amplitude = 1

# test 1: 1 section stim in middle
axon1 = nrv.unmyelinated(y,z,d,L,model='Schild_97',dt=0.001,Nrec=100)
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
results = axon1.simulate(t_sim=15,record_I_ions=True, record_particles=True)
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
plt.savefig('./unitary_tests/figures/37_A.png')

plt.figure()
plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
plt.xlabel('time (ms)')
plt.ylabel('V membrane (mV)')
plt.legend()
plt.savefig('./unitary_tests/figures/37_B.png')

fig, axs = plt.subplots(3)

axs[0].plot(results['t'],results['V_mem'][25])
axs[1].plot(results['t'],results['I_na'][25],label='I_na')
axs[1].plot(results['t'],results['I_k'][25],label='I_k')
axs[1].plot(results['t'],results['I_ca'][25],label='I_ca')

axs[2].plot(results['t'],results['d_can'][25],label='d_can')
axs[2].plot(results['t'],results['f1_can'][25],label='f1_can')
axs[2].plot(results['t'],results['f2_can'][25],label='f2_can')
axs[2].plot(results['t'],results['d_cat'][25],label='d_cat')
axs[2].plot(results['t'],results['f_cat'][25],label='f_cat')
axs[2].plot(results['t'],results['p_ka'][25],label='p_ka')
axs[2].plot(results['t'],results['q_ka'][25],label='q_ka')
axs[2].plot(results['t'],results['c_ka'][25],label='c_ka')
axs[2].plot(results['t'],results['n_kd'][25],label='n_kd')
axs[2].plot(results['t'],results['x_kds'][25],label='x_kds')
axs[2].plot(results['t'],results['y1_kds'][25],label='y1_kds')
axs[2].plot(results['t'],results['m_naf'][25],label='m_naf')
axs[2].plot(results['t'],results['h_naf'][25],label='h_naf')
axs[2].plot(results['t'],results['m_nas'][25],label='m_nas')
axs[2].plot(results['t'],results['h_nas'][25],label='h_nas')
plt.savefig('./unitary_tests/figures/37_C.png')


#plt.show()