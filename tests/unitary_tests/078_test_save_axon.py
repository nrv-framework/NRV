from sqlite3 import OptimizedUnicode
import nrv
import matplotlib.pyplot as plt


# axon def
y = 0						# axon y position, in [um]
z = 0						# axon z position, in [um]
d = 16						# axon diameter, in [um]
L=nrv.get_length_from_nodes(d,20)                # get length for 20 nodes of ranvier

dt = 0.001
f_dlambda = 100


endoneurium = nrv.load_material('endoneurium_bhadra')

my_model = 'Nerve_1_Fascicle_1_LIFE'
extra_stim = nrv.FEM_stimulation(my_model) #, endo_mat=endoneurium)
### Simulation box size
Outer_D = 5     # in in [mm]
extra_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
Nerve_D = 250   # in [um]
Fascicle_D = 220# in [um]
extra_stim.reshape_nerve(Nerve_D, L)
extra_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition

# electrode def
z_elec = 0				# electrode x position, in [um]
y_elec = 500				# electrode y position, in [um]
model = 'MRG'

axon1 = nrv.myelinated(y,z,d,L,rec='all',dt=dt,freq=f_dlambda,model=model)
x_elec = axon1.x_nodes[10]	# electrode y position, in [um]
# first electrode
D_1 = 25
length_1 = 1000
y_c_1 = 50
z_c_1 = 50
x_1_offset = x_elec - (length_1/2)
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)

start = 1
I_cathod = 10
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

# extracellular stimulation setup
extra_stim.add_electrode(elec_1, stim1)

axon1.attach_extracellular_stimulation(extra_stim)

footprints = axon1.get_electrodes_footprints_on_axon()

axon1.save_axon(save=True, fname="./unitary_tests/figures/78_axon.json", extracel_context=True)
# simulate the axon
results = axon1.simulate(t_sim=5,footprints=footprints)
del axon1

plt.figure()
for k in range(len(results['node_index'])):
	index = results['node_index'][k]
	plt.plot(results['t'], results['V_mem'][index]+k*100, color = 'k')
plt.yticks([])
plt.xlim(0.9,2)
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/78_A.png')

#plt.show()
