import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "__gen/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"

y = 50
z = 0
d = 10
l_a = 10_000

m_ax = nrv.myelinated(y=y, z=z, d=d, L=l_a)


###########################
## extracellular context ##
###########################
test_stim = nrv.FEM_stimulation()
# ### Simulation box size
Outer_D = 5
test_stim.reshape_outerBox(Outer_D)
test_stim.reshape_nerve(Nerve_D=500, Length=l_a)
# test_stim.reshape_fascicle(nrv.create_cshape(diameter=400))
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 50
z_c_1 = 50
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
stim1 = nrv.stimulus()
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
test_stim.add_electrode(elec_1, stim1)

m_ax.attach_extracellular_stimulation(test_stim)

m_ax.get_electrodes_footprints_on_axon()

print("generated")
m_ax.save(fname=ofname, save=True, extracel_context=True)
print(f"saved to {ofname}")

res = m_ax.simulate(t_sim=5)
del m_ax

fig, ax = plt.subplots()
res.plot_x_t(ax, "V_mem")
plt.show()
