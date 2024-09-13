import nrv
import matplotlib.pyplot as plt

import nrv
import numpy as np
import matplotlib.pyplot as plt

expected_seq = ['node', 'MYSA', 'FLUT', 'STIN', 'STIN', 'STIN', 'STIN', 'STIN', 'FLUT', 'MYSA', 'node', 'MYSA', 'FLUT']
i_plot, j_plot = (4,7)
N_plot = i_plot * j_plot

## Test1
# Ax pty
Nseg=1
y = 0
z = 0
d = 10
L = nrv.get_length_from_nodes(d, 10)
t_sim = 10
node_shift = 0

# Iclamp pty
t_start = 1
duration = 0.1
amplitude = 2

axon_mrg = nrv.myelinated(y,z,d,L,dt=0.005,rec='all', Nseg_per_sec=Nseg,model='MRG', node_shift=node_shift)
axon_mrg.insert_I_Clamp_node(1, t_start, duration, amplitude)
res_mrg = axon_mrg.simulate(t_sim=t_sim, record_g_mem=True, record_g_ions=True)
del axon_mrg

axon_motor = nrv.myelinated(y,z,d,L,dt=0.005,rec='all', Nseg_per_sec=Nseg,model='Gaines_motor', node_shift=node_shift)
axon_motor.insert_I_Clamp_node(1, t_start, duration, amplitude)
res_motor = axon_motor.simulate(t_sim=t_sim, record_g_mem=True, record_g_ions=True)
del axon_motor

axon_sensory = nrv.myelinated(y,z,d,L,dt=0.005,rec='all', Nseg_per_sec=Nseg,model='Gaines_sensory', node_shift=node_shift)
axon_sensory.insert_I_Clamp_node(1, t_start, duration, amplitude)
res_sensory = axon_sensory.simulate(t_sim=t_sim, record_g_mem=True, record_g_ions=True)
del axon_sensory

res_mrg.compute_f_mem()
res_motor.compute_f_mem()
res_sensory.compute_f_mem()
res_mrg.get_myelin_properties()
res_motor.get_myelin_properties()
res_sensory.get_myelin_properties()

seq_types_mrg = res_mrg['axon_path_type']
seq_types_motor = res_motor['axon_path_type']
seq_types_sensory = res_sensory['axon_path_type']
print(seq_types_motor[:11], res_motor['Nsec'])

C = res_motor.find_central_index()
print(C)


fig1 = plt.figure(1, figsize=(20, 8))
fig2 = plt.figure(2, figsize=(20, 8))
fig3 = plt.figure(3, figsize=(20, 8))
for i in range(N_plot):
    x =  i + C

    plt.figure(1)
    plt.subplot(i_plot, j_plot,i+1)
    plt.plot(res_mrg['t'],res_mrg['V_mem'][x],label='MRG')
    plt.plot(res_motor['t'],res_motor['V_mem'][x],label='motor')
    plt.plot(res_sensory['t'],res_sensory['V_mem'][x],label='sensory')
    plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))

    plt.figure(2)
    ax = plt.subplot(i_plot, j_plot,i+1)
    plt.plot(res_mrg['t'],res_mrg['g_mem'][x],label='MRG')
    plt.plot(res_motor['t'],res_motor['g_mem'][x],label='motor')
    plt.plot(res_sensory['t'],res_sensory['g_mem'][x],label='sensory')
    plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))
    ax.ticklabel_format(scilimits=[-1, 1], useMathText=True)

    plt.figure(3)
    ax = plt.subplot(i_plot, j_plot,i+1)
    plt.plot(res_mrg['t'],res_mrg['f_mem'][x],label='MRG')
    plt.plot(res_motor['t'],res_motor['f_mem'][x],label='motor')
    plt.plot(res_sensory['t'],res_sensory['f_mem'][x],label='sensory')
    plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))
    ax.ticklabel_format(scilimits=[-1, 1], useMathText=True)

plt.figure(1)
fig1.legend(['MRG', 'motor', 'sensory'])
fig1.tight_layout()
fig1.savefig('./unitary_tests/figures/98_A.png')

plt.figure(2)
fig2.legend(['MRG', 'motor', 'sensory'])
fig2.tight_layout()
fig2.savefig('./unitary_tests/figures/98_B.png')

plt.figure(3)
fig3.legend(['MRG', 'motor', 'sensory'])
fig3.tight_layout()
fig3.savefig('./unitary_tests/figures/98_C.png')
plt.close()

plt.figure(4, figsize=(10,8))
ax = plt.subplot(3, 1, 1)
plt.plot(res_mrg['x_rec'], res_mrg['g_mye'])
plt.plot(res_motor['x_rec'], res_motor['g_mye'])
plt.plot(res_sensory['x_rec'], res_sensory['g_mye'])
plt.yscale('log')
plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))
ax = plt.subplot(3, 1, 2)
plt.plot(res_mrg['x_rec'], res_mrg['c_mye'])
plt.plot(res_motor['x_rec'], res_motor['c_mye'])
plt.plot(res_sensory['x_rec'], res_sensory['c_mye'])
plt.yscale('log')
plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))
ax = plt.subplot(3, 1, 3)
plt.plot(res_mrg['x_rec'], res_mrg['f_mye'])
plt.plot(res_motor['x_rec'], res_motor['f_mye'])
plt.plot(res_sensory['x_rec'], res_sensory['f_mye'])
plt.yscale('log')
plt.title(str(x)+": "+res_motor.get_index_myelinated_sequence(x))
plt.savefig('./unitary_tests/figures/98_D.png')
plt.legend(['MRG', 'motor', 'sensory'])
#plt.show()
