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
    bbox_pts = circle.bbox
    bbox = bbox_pts[np.array([0,0,2,2,0])],bbox_pts[np.array([1,3,3,1,1])]
    assert circle.center == center, "Center should be set correctly."
    assert circle.r1 == radius, "Radius should be set correctly."
    assert circle.radius == radius, "Radius should be set correctly."
    assert circle.is_inside((1, 1)), "Point (1, 1) should be inside the circle."
    assert not circle.is_inside((5, 5)), "Point (5, 5) should be outside the circle."
    assert circle.is_inside((3, 1)), "Point (3, 1) should be inside the circle." 
    assert not circle.is_inside((3, 4)), "Point (3, 4) should be outside the circle."


    y_trace, z_trace = circle.get_trace()
    # Plot the circle
    y_trace, z_trace = circle.get_trace()
    fig, ax = plt.subplots(figsize=(6, 6))
    circle.plot(ax, label="Polygon Trace")
    circle.plot_bbox(ax, "-+",color=("k",.2),label='bbox')
    plt.scatter(*circle.center, color='red', label='Center', zorder=5)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('circle Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"A.png")

if __name__ == "__main__":
    test_cercle()
    print("All tests passed successfully.")

    # plt.show()