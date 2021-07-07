import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

N = 100
start = time.time()
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N)
t = time.time() - start

print('Population of '+str(N)+' axons generated in '+str(t)+' s')

nrv.save_axon_population('./unitary_tests/figures/52_test.pop',axons_diameters, axons_type)

axons_diameters_2, axons_type_2, M_diam_list_2, U_diam_list_2 = nrv.load_axon_population('./unitary_tests/figures/52_test.pop')

plt.figure()
plt.hist(M_diam_list_2,bins = 12,color = 'blue',label='Myelinated')
plt.hist(U_diam_list_2,bins = 10,color = 'red',label='Unmyelinated')
plt.savefig('./unitary_tests/figures/52_A.png')
#plt.show()