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

Nseg=2
y = 0
z = 0
d = 6
L = nrv.get_length_from_nodes(d, 3)

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
results = axon1.simulate(t_sim=t_sim, record_V_mem=False, record_g_mem=True, record_g_ions=True)

C = len(axon1.x_rec)//2
seq_types = axon1.axon_path_type
seq_index = axon1.axon_path_index
print(C)

print(len(axon1.x_rec), 2*len(axon1.axon_path_type), len(axon1.axon_path_index), len(axon1.rec_position_list))
print(axon1.axon_path_type)
print(axon1.axon_path_index)
print(axon1.rec_position_list)
del axon1



plt.figure(figsize=(14, 10))
plt.subplot(2,2,1)
map = plt.pcolormesh(results['t'], results['x_rec'], results['g_mem'] ,shading='auto')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('g membrane (mV)')
plt.tight_layout()


plt.subplot(2,2,2)
map = plt.pcolormesh(results['t'], results['x_rec'], results['g_nap'] ,shading='auto')
cbar = plt.colorbar(map)
cbar.set_label('g_nap(mV)')

plt.subplot(2,2,3)
map = plt.pcolormesh(results['t'], results['x_rec'], results['g_k'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('g_k (mV)')

plt.subplot(2,2,4)
map = plt.pcolormesh(results['t'], results['x_rec'], results['g_q'] ,shading='auto')
plt.xlabel('time (ms)')

cbar = plt.colorbar(map)
cbar.set_label('g_q (mV)')
plt.savefig('./unitary_tests/figures/97_A.png')

plt.figure(figsize=(15, 8))

for i in range(8):
    x = C+i
    plt.subplot(2,4,i+1)
    plt.plot(results['t'],results['g_na'][x],label='g_na')
    plt.plot(results['t'],results['g_nap'][x],label='g_nap')
    plt.plot(results['t'],results['g_k'][x],label='g_k')
    plt.plot(results['t'],results['g_kf'][x],label='g_kf')
    plt.plot(results['t'],results['g_l'][x],label='g_l')
    plt.plot(results['t'],results['g_q'][x],label='g_q')

    plt.plot(results['t'],results['g_mem'][x],label='g_mem', color='k')
    print(seq_types[(x-1)//Nseg])
    plt.title(seq_types[(x-1)//Nseg]+' '+str(seq_index[(x-1)//Nseg]))
    plt.legend()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/97_B.png')


plt.figure(figsize=(15, 8))
seq = [0, 1, 2, 3, 11, 10, 9, 8]
for i in range(8):
    x = C+seq[i]*2
    plt.subplot(2,4,i+1)
    plt.plot(results['t'],results['g_na'][x],label='g_na')
    plt.plot(results['t'],results['g_nap'][x],label='g_nap')
    plt.plot(results['t'],results['g_k'][x],label='g_k')
    plt.plot(results['t'],results['g_kf'][x],label='g_kf')
    plt.plot(results['t'],results['g_l'][x],label='g_l')
    plt.plot(results['t'],results['g_q'][x],label='g_q')

    plt.plot(results['t'],results['g_mem'][x],label='g_mem', color='k')
    print(seq_types[(x-1)//Nseg])
    plt.title(seq_types[(x-1)//Nseg]+' '+str(seq_index[(x-1)//Nseg]))
    plt.legend()
plt.tight_layout()
plt.savefig('./unitary_tests/figures/97_C.png')

#plt.show()
