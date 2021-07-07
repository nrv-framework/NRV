import nrv
import matplotlib.pyplot as plt


y = 0
z = 0
d = 2
L = 2000


axon1 = nrv.thin_myelinated(y,z,d,L,model='RGK',dt=0.001,rec='nodes')

t_start = 20
duration = 0.5
amplitude = 0.4
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)

results = axon1.simulate(t_sim=30)
del axon1

plt.figure()
plt.plot(results['t'],results['V_mem'][2],color='r')
plt.plot(results['t'],results['V_mem'][6],color='b')
plt.plot(results['t'],results['V_mem'][12],color='k')
plt.savefig('./unitary_tests/figures/48_A.png')


axon2 = nrv.thin_myelinated(y,z,d,L,model='extended_Gaines',dt=0.001,rec='nodes')
duration = 0.1
amplitude = 1
axon2.insert_I_Clamp(0.5, t_start, duration, amplitude)

results2 = axon2.simulate(t_sim=30)
del axon2

plt.figure()
plt.plot(results2['t'],results2['V_mem'][2],color='r')
plt.plot(results2['t'],results2['V_mem'][6],color='b')
plt.plot(results2['t'],results2['V_mem'][12],color='k')
plt.savefig('./unitary_tests/figures/48_B.png')

#plt.show()