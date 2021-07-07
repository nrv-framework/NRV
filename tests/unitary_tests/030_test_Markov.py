import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 10
L = 20000

########## test A : myelinated record all #############
axon1 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes')
axon1.set_Markov_Nav()

t_start = 2
duration = 0.1
amplitude = 3
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)

results = axon1.simulate(t_sim=6, record_particles=True)
del axon1


if results['Simulation_state'] == 'Unsuccessful':
	print(results['Error_from_prompt'])


plt.figure()
for k in range(len(results['x_rec'])):
	plt.plot(results['t'],results['V_mem'][k]+100*k,color='k')
plt.yticks([])
plt.savefig('./unitary_tests/figures/30_A.png')

fig, axs = plt.subplots(3)
axs[0].plot(results['t'],results['V_mem'][2])

axs[1].plot(results['t'],results['C1_nav11'][2]+results['C2_nav11'][2],label='Nav 1.1 C')
axs[1].plot(results['t'],results['O1_nav11'][2]+results['O2_nav11'][2],label='Nav 1.1 O')
axs[1].plot(results['t'],results['I1_nav11'][2]+results['I2_nav11'][2],label='Nav 1.1 I')
axs[1].legend()

axs[2].plot(results['t'],results['C1_nav16'][2]+results['C2_nav16'][2],label='Nav 1.6 C')
axs[2].plot(results['t'],results['O1_nav16'][2]+results['O2_nav16'][2],label='Nav 1.6 O')
axs[2].plot(results['t'],results['I1_nav16'][2]+results['I2_nav16'][2],label='Nav 1.6 I')
axs[2].legend()
plt.savefig('./unitary_tests/figures/30_B.png')
#plt.show()