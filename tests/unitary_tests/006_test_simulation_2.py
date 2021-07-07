import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 1
L = 5000

# test 1: 100 recording over more than 250 segments, 1 section
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100)
results = axon1.simulate(t_sim=2)
del axon1
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_A.png')

# test 2:all recording over more than 250 segments, 1 section
axon2 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=0)
results = axon2.simulate(t_sim=2)
del axon2
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_B.png')

# test 3:all recording over more than 250 segments, 1 section
axon3 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=3)
results = axon3.simulate(t_sim=2)
del axon3
plt.figure()
plt.plot(results['t'], results['V_mem'][0],color='b')
plt.plot(results['t'], results['V_mem'][1],color='r')
plt.plot(results['t'], results['V_mem'][2],color='k')
plt.xlabel('time (ms)')
plt.ylabel('voltage (mV)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_C.png')

# test 4:all recording over more than 250 segments, 3 sections
axon4 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100,Nsec=3)
results = axon4.simulate(t_sim=2)
del axon4
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_D.png')

# test 5:all recording over more than 250 segments, 3 sections
axon5 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=0,Nsec=3)
results = axon5.simulate(t_sim=2)
del axon5
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_E.png')

# test 6:all recording over more than 250 segments, 3 sections
axon6 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=3,Nsec=3)
results = axon6.simulate(t_sim=2)
del axon6
plt.figure()
plt.plot(results['t'], results['V_mem'][0],color='b')
plt.plot(results['t'], results['V_mem'][1],color='r')
plt.plot(results['t'], results['V_mem'][2],color='k')
plt.xlabel('time (ms)')
plt.ylabel('voltage (mV)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/06_F.png')