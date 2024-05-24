import nrv
import matplotlib.pyplot as plt
import numpy as np

y = 0
z = 0
d = 1
L = 5000
model = 'Schild_94'
t_start = 1
duration = 0.5
amplitude = 1
Nrec = 100

# test 1: 1 section stim in middle
axon1 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
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
plt.savefig('./unitary_tests/figures/36_A.png')

plt.figure()
plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
plt.xlabel('time (ms)')
plt.ylabel('V membrane (mV)')
plt.legend()
plt.savefig('./unitary_tests/figures/36_B.png')

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
axs[2].plot(results['t'],results['l_naf'][25],label='l_naf')
axs[2].plot(results['t'],results['m_nas'][25],label='m_nas')
axs[2].plot(results['t'],results['h_nas'][25],label='h_nas')
plt.savefig('./unitary_tests/figures/36_C.png')
del results

# test 2: gmem for stim in left side
cmshild = 1.326291192
gnabar_hh = 0.120
gkbar_hh = 0.036
gl_hh = 0.0003

axon2 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
cm = axon2.get_membrane_capacitance()
axon2.insert_I_Clamp(0, t_start, duration, amplitude)
results = axon2.simulate(t_sim=10, record_particles=True, record_g_ions=True, record_g_mem=True)
print(axon2.T == 37)

print(np.allclose(cm, cmshild))
del axon2

#### Check results
fc2 = nrv.compute_f_mem(results)
fig2, ax1 = plt.subplots()
ax1.set_xlabel('time (ms)')

ax1.plot(results['t'],results['V_mem'][Nrec//2]-results['V_mem'][Nrec//2][0], 'k',label='Vmem variation')
ax1.set_ylabel('Mem. Voltage (mV)')
ax2 = ax1.twinx()
ax1.legend(loc=2)

ax2.plot(results['t'], results['g_naf'][Nrec//2]*1000, label=r'$g_{naf}$')
ax2.plot(results['t'], results['g_nas'][Nrec//2]*1000, label=r'$g_{nas}$')
ax2.plot(results['t'], results['g_kd'][Nrec//2]*1000, label=r'$g_{kd}$')
ax2.plot(results['t'], results['g_ka'][Nrec//2]*1000, label=r'$g_{ka}$')
ax2.plot(results['t'], results['g_kds'][Nrec//2]*1000, label=r'$g_{kds}$')
ax2.plot(results['t'], results['g_kca'][Nrec//2]*1000, label=r'$g_{kca}$')
ax2.plot(results['t'], results['g_can'][Nrec//2]*1000, label=r'$g_{can}$')
ax2.plot(results['t'], results['g_cat'][Nrec//2]*1000, label=r'$g_{cat}$')
ax2.plot(results['t'], results['g_mem'][Nrec//2]*1000, label=r'$g_{mem}$')
ax2.set_ylabel(r'conductance ($mS.cm^{-2}$)')
ax2.legend()
fig2.savefig('./unitary_tests/figures/36_D.png')

plt.figure(figsize=(9,7))
plt.subplot(3,1,1)
plt.plot(results['t'],results['V_mem'][Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel('Mem. Voltage (mV)')
plt.grid()
plt.legend(title = 'polarisation')
plt.subplot(3,1,2)
plt.semilogy(results['t'],results['g_mem'][Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel(r'$g_m$ ($mS\cdot cm^{-2}$)')
plt.grid()
plt.subplot(3,1,3)
plt.semilogy(results['t'],results['f_mem'][Nrec//2])
plt.xlabel('time (ms)')
plt.ylabel(r'$f_{mem}$ ($Hz$)')
plt.grid()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/36_E.png')

#plt.show()