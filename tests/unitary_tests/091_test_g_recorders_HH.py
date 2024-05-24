import nrv
import matplotlib.pyplot as plt

import nrv
import numpy as np
import matplotlib.pyplot as plt

y = 0
z = 0
d = 1
L = 500
cm = 1 * 1e-6 # F

t_start = 0
duration = 0.2
amplitude = 1


gnabar_hh = 0.120
gkbar_hh = 0.036
gl_hh = 0.0003


axon1 = nrv.unmyelinated(y,z,d,L,dt=0.0005,Nseg_per_sec = 500, model='HH')
axon1.insert_I_Clamp(0, t_start, duration, amplitude)

t_sim=4
results = axon1.simulate(t_sim=t_sim, record_particles=True, record_g_mem=True, record_g_ions=True)
del axon1

#### Check results
gna_hh = gnabar_hh*np.multiply(np.power(results['m'],3),results['h'])
gk_hh = gkbar_hh*np.power(results['n'],4)

gm = gna_hh + gk_hh + gl_hh  # en S.cm-2

### !! delay of dt between particle rec and conductance rec ###
print(np.allclose(gna_hh[:,:-1],results['g_na'][:,1:]))
print(np.allclose(gk_hh[:,:-1],results['g_k'][:,1:]))
print(np.allclose(gm[:,:-1],results['g_mem'][:,1:]))


##### Plots results
fig, ax1 = plt.subplots()
ax1.set_xlabel('time (ms)')

ax1.plot(results['t'],results['V_mem'][L//2]-results['V_mem'][L//2][0], 'k',label='Vmem variation')
ax1.set_ylabel('Mem. Voltage (mV)')
ax2 = ax1.twinx()
ax1.legend(loc=2)

ax2.plot(results['t'], results['g_na'][L//2]*1000, label=r'$g_{Na}$')
ax2.plot(results['t'], results['g_k'][L//2]*1000, label=r'$g_{K}$')
ax2.plot(results['t'], results['g_l'][L//2]*1000, label=r'$g_{l}$')
ax2.plot(results['t'], results['g_mem'][L//2]*1000, label=r'$g_{mem}$')
ax2.set_ylabel(r'conductance ($mS.cm^{-2}$)')
ax2.legend()
plt.savefig('./unitary_tests/figures/91_A.png')

fc = results['g_mem']/(2*np.pi*cm)

plt.figure(figsize=(9,7))
plt.subplot(3,1,1)
plt.plot(results['t'],results['V_mem'][L//2])
plt.xlabel('time (ms)')
plt.ylabel('Mem. Voltage (mV)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red',label='de-')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue',label='re-')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green',label='hyper-')
plt.grid()
plt.legend(title = 'polarisation')
plt.subplot(3,1,2)
plt.semilogy(results['t'],results['g_mem'][L//2])
plt.xlabel('time (ms)')
plt.ylabel(r'$g_m$ ($mS\cdot cm^{-2}$)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green')
plt.grid()
plt.subplot(3,1,3)
plt.semilogy(results['t'],fc[L//2])
plt.xlabel('time (ms)')
plt.ylabel(r'$f_{mem}$ ($Hz$)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green')
plt.grid()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/91_B.png')


#plt.show()