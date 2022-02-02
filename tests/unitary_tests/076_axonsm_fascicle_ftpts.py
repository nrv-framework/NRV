import nrv
import numpy as np
import matplotlib.pyplot as plt
import time
import os, os.path

DIR = './unitary_tests/'


outputfile = DIR + 'figures/76_fascicle_1.json'
figfile = DIR + 'figures/76_A.png'


N = 75
t_start = time.time()
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N, M_stat="Ochoa_M")


t1 = time.time()

print('Population of '+str(N)+' axons generated in '+str(t1 - t_start)+' s')


D = 500				# diameter, in um
L = 10000 			# length, in um

fascicle_1 = nrv.fascicle(ID=76)
fascicle_1.define_length(L)
fascicle_1.define_circular_contour(D)
fascicle_1.fill_with_population(axons_diameters, axons_type, Delta=0.4)
fascicle_1.fit_circular_contour(Delta = 0.1)
fascicle_1.generate_random_NoR_position()
t2 = time.time()

print('Filled fascicle generated in '+str(t2 - t1)+' s')

my_model = 'Nerve_1_Fascicle_1_LIFE'

###########################
## extracellular context ##
###########################
test_stim = nrv.FEM_stimulation(my_model)
# ### Simulation box size
Outer_D = 5
test_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
Nerve_D = 250
Fascicle_D = 220
test_stim.reshape_nerve(Nerve_D, L)
test_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 0
z_c_1 = 0
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
#stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
test_stim.add_electrode(elec_1, stim1)

##########################
## Fascicle declaration ##
##########################
fascicle_1.attach_extracellular_stimulation(test_stim)

t3 = time.time()
print('Extracel context generated in '+str(t3 - t2)+' s')
#Footprint saving
footprints = fascicle_1.get_electrodes_footprints_on_axons()

t4 = time.time()
print('Electrod footprint generated in '+str(t4 - t3)+' s')

fascicle_1.save_fascicle_configuration(outputfile,extracel_context=True)

t5 = time.time()
print('Total time '+str(t5 - t_start)+' s')


fig, ax = plt.subplots(figsize=(6,6))
fascicle_1.plot(fig, ax, num=True)
plt.savefig(figfile)
