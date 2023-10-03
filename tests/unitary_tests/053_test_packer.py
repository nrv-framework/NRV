import nrv
import numpy as np
import matplotlib.pyplot as plt
import time
import os

if not os.path.exists('./unitary_tests/figures/53_test_packer'):
	os.makedirs('./unitary_tests/figures/53_test_packer')

#nrv.verbose = False

#test_axons = np.ones(95)

test_axons, axons_type, M_diam_list, U_diam_list = nrv.load_axon_population('./unitary_tests/sources/52_test.pop')

start = time.time()
y_axons, z_axons, iteration, FVF, probed_iter = nrv.axon_packer(test_axons,Delta = 0.5, monitor = False, monitoring_Folder='./unitary_tests/figures/53_test_packer/',y_gc = 100, z_gc = 200,v_att = 0.01, v_rep = 0.1)
t = time.time() - start
print('Packing performed in '+str(t)+' s')

nrv.save_placed_axon_population('./unitary_tests/sources/53_test.ppop',test_axons, axons_type, y_axons, z_axons)

# plot the Fiber Volme Fraction
plt.figure()
plt.plot(probed_iter,FVF)
plt.savefig('./unitary_tests/figures/53_A.png')


# plot the final results, with distinction between un- and myelinated axons
myelinated_mask = np.argwhere(axons_type == 1)
y_myelinated = y_axons[myelinated_mask]
z_myelinated = z_axons[myelinated_mask]
M_circles = []
for k in range(len(y_myelinated)):
		M_circles.append(plt.Circle((y_myelinated[k], z_myelinated[k]), M_diam_list[k]/2, color='r',fill=True))


unmyelinated_mask = np.argwhere(axons_type == 0) 
y_unmyelinated = y_axons[unmyelinated_mask]
z_unmyelinated = z_axons[unmyelinated_mask]
U_circles = []
for k in range(len(y_unmyelinated)):
		U_circles.append(plt.Circle((y_unmyelinated[k], z_unmyelinated[k]), U_diam_list[k]/2, color='b',fill=True))

fig, ax = plt.subplots(figsize=(8,8)) 
for circle in M_circles:
		ax.add_patch(circle)
for circle in U_circles:
		ax.add_patch(circle)
plt.xlim(min(y_axons)-14,max(y_axons)+14)
plt.ylim(min(z_axons)-14,max(z_axons)+14)
plt.savefig('./unitary_tests/figures/53_B.png')
plt.savefig('./unitary_tests/figures/53_B.pdf')
#plt.show()
