import nrv.utils.geom as geom
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_get_point_inside_ellipse():
    center = 1, 2
    r = 3, 2
    angle = np.pi/4 # Rotation angle in degrees
    ellipse = geom.Ellipse(center, r, angle)

    y_trace, z_trace = ellipse.get_trace()
    inside_pts = ellipse.get_point_inside(1000, delta=.5)
    assert ellipse.is_inside(inside_pts), "Generated points should be inside the rotated ellipse."

    # Plot the rotated ellipse
    plt.figure(figsize=(6, 6))
    plt.plot(y_trace, z_trace, label='Rotated Ellipse Trace')

    plt.scatter(*ellipse.center[:2], color='red', label='Center', zorder=5)
    plt.scatter(*inside_pts.T, color=(.2,.6,.3,.2), label='generated points', zorder=5)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Rotated Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"A.png")


def test_get_point_inside_circle():
    center = (-1, 2)
    r = 4
    angle = np.pi/4 # Rotation angle in degrees
    circle = geom.Circle(center, r, angle)

    y_trace, z_trace = circle.get_trace()
    inside_pts = circle.get_point_inside(1000, delta=.5)
    assert circle.is_inside(inside_pts), "Generated points should be inside the rotated circle."

    # Plot the rotated ellipse
    plt.figure(figsize=(6, 6))
    plt.plot(y_trace, z_trace, label='Rotated Ellipse Trace')

    plt.scatter(*circle.center[:2], color='red', label='Center', zorder=5)
    plt.scatter(*inside_pts.T, color=(.2,.6,.3,.2), label='generated points', zorder=5)
    plt.xlim(-8, 8)
    plt.ylim(-8, 8)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Rotated Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"B.png")

if __name__ == "__main__":
    test_get_point_inside_ellipse()
    test_get_point_inside_circle()
    print("All tests passed successfully.")

    # plt.show()

