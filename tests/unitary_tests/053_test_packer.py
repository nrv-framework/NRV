import nrv
import numpy as np
import matplotlib.pyplot as plt
import time
import os


if __name__ == "__main__":
    #if not os.path.exists('./unitary_tests/figures/053_test_packer'):
    #	os.makedirs('./unitary_tests/figures/053_test_packer')

    #nrv.verbose = False

    #test_axons = np.ones(95)

    test_axons, axons_type, M_diam_list, U_diam_list, _, _ = nrv.load_axon_population('./unitary_tests/sources/52_test.pop') 

    start = time.perf_counter()
    y_axons, z_axons = nrv.axon_packer(test_axons, n_iter = 32001,delta = 0.5) #, monitor = True, monitoring_Folder='./unitary_tests/figures/053_test_packer/',y_gc = 100, z_gc = 200,v_att = 0.01, v_rep = 0.1)
    t = time.perf_counter() - start
    print('Packing performed in '+str(t)+' s')

    nrv.save_axon_population('./unitary_tests/results/53_test.ppop',test_axons, axons_type, y_axons, z_axons)

    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(y_axons))

    nrv.plot_population(test_axons, y_axons, z_axons,ax=ax,size = size_plot,axon_type=axons_type)
    fig.savefig('./unitary_tests/figures/53_B.png')
