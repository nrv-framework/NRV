import nrv.utils.geom as geom
import matplotlib.pyplot as plt

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_ellipse():
    center = (1, 1)
    r1 = 3
    r2 = 2
    ellipse = geom.Ellipse(center, r1, r2)
    assert ellipse.center == center, "Center should be set correctly."
    assert ellipse.r1 == r1, "Semi-major axis should be set correctly."
    assert ellipse.r2 == r2, "Semi-minor axis should be set correctly."
    assert ellipse.is_inside((1, 1)), "Point (1, 1) should be inside the ellipse."
    assert not ellipse.is_inside((5, 5)), "Point (5, 5) should be outside the ellipse."
    assert ellipse.is_inside((3, 1)), "Point (3, 1) should be inside the ellipse." 
    assert not ellipse.is_inside((3, 4)), "Point (3, 4) should be outside the ellipse."


    y_trace, z_trace = ellipse.get_trace()
    assert len(y_trace) == ellipse.Ntheta, "Trace x-coordinates should match Ntheta."
    assert len(z_trace) == ellipse.Ntheta, "Trace y-coordinates should match Ntheta."
    # Plot the ellipse
    plt.figure(figsize=(6, 6))
    plt.plot(y_trace, z_trace, label='Ellipse Trace')
    plt.scatter(*ellipse.center[:2], color='red', label='Center', zorder=5)
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
    test_ellipse()
    print("All tests passed successfully.")