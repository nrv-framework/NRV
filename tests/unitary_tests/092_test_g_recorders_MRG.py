import nrv
import matplotlib.pyplot as plt

import nrv
import numpy as np
import matplotlib.pyplot as plt

gnafbar_mrg = 3.0 # S.cm-2
gnapbar_mrg = 0.01 # S.cm-2
gksbar_mrg = 0.08  # S.cm-2
gl_mrg = 0.007  # S.cm-2
cm=1 * 1e-6 # F

y = 0
z = 0
d = 6
L = nrv.get_length_from_nodes(d, 15)

axon1 = nrv.myelinated(y,z,d,L,dt=0.0005 ,Nseg_per_sec=1,rec='nodes', model='MRG')

t_start = 2
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)


t_sim=15
results = axon1.simulate(t_sim=t_sim, record_particles=True, record_g_mem=True, record_g_ions=True)
del axon1

#### Check results
gnaf_mrg = gnafbar_mrg*np.multiply(np.power(results['m'],3),results['h'])
gnap_mrg = gnapbar_mrg*np.power(results['mp'],3)
gks_mrg = gksbar_mrg*results['s']

gm = gnaf_mrg + gnap_mrg + gks_mrg + gl_mrg  # en S.cm-2
rm = 1/gm 

print(np.allclose(gnaf_mrg,results['g_na']))
print(np.allclose(gnap_mrg,results['g_nap']))
print(np.allclose(gks_mrg,results['g_k']))
print(np.allclose(gm,results['g_mem']))

##### Plots results
mid_node = 5

fig, ax1 = plt.subplots()
ax1.set_xlabel('time (ms)')
ax1.plot(results['t'],results['V_mem'][mid_node]-results['V_mem'][mid_node][0], 'k',label='Vmem variation')
ax1.set_ylabel('Mem. Voltage (mV)')
ax2 = ax1.twinx()
ax1.legend(loc=2)

ax2.plot(results['t'], results['g_na'][mid_node]*1000, label='$g_{Na}$')
ax2.plot(results['t'], results['g_nap'][mid_node]*1000, label='$g_{Nap}$')
ax2.plot(results['t'], results['g_k'][mid_node]*1000, label='$g_{K}$')
ax2.plot(results['t'], results['g_l'][mid_node]*1000, label='$g_{l}$')
ax2.plot(results['t'], results['g_mem'][mid_node]*1000, label='$g_{mem}$')
ax2.set_ylabel('conductance ($mS.cm^{-2}$)')
ax2.legend()
plt.savefig('./unitary_tests/figures/92_A.png')

fc = results['g_mem']/(2*np.pi*cm)

plt.figure(figsize=(9,7))
plt.subplot(3,1,1)
plt.plot(results['t'],results['V_mem'][mid_node])
plt.xlabel('time (ms)')
plt.ylabel('Mem. Voltage (mV)')
plt.grid()
plt.legend(title = 'polarisation')
plt.subplot(3,1,2)
plt.semilogy(results['t'],results['g_mem'][mid_node])
plt.xlabel('time (ms)')
plt.ylabel('$g_m$ ($mS\cdot cm^{-2}$)')
plt.grid()
plt.subplot(3,1,3)
plt.semilogy(results['t'],fc[mid_node])
plt.xlabel('time (ms)')
plt.ylabel('$f_{mem}$ ($Hz$)')
plt.grid()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/92_B.png')

#plt.show()