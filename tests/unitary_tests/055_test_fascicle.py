import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # parameters for the test fascicle
    d = 25                # diameter, in um
    L = 10000             # length, in um

    fascicle_1 = nrv.fascicle()
    fascicle_1.define_length(L)
    fascicle_1.define_circular_contour(d)
    fascicle_1.fill()

    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True)
    plt.savefig('./unitary_tests/figures/55.png')
    #plt.show()


