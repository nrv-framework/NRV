import nrv
import numpy as np
import matplotlib.pyplot as plt

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def create_fascicle_default():

    fascicle_1 = nrv.fascicle()
    fascicle_1.fill()

    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True)
    ax.set_title("default fascicle")
    fig.savefig(figdir+"A.png")

    assert nrv.is_fascicle(fascicle_1), "Should be a nrv.fascicle"
    assert fascicle_1.d==50, "Default diam"

def create_fascicle_set_geometry():
    r1 = 15                # diameter, in um
    L = 10000             # length, in um
    r2 = 25, 60                 # diameter, in um

    fascicle_1 = nrv.fascicle()
    fascicle_1.define_length(L)
    fascicle_1.set_geometry(radius=r1)
    fascicle_1.fill()
    fig, axs = plt.subplots(2)
    fascicle_1.plot(axs[0], num=True)
    axs[0].set_title("fascicle to small")

    fascicle_2 = nrv.fascicle()
    fascicle_2.set_geometry(radius=r2, rot=np.pi/4)
    fascicle_2.fill()
    fascicle_2.plot(axs[1], num=True)
    axs[1].set_title("ellipse fascicle")
    fig.savefig(figdir+"B.png")


def create_fascicle_FVF():
    fascicle_1 = nrv.fascicle()
    fascicle_1.set_geometry(radius=50)

    fascicle_1.fill(FVF=0.55)
    print(np.pi*np.sum((fascicle_1.axons["diameters"]/2)**2))
    print(np.pi*np.sum((fascicle_1.axons["diameters"]/2)**2)/fascicle_1.axons.n_ax, np.mean(fascicle_1.axons["diameters"]))
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True)
    fig.savefig(figdir+"C.png")

    assert nrv.is_fascicle(fascicle_1), "Should be a nrv.fascicle"


if __name__ == "__main__":
    # parameters for the test fascicle
    create_fascicle_default()
    create_fascicle_set_geometry()
    create_fascicle_FVF()
    # plt.show()


