import nrv
import matplotlib.pyplot as plt
import numpy as np

model='Sundt'
y = 0
z = 0
d = 1
L = 5000
Nrec = 100
t_start = 1
duration = 0.5
amplitude = 1

# test 1: 1 section stim in middle
axon1 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
results = axon1.simulate(t_sim=10,record_I_ions=True, record_particles=True)
print(axon1.T == 37)
del axon1

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/34_A.png')

plt.figure()
plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
plt.xlabel('time (ms)')
plt.ylabel('V membrane (mV)')
plt.legend()
plt.savefig('./unitary_tests/figures/34_B.png')

fig, axs = plt.subplots(3)

axs[0].plot(results['t'],results['V_mem'][25])
axs[1].plot(results['t'],results['I_na'][25],label='I_na')
axs[1].plot(results['t'],results['I_k'][25],label='I_k')
axs[1].plot(results['t'],results['I_l'][25],label='I_l')
axs[2].plot(results['t'],results['m'][25],label='m')
axs[2].plot(results['t'],results['n'][25],label='n')
axs[2].plot(results['t'],results['h'][25],label='h')
plt.savefig('./unitary_tests/figures/34_C.png')
del results

# test 2: gmem for stim in left side
cm = 1 * 1e-6 # F
gnabar_hh = 0.120
gkbar_hh = 0.036
gl_hh = 0.0003

axon2 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
axon2.insert_I_Clamp(0, t_start, duration, amplitude)
results = axon2.simulate(t_sim=10, record_particles=True, record_g_ions=True, record_g_mem=True)
print(axon2.T == 37)
del axon2

#### Check results
gna_hh = gnabar_hh*np.multiply(np.power(results['m'],3),results['h'])
gk_hh = gkbar_hh*np.power(results['n'],4)

gm = gna_hh + gk_hh + gl_hh  # en S.cm-2

### !! delay of dt between particle rec and conductance rec ###
print(np.allclose(gna_hh[:,:-1],results['g_na'][:,1:]))
print(np.allclose(gk_hh[:,:-1],results['g_k'][:,1:]))
print(np.allclose(gm[:,:-1],results['g_mem'][:,1:]))
fig2, ax1 = plt.subplots()
ax1.set_xlabel('time (ms)')

ax1.plot(results['t'],results['V_mem'][Nrec//2]-results['V_mem'][Nrec//2][0], 'k',label='Vmem variation')
ax1.set_ylabel('Mem. Voltage (mV)')
ax2 = ax1.twinx()
ax1.legend(loc=2)

ax2.plot(results['t'], results['g_na'][Nrec//2]*1000, label='$g_{Na}$')
ax2.plot(results['t'], results['g_k'][Nrec//2]*1000, label='$g_{K}$')
ax2.plot(results['t'], results['g_l'][Nrec//2]*1000, label='$g_{l}$')
ax2.plot(results['t'], results['g_mem'][Nrec//2]*1000, label='$g_{mem}$')
ax2.set_ylabel('conductance ($mS.cm^{-2}$)')
ax2.legend()
fig2.savefig('./unitary_tests/figures/34_D.png')

fc = results['g_mem']/(2*np.pi*nrv.cm)

plt.figure(figsize=(9,7))
plt.subplot(3,1,1)
plt.plot(results['t'],results['V_mem'][Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel('Mem. Voltage (mV)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red',label='de-')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue',label='re-')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green',label='hyper-')
plt.grid()
plt.legend(title = 'polarisation')
plt.subplot(3,1,2)
plt.semilogy(results['t'],results['g_mem'][Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel('$g_m$ ($mS\cdot cm^{-2}$)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green')
plt.grid()
plt.subplot(3,1,3)
plt.semilogy(results['t'],fc[Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel('$f_{mem}$ ($Hz$)')
plt.axvspan(0.35, 0.52, alpha=0.25, color='red')
plt.axvspan(0.52, 0.9, alpha=0.25, color='blue')
plt.axvspan(0.9, 2.5, alpha=0.25, color='green')
plt.grid()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/34_E.png')

#plt.show()