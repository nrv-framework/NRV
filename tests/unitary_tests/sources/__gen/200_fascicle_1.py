import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "__gen/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"
n_ax = 10


l_f = 10_000
d_f = 66
Nerve_D = 250

##########################
## Fascicle declaration ##
##########################
fascicle_1 = nrv.fascicle(d_f)
fascicle_1.fill(n_ax=n_ax)
fascicle_1.define_length(l_f)

###########################
## extracellular context ##
###########################
test_stim = nrv.FEM_stimulation()
# ### Simulation box size
Outer_D = 5
test_stim.reshape_outerBox(Outer_D)
test_stim.reshape_nerve(Nerve_D, l_f)
test_stim.reshape_fascicle(fascicle_1.geom)
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 50
z_c_1 = 50
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
test_stim.add_electrode(elec_1, stim1)



# extra cellular stimulation
fascicle_1.attach_extracellular_stimulation(test_stim)
# simulation
fascicle_1.compute_electrodes_footprints()
fascicle_1.loaded_footprints = True

fig, ax = plt.subplots()

fascicle_1.plot(axes=ax)

print("generated")
fascicle_1.save(ofname, save=True, extracel_context=True)
print(f"saved to {ofname}")

del fascicle_1

plt.show()
