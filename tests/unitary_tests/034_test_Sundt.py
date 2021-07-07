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
axon1 = nrv.unmyelinated(y,z,d,L,model='Sundt',dt=0.001,Nrec=100)
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

#plt.show()