import nrv
import numpy as np
import matplotlib.pyplot as plt


y = 0
z = 0
d = 10
L = nrv.get_length_from_nodes(d, 20)


axon1 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')
axon1.set_Markov_Nav(np.arange(5,15))

# Voltage clamp
clamp_node = 10
v_stim = nrv.datfile_2_stim('./unitary_tests/sources/065_V_env.dat', dt=0.005)
axon1.insert_V_Clamp_node(clamp_node, v_stim)


plt.figure()
plt.step(v_stim.t, v_stim.s, where='post')
plt.savefig('./unitary_tests/figures/65_A.png')



## IClamp for spike initiation
t_start = 90
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp_node(1, t_start, duration, amplitude)


results = axon1.simulate(t_sim=100)
del axon1

print('Simulation performed in ',results['sim_time'],' s')


plt.figure()
for k in range(len(results['x_rec'])):
	plt.plot(results['t'],results['V_mem'][k]+k*100, color='k')
plt.yticks([])
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/65_B.png')

#plt.show()
