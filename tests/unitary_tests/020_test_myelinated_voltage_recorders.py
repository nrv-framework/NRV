import nrv
import matplotlib.pyplot as plt
# Note : every print should be true

y = 0
z = 0
d = 10
L = 5000


axon1 = nrv.myelinated(y,z,d,L,dt=0.001,rec='all')
#print(axon1.rec_position_list)
total = 0
for positions in axon1.rec_position_list:
	total += len(positions)
#print(total)
print(total == len(axon1.x_rec))

results = axon1.simulate(t_sim=2)
del axon1
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/20_A.png')

# test 2
axon2 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes')
results2 = axon2.simulate(t_sim=2)
del axon2

plt.figure()
for k in range(len(results2['x_rec'])):
	plt.plot(results2['t'],results2['V_mem'][k]+k*100, color='k')
plt.yticks([])
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/20_B.png')

#plt.show()