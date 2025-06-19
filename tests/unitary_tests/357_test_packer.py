from nrv.nmod.utils import Placer, get_ppop_info
from nrv.utils.geom import Ellipse

import matplotlib.pyplot as plt
import matplotlib.patches as ptc

import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_place_default_geom():
    # Place witout ax
    n1 = 100
    circles = Placer()
    r1, y1, z1, _ok1 = circles.place_all(n1)
    get_ppop_info(y1, z1, r1, verbose=True)

    assert r1.shape == (n1,), "Wrong size of radius list"
    assert y1.shape == (n1,), "Wrong size of y postion list"
    assert z1.shape == (n1,), "Wrong size of z postion list"
    
    # From a list
    n2 = 200
    c2 = Placer()
    r_list = c2.rmin + (c2.rmax - c2.rmin) * np.random.random(n2) * np.random.random(n2)
    r2, y2, z2, _ok2 = c2.place_all(r_list)
    assert r2.shape == (n2,), "Wrong size of radius list"
    assert y2.shape == (n2,), "Wrong size of y postion list"
    assert z2.shape == (n2,), "Wrong size of z postion list"


    fig, ax = plt.subplots()
    plt.plot(*circles.geom.get_trace(), label="default shape")
    for i in range(n1):
        if _ok1[i]:
            c = ptc.Circle((y1[i], z1[i]), r1[i], color="darkred")
            if i==0:
                c.set_label("pop 1")
            ax.add_artist(c)

    for i in range(n2):
        if _ok2[i]:
            c = ptc.Circle((y2[i], z2[i]), r2[i], color="teal")
            if i==0:
                c.set_label("pop 2")
            ax.add_artist(c)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Packing default shape Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"A.png")




def test_place_eliptic_geom():
    # 
    center = (100, 200)
    r1 = 300
    r2 = 200
    angle = -np.pi/12
    ellipse = Ellipse(center, (r1, r2), angle)
    y_trace, z_trace = ellipse.get_trace()
    # Place witout ax
    n1 = 400
    circles = Placer(geom=ellipse, delta=1)
    r1, y1, z1, _ok1 = circles.place_all(n1)
    get_ppop_info(y1, z1, r1, verbose=True)

    assert r1.shape == (n1,), "Wrong size of radius list"
    assert y1.shape == (n1,), "Wrong size of y postion list"
    assert z1.shape == (n1,), "Wrong size of z postion list"
    
    # From a list
    n2 = 100
    c2 = Placer(geom=ellipse, delta_trace=50)
    r_list = c2.rmin + (c2.rmax - c2.rmin) * np.random.random(n2) * np.random.random(n2)
    r2, y2, z2, _ok2 = c2.place_all(r_list)
    assert r2.shape == (n2,), "Wrong size of radius list"
    assert y2.shape == (n2,), "Wrong size of y postion list"
    assert z2.shape == (n2,), "Wrong size of z postion list"


    fig, ax = plt.subplots()
    plt.plot(*circles.geom.get_trace(), label="Set shape")
    for i in range(n1):
        if _ok1[i]:
            c = ptc.Circle((y1[i], z1[i]), r1[i], color="darkred")
            if i==0:
                c.set_label("pop 1")
            ax.add_artist(c)

    for i in range(n2):
        if _ok2[i]:
            c = ptc.Circle((y2[i], z2[i]), r2[i], color="teal")
            if i==0:
                c.set_label("pop 2")
            ax.add_artist(c)

    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Packing Ellipse shape Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"B.png")

if __name__ == "__main__":
    test_place_default_geom()
    test_place_eliptic_geom()
    print("All tests passed successfully.")

    # plt.show()


