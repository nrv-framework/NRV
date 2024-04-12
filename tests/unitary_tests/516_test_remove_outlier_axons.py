import nrv
import numpy as np
import matplotlib.pyplot as plt

test_axons, axons_type, M_diam_list, U_diam_list, _, _ = nrv.load_axon_population('./unitary_tests/sources/52_test.pop') 

y_axons, z_axons = nrv.axon_packer(test_axons,delta = 10)#, monitor = False, monitoring_Folder='./unitary_tests/figures/53_test_packer/',y_gc = 100, z_gc = 200,v_att = 0.01, v_rep = 0.1)

fig, ax = plt.subplots(figsize=(8, 8))
size_plot = 3*np.max(np.abs(y_axons))

pop_diam = nrv.get_circular_contour(test_axons,y_axons,z_axons,delta = 5)

nrv.plot_population(test_axons, y_axons, z_axons,ax=ax,size = size_plot,axon_type=axons_type)
ax.add_patch(plt.Circle((0, 0), pop_diam/4, color='k',fill=False))

fig.savefig('./unitary_tests/figures/516_base.png')

test_axons,y_axons,z_axons,axons_type  = nrv.remove_outlier_axons(test_axons, y_axons, z_axons, axons_type, pop_diam/2)

fig, ax = plt.subplots(figsize=(8, 8))
size_plot = 3*np.max(np.abs(y_axons))
nrv.plot_population(test_axons, y_axons, z_axons,ax=ax,size = size_plot,axon_type=axons_type)
ax.add_patch(plt.Circle((0, 0), pop_diam/4, color='k',fill=False))
fig.savefig('./unitary_tests/figures/516_outliers_removed.png')

#plt.show()