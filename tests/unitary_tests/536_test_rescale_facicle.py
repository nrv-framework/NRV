import nrv

import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
sfile = "./unitary_tests/sources/200_fascicle_1"
if __name__ == "__main__":
    x_min, x_max = 1000.0, 3000.0


    fig, ax = plt.subplots()

    fasc = nrv.load_fascicle(sfile)
    i_myel = np.argwhere(fasc.axons["types"]==1)[:,0]
    fasc.axons.generate_NoR_position_from_data(np.zeros(len(fasc.axons)))
    fasc.plot_x(ax)
    deltaxs = nrv.get_MRG_parameters(fasc.axons["diameters"].to_numpy()[i_myel])[5]
    for i, dx in enumerate(deltaxs):
        ax.plot([0, dx], [i_myel[i], i_myel[i]], linewidth=3)
    del fasc
    fig.savefig(figdir+"A.png")
    
    fasc = nrv.load_fascicle(sfile)
    ax.set_xlim(0,1000)
    fig, axs = plt.subplots(2)
    fasc.plot_x(axs[0])
    axs[0].set_xlim(x_min, x_max)
    del fasc
    fasc1 = nrv.load_fascicle(sfile)
    fasc1.define_length(x_max-x_min)
    l1 = fasc1.axons["node_shift"][i_myel]*deltaxs
    x_l = (l1 - x_min)%deltaxs
    fasc1.axons["node_shift"][i_myel] = x_l / deltaxs


    print(np.all(fasc1.axons["node_shift"]>0), np.all(fasc1.axons["node_shift"]<1))
    fasc1.plot_x(axs[1])
    fig.savefig(figdir+"B.png")
    plt.show()

