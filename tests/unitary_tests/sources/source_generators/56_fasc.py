import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "source_generators/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"
n_ax = 35

fascicle_1 = nrv.fascicle(diameter=25)
fascicle_1.fill(n_ax=n_ax)
print(fascicle_1.n_ax)

fig, axs = plt.subplots(1, 2)
fascicle_1.plot(axes=axs[0])
fascicle_1.save(ofname, save=True)
del fascicle_1

fascicle_2 = nrv.load_fascicle(data=ofname)
fascicle_2.plot(axes=axs[1])
del fascicle_2

plt.show()

