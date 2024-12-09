import nrv

import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":
    fname = "./unitary_tests/sources/200_fascicle_1"
    x_min, x_max = 1000.0, 3000.0


    fig, ax = plt.subplots()

    fasc = nrv.load_fascicle(fname)
    i_myel = np.argwhere(fasc.axons_type==1)[:,0]
    fasc.NoR_relative_position *= 0
    fasc.plot_x(ax)
    deltaxs = nrv.get_MRG_parameters(fasc.axons_diameter[i_myel])[5]
    for i, dx in enumerate(deltaxs):
        ax.plot([0, dx], [i_myel[i], i_myel[i]], linewidth=3)
    del fasc

    fasc = nrv.load_fascicle(fname)

    fig, axs = plt.subplots(2)
    fasc.plot_x(axs[0])
    axs[0].set_xlim(x_min, x_max)
    del fasc
    fasc1 = nrv.load_fascicle(fname)
    print(fasc1.NoR_relative_position)
    fasc1.define_length(x_max-x_min)
    l1 = fasc1.NoR_relative_position[i_myel]*deltaxs
    x_l = (l1 - x_min)%deltaxs
    fasc1.NoR_relative_position[i_myel] = x_l / deltaxs


    print(np.all(fasc1.NoR_relative_position>0), np.all(fasc1.NoR_relative_position<1))
    fasc1.plot_x(axs[1])
    
    plt.show()

