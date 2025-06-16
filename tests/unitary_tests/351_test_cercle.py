import nrv.utils.geom as geom
import matplotlib.pyplot as plt
import numpy as np


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

def test_cercle():
    center = (1, 1)
    radius = 2
    circle = geom.Circle(center, radius)
    assert circle.center == center, "Center should be set correctly."
    assert circle.r1 == radius, "Radius should be set correctly."
    assert circle.radius == radius, "Radius should be set correctly."
    assert circle.is_inside((1, 1)), "Point (1, 1) should be inside the circle."
    assert not circle.is_inside((5, 5)), "Point (5, 5) should be outside the circle."
    assert circle.is_inside((3, 1)), "Point (3, 1) should be inside the circle." 
    assert not circle.is_inside((3, 4)), "Point (3, 4) should be outside the circle."


    y_trace, z_trace = circle.get_trace()
    assert len(y_trace) == circle.Ntheta, "Trace x-coordinates should match Ntheta."
    assert len(z_trace) == circle.Ntheta, "Trace y-coordinates should match Ntheta."
    # Plot the circle
    plt.figure(figsize=(6, 6))
    plt.plot(y_trace, z_trace, label='Ellipse Trace')
    plt.scatter(*circle.center[:2], color='red', label='Center', zorder=5)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"A.png")

if __name__ == "__main__":
    test_cercle()
    print("All tests passed successfully.")