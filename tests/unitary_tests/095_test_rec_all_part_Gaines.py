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

## Test1

Nseg=3
y = 0
z = 0
d = 6
L = nrv.get_length_from_nodes(d, 7)

axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all', Nseg_per_sec=Nseg-1,model='Gaines_motor')
#print(axon1.rec_position_list)
total = 0
for positions in axon1.rec_position_list:
	total += len(positions)
#print(total)
print(total == len(axon1.x_rec))

t_start = 1
duration = 0.1
amplitude = 2
axon1.insert_I_Clamp_node(1, t_start, duration, amplitude)

t_sim=5
results = axon1.simulate(t_sim=t_sim, record_V_mem=False, record_particles=True)

C = len(axon1.x_rec)//2
seq_types = axon1.axon_path_type
seq_index = axon1.axon_path_index

del axon1



plt.figure(figsize=(14, 10))
plt.subplot(2,2,1)
map = plt.pcolormesh(results['t'], results['x_rec'], results['q'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('q (mV)')

plt.subplot(2,2,2)
map = plt.pcolormesh(results['t'], results['x_rec'], results['mp'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('mp(mV)')

plt.subplot(2,2,3)
map = plt.pcolormesh(results['t'], results['x_rec'], results['s'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('s (mV)')
plt.savefig('./unitary_tests/figures/95_A.png')

plt.subplot(2,2,4)
map = plt.pcolormesh(results['t'], results['x_rec'], results['n'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('n (mV)')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/95_A.png')


plt.figure(figsize=(15, 8))

for i in range(8):
    x = C+i
    plt.subplot(2,4,i+1)
    plt.plot(results['t'],results['m'][x],label='m')
    plt.plot(results['t'],results['mp'][x],label='mp')
    plt.plot(results['t'],results['h'][x],label='h')
    plt.plot(results['t'],results['n'][x],label='n')
    plt.plot(results['t'],results['s'][x],label='s')
    plt.plot(results['t'],results['q'][x],label='q')
    print(seq_types[(x-1)//Nseg])
    plt.title(seq_types[(x-1)//Nseg]+''+str(seq_index[(x-1)//Nseg]))
    plt.legend()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/95_B.png')


plt.figure(figsize=(15, 8))
seq = [0, 1, 2, 3, 11, 10, 9, 8]
for i in range(8):
    x = C+seq[i]*2
    plt.subplot(2,4,i+1)
    plt.plot(results['t'],results['m'][x],label='m')
    plt.plot(results['t'],results['mp'][x],label='mp')
    plt.plot(results['t'],results['h'][x],label='h')
    plt.plot(results['t'],results['n'][x],label='n')
    plt.plot(results['t'],results['s'][x],label='s')
    plt.plot(results['t'],results['q'][x],label='q')
    print(seq_types[(x-1)//Nseg])
    plt.title(seq_types[(x-1)//Nseg]+''+str(seq_index[(x-1)//Nseg]))
    plt.legend()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/95_C.png')

#plt.show()
