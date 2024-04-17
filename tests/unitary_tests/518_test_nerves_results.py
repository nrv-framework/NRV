import nrv
import numpy as np
import matplotlib.pyplot as plt



nerve_results = nrv.load_any("./unitary_tests/sources/518_nerve_results.json")
fig, ax = plt.subplots(figsize=(8, 8))
nerve_results.plot_recruited_fibers(ax)

nerve_results = nrv.load_any("./unitary_tests/sources/518_nerve_results2.json")
fig, ax = plt.subplots(figsize=(8, 8))
nerve_results.plot_recruited_fibers(ax)

plt.show()
exit()
fas1 = nerve_results.get_fascicle_results(ID = 1)
fas1.get_recruited_axons()
fig, ax = plt.subplots(figsize=(8, 8))
fas1.plot_recruited_fibers(ax)

fas2 = nerve_results.get_fascicle_results(ID = 2)
fig, ax = plt.subplots(figsize=(8, 8))
fas2.plot_recruited_fibers(ax)


#ax.set_ylim(-200,200)
#ax.set_xlim(-200,200)
plt.show()
#print(nerve_results.fascicle1)
