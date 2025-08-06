import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "__gen/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"


outer_d = 5     # mm
nerve_d = 105  # um
nerve_l = 5010  # um
fasc1_d = 70   # um
fasc1_y = 0     # um
fasc1_z = 0     # um

t_sim, dt = 20, 0.001    # ms
percent_unmyel = 1
unmyelinated_nseg = 1000
axons_data={
    "diameters":[1.001],
    "types":[0],
    "y":[0],
    "z":[0],
}

nerve_1 = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d, t_sim=t_sim, dt=dt, postproc_label="sample_keys", record_g_mem=True)


fascicle_1 = nrv.fascicle(diameter=fasc1_d, ID=1, unmyelinated_nseg=unmyelinated_nseg)
fascicle_1.fill(data=axons_data)
nerve_1.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

nerve_1.save(save=True, fname=ofname)


fig, ax = plt.subplots(figsize=(6, 6))
nerve_1.plot(ax)
fig, ax = plt.subplots(figsize=(6, 6))
nerve_1.fascicles[1].plot_x(ax)
ax.grid()

plt.show()