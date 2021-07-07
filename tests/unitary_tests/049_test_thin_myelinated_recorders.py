import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 2
L = 2000


axon1 = nrv.thin_myelinated(y,z,d,L,model='Extended_Gaines',dt=0.001,rec='nodes')

t_start = 2
duration = 0.5
amplitude = 0.4
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)

results1 = axon1.simulate(t_sim=10,record_I_ions=True, record_particles=True)
del axon1
if results1['Simulation_state'] == 'Unsuccessful':
	print(results1['Error_from_prompt'])

axon2 = nrv.thin_myelinated(y,z,d,L,model='RGK',dt=0.001,rec='nodes')
axon2.insert_I_Clamp(0.5, t_start, duration, amplitude)
results2 = axon2.simulate(t_sim=10,record_I_ions=True, record_particles=True)
del axon2
if results2['Simulation_state'] == 'Unsuccessful':
	print(results2['Error_from_prompt'])

fig, axs = plt.subplots(3)
axs[0].plot(results1['t'],results1['V_mem'][3])

axs[1].plot(results1['t'],results1['I_na'][3])
axs[1].plot(results1['t'],results1['I_nap'][3])
axs[1].plot(results1['t'],results1['I_k'][3])
axs[1].plot(results1['t'],results1['I_kf'][3])
axs[1].plot(results1['t'],results1['I_l'][3])

axs[2].plot(results1['t'],results1['m'][3])
axs[2].plot(results1['t'],results1['mp'][3])
axs[2].plot(results1['t'],results1['s'][3])
axs[2].plot(results1['t'],results1['h'][3])
axs[2].plot(results1['t'],results1['n'][3])
plt.savefig('./unitary_tests/figures/49_A.png')

fig, axs2 = plt.subplots(3)
axs2[0].plot(results2['t'],results2['V_mem'][3])

axs2[1].plot(results2['t'],results2['I_na'][3])
axs2[1].plot(results2['t'],results2['I_k'][3])
axs2[1].plot(results2['t'],results2['I_l'][3])

axs2[2].plot(results2['t'],results2['m_nav19'][3])
axs2[2].plot(results2['t'],results2['s_nav19'][3])
axs2[2].plot(results2['t'],results2['h_nav19'][3])
axs2[2].plot(results2['t'],results2['m_nax'][3])
axs2[2].plot(results2['t'],results2['h_nax'][3])
axs2[2].plot(results2['t'],results2['nf_ks'][3])
axs2[2].plot(results2['t'],results2['ns_ks'][3])
plt.savefig('./unitary_tests/figures/49_B.png')

#plt.show()