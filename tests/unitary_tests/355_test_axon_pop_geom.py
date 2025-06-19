from nrv.utils import geom
from nrv.nmod._axon_population import axon_population
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_axon_pop_set_geometry():
    # 
    center = (1000, 2000)
    r = 3000, 2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)
    y_trace, z_trace = ellipse.get_trace()

    pop_1 = axon_population()
    assert not pop_1.has_geom, "Axon population should not contain geometry at the creation."

    pop_1.set_geometry(ellipse)
    assert pop_1.has_geom, "Axon population should not contain geometry at the creation."
    assert pop_1.geom.center == center, "Center should be set correctly."
    assert pop_1.geom.r1 == r[0], "Semi-major axis should be set correctly."
    assert pop_1.geom.r2 == r[1], "Semi-minor axis should be set correctly."
    assert pop_1.geom.is_inside((1, 1)), "Point (1, 1) should be inside the ellipse."



def test_axon_pop_create_geometry():
    # 
    center = 1000, 2000
    r = 3000,2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)
    y_trace, z_trace = ellipse.get_trace()

    pop_1 = axon_population()

    assert not pop_1.has_geom, "Axon population should not contain geometry at the creation."

    pop_1.set_geometry(center=center, radius=r, rot=angle)

    assert pop_1.has_geom, "Axon population should not contain geometry at the creation."
    assert pop_1.geom.center == center, "Center should be set correctly."
    assert pop_1.geom.r1 == r[0], "Semi-major axis should be set correctly."
    assert pop_1.geom.r2 == r[1], "Semi-minor axis should be set correctly."
    assert pop_1.geom.is_inside((1, 1)), "Point (1, 1) should be inside the ellipse."



if __name__ == "__main__":
    test_axon_pop_set_geometry()
    test_axon_pop_create_geometry()
    print("All tests passed successfully.")


