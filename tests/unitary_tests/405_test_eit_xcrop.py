import nrv
import eit

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    nerves_folder = "./unitary_tests/nerves/"
    res_dir  = f"./unitary_tests/results/"
    ffile = nerves_folder + "400_1max_nerve.json"
    # fname = "400_m1_nerve.json"
    l_elec = 2600 # um
    x_rec = 10250 # um

    x_min, x_max = x_rec-l_elec/2, x_rec+l_elec/2
    fasc = nrv.load_nerve(ffile).fascicles["1"]
    fig, axs = plt.subplots(3)
    fasc.plot_x(axs[0])
    del fasc

    fasc = nrv.load_nerve(ffile).fascicles["1"]

    fasc.NoR_relative_position *= 0
    fasc.plot_x(axs[2])
    deltaxs = nrv.get_MRG_parameters(fasc.axons_diameter)[5]
    for i, dx in enumerate(deltaxs):

        axs[2].plot([0, dx], [i, i])

    del fasc

    fasc1 = nrv.load_nerve(ffile).fascicles["1"]
    axs[0].set_xlim(x_min, x_max)
    deltaxs = nrv.get_MRG_parameters(fasc1.axons_diameter)[5]
    fasc1.define_length(x_max-x_min)

    l1 = fasc1.NoR_relative_position*deltaxs
    x_l = np.mod((l1 - x_min),deltaxs)
    i__ = 1
    print("x_l", x_l)
    print("l1", l1)
    print("deltaxs", deltaxs, )
    print("diameters", fasc1.axons_diameter, )
    fasc1.NoR_relative_position = x_l / deltaxs
    print("new NoR_relative_position", fasc1.NoR_relative_position)
    print(np.all(fasc1.NoR_relative_position>0), np.all(fasc1.NoR_relative_position<1))
    fasc1.plot_x(axs[1],)

    eit.plot_nerve_nor(fname=ffile, l_elec=l_elec, x_rec=x_rec,fasc_ID="1")
    plt.show()

