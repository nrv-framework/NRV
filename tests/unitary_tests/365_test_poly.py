import nrv.utils.geom as geom
import matplotlib.pyplot as plt
import numpy as np


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

def test_cercle():
    points = [[-6,1.5],[0,-2], [-2,1.5],[0,5]]
    poly = geom.Polygon(vertices=points)
    bbox_pts = poly.bbox
    bbox = bbox_pts[np.array([0,0,2,2,0])],bbox_pts[np.array([1,3,3,1,1])]
    assert np.allclose(points, poly.vertices), "Center should be set correctly."
    inside_pts = poly.get_point_inside(1000)
    assert poly.is_inside((inside_pts[0],inside_pts[1])), "Generated points should be inside the rotated ellipse."

    # Plot the poly
    fig, ax = plt.subplots(figsize=(6, 6))
    poly.plot(ax, label="Polygon Trace")
    poly.plot_bbox(ax, "-+",color=("k",.2),label='bbox')
    ax.scatter(*poly.center[:2], color='red', label='Center', zorder=5)
    ax.scatter(*inside_pts, color=(.2,.6,.3,.2), label='generated points', zorder=5)
    # plt.xlim(-5, 5)
    # plt.ylim(-5, 5)
    ax.set_aspect('equal', adjustable='box')
    ax.set_title('Poligon Test')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.legend()
    ax.grid()
    fig.savefig(figdir+"A.png")

if __name__ == "__main__":
    test_cercle()
    print("All tests passed successfully.")

    plt.show()