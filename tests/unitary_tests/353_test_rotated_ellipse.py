import nrv.utils.geom as geom
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"



def test_rotated_ellipse():
    center = (1, 1)
    r1 = 3
    r2 = 2
    angle = np.pi/4 # Rotation angle in degrees
    ellipse = geom.Ellipse(center, r1, r2, angle)

    y_trace, z_trace = ellipse.get_trace()
    X_trace = np.array((y_trace, z_trace)).T

    trace_rtra = X_trace-ellipse.c
    trace_rrot = trace_rtra @ ellipse.Rmatrix_inverse
    trace_nms = trace_rrot/np.array([ellipse.r1, ellipse.r2])

    assert ellipse.is_inside((0, 2)), "Point (0, 2) should be inside the rotated ellipse."
    assert ellipse.is_inside(([0,0], [2,1])), "Point (0, 2) and (2, 1) should be inside the rotated ellipse."
    assert not ellipse.is_inside((5, 5)), "Point (5, 5) should be outside the rotated ellipse."
    
    # Plot the rotated ellipse
    plt.figure(figsize=(6, 6))
    plt.plot(y_trace, z_trace, label='Rotated Ellipse Trace')
    plt.scatter(*ellipse.center, color='red', label='Center', zorder=5)

    plt.plot(*trace_rrot.T, color=("r",.3),label='Inverse Translated Ellipse Trace')
    plt.plot(*trace_rtra.T, color=("orange",.3),label='Inverse Rotated Ellipse Trace')
    plt.plot(*trace_nms.T, color=("purple",.3),label='Normalized Trace')

    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Rotated Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid()
    plt.savefig(figdir+"A.png")

if __name__ == "__main__":
    test_rotated_ellipse()
    print("All tests passed successfully.")
