import nrv
import matplotlib.pyplot as plt


###########################
## extracellular context ##
###########################
nrv.parameters.set_nrv_verbosity(2)
test_stim = nrv.FEM_stimulation(comsol=False)
### Simulation box size
Outer_D = 5
test_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
L = 10000
Nerve_D = 250
Fascicle_D = 220
test_stim.reshape_nerve(Nerve_D, L)
test_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 50
z_c_1 = 50
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
test_stim.add_electrode(elec_1, stim1)

##########
## axon ##
##########
# axon def
y = 100						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 6.5						# axon diameter, in [um]
axon1 = nrv.myelinated(y,z,d,L,rec='all')
axon1.attach_extracellular_stimulation(test_stim)

axon1.get_electrodes_footprints_on_axon()
#print(axon1.extra_stim.electrodes[0].footprint)
axon1.save(save=True, fname="./unitary_tests/figures/503_axon.json", extracel_context=True)
# simulate the axon
results = axon1.simulate(t_sim=5, loaded_footprints=True)
del axon1

plt.figure()
for k in range(len(results['node_index'])):
    index = results['node_index'][k]
    plt.plot(results['t'], results['V_mem'][index]+k*100, color = 'k')
plt.yticks([])
plt.xlim(0.9,2)
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/503_A.png')

#plt.show()
