import nrv.utils.geom as geom
import matplotlib.pyplot as plt

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_ellipse():
    center = (1, 1)
    r = 3, 2
    ellipse = geom.Ellipse(center, r)
    bbox = geom.get_cshape_bbox(ellipse, looped_end=True)

    assert ellipse.center == center, "Center should be set correctly."
    assert ellipse.r1 == r[0], "Semi-major axis should be set correctly."
    assert ellipse.r2 == r[1], "Semi-minor axis should be set correctly."
    assert ellipse.is_inside((1, 1)), "Point (1, 1) should be inside the ellipse."
    assert not ellipse.is_inside((5, 5)), "Point (5, 5) should be outside the ellipse."
    assert ellipse.is_inside((3, 1)), "Point (3, 1) should be inside the ellipse." 
    assert not ellipse.is_inside((3, 4)), "Point (3, 4) should be outside the ellipse."


    fig, ax = plt.subplots(figsize=(6, 6))
    ellipse.plot(ax, label="Polygon Trace")
    ellipse.plot_bbox(ax, "-+",color=("k",.2),label='bbox')
    plt.scatter(*ellipse.center, color='red', label='Center', zorder=5)
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    fig.savefig(figdir+"A.png")


if __name__ == "__main__":
    test_ellipse()
    print("All tests passed successfully.")

    # plt.show()
