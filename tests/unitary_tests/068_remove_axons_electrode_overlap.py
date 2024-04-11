import nrv
import numpy as np
import matplotlib.pyplot as plt
import time


if nrv.MCH.do_master_only_work():
	start_time = time.time()

L = 10000 			# length, in um
fascicle_1 = nrv.fascicle()
fascicle_1.define_length(L)
fascicle_1.load_fascicle_configuration('./unitary_tests/sources/56_fasc.json')

# electrode def
x_elec = L/2				# electrode x position, in [um]
y_elec = 0				# electrode y position, in [um]
z_elec = 5					# electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

fascicle_1.remove_axons_electrode_overlap(E1)

fig, ax = plt.subplots(figsize=(8,8))
fascicle_1.plot(ax)
plt.savefig('./unitary_tests/figures/68_A.png')

##### LIFE electrode
D_1 = 5
length_1 = 1000
y_c_1 = 0
z_c_1 = -5
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)

fascicle_1.remove_axons_electrode_overlap(elec_1)

fig2, ax2 = plt.subplots(figsize=(8,8))
fascicle_1.plot(ax2)
plt.savefig('./unitary_tests/figures/68_B.png')
#plt.show()