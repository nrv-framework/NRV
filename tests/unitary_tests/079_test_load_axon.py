import nrv
import matplotlib.pyplot as plt


# axon def

axon1 = nrv.load_any('./unitary_tests/sources/79_axon.json', extracel_context=True)

# stimulus def
start = 1
I_cathod = 10
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
axon1.change_stimulus_from_elecrode(0, stim1)




# simulate the axon
results = axon1.simulate(t_sim=5)
del axon1


plt.figure()
for k in range(len(results['node_index'])):
    index = results['node_index'][k]
    plt.plot(results['t'], results['V_mem'][index]+k*100, color = 'k')
plt.yticks([])
plt.xlim(0.9,2)
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/79_A.png')

#plt.show()
