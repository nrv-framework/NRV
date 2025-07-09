import nrv
import numpy as np
import matplotlib.pyplot as plt
import time


if __name__ == "__main__":
    #todo: test with unymelinated
    geom = nrv.create_cshape(diameter=100)
    pop = nrv.axon_population(geometry=geom)
    n_ax = 200      #size of the axon population
    pop.create_population(n_ax=n_ax, percent_unmyel=0.0, M_stat="Ochoa_M", U_stat="Ochoa_U")

    start = time.perf_counter()
    pop.place_population(method="packing", n_iter = 25_001,delta = 10) #, monitor = True, monitoring_Folder='./unitary_tests/figures/053_test_packer/',y_gc = 100, z_gc = 200,v_att = 0.01, v_rep = 0.1)
    t = time.perf_counter() - start
    print('Packing performed in '+str(t)+' s')


    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(pop["y"]))

    pop.plot(axes=ax)



    # plt.show()