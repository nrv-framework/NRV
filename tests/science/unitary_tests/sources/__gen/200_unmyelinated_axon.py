import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "__gen/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"

y = 50
z = 0
d = 1
l_a = 5000

u_ax = nrv.unmyelinated(y=y, z=z, d=d, L=l_a)


###########################
## extracellular context ##
###########################
test_stim = nrv.stimulation()
# ### Simulation box size
Outer_D = 5
# test_stim.reshape_fascicle(nrv.create_cshape(diameter=400))
##### electrode and stimulus definition
y_c_1 = 100
z_c_1 = 0
x_1_offset = l_a/2
elec_1 = nrv.point_source_electrode(x_1_offset, y_c_1, z_c_1)
# stimulus def
start = 1
I_cathod = 100
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
test_stim.add_electrode(elec_1, stim1)

u_ax.attach_extracellular_stimulation(test_stim)


print("generated")
u_ax.save(fname=ofname, save=True, extracel_context=True)
print(f"saved to {ofname}")

res = u_ax.simulate(t_sim=5)
del u_ax

fig, ax = plt.subplots()
res.plot_x_t(ax, "V_mem")
plt.show()
