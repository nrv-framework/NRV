
import nrv
import matplotlib.pyplot as plt
import numpy as np

def stimulus_generator(X, **kwargs):
    stim = nrv.stimulus()
    start = X[0]
    I_cathod = X[1]
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim.biphasic_pulse(start,  I_cathod, T_cathod, I_anod, T_inter)
    return stim

test_stim_CM = nrv.stimulus_CM(stim_gen=stimulus_generator)


static_context = "./unitary_tests/sources/202_axon.json"
X = np.array([
    [1, 1],
    [1, 20],
    [1, 40],
    [1, 60],
    [1, 80],
    [1, 100],
])

results = []
# simulate the axon
plt.figure(1)
plt.figure(2)
for i, x in enumerate(X):
    print(x)
    ax = test_stim_CM(x, static_context)
    results = ax(t_sim=5)
    del ax


    plt.figure(1)
    plt.plot(results['extra_stim']['stimuli'][0]['t'], results['extra_stim']['stimuli'][0]['s'], '.')
    plt.figure(2)
    plt.subplot(2,3,i+1)
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')


cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.figure(1)
plt.savefig('./unitary_tests/figures/202_A.png')
plt.figure(2)
plt.savefig('./unitary_tests/figures/202_B.png')
#plt.show()