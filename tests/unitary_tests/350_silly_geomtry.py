import nrv.utils.geom as geom
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

def nrv_geom():
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # N
    r1 = 2
    r2 = 8
    center = (2, 1)
    el = geom.Ellipse(center, (r1, r2))
    X_trace1= el.get_trace()
    inside_pts1 = el.get_point_inside(5000, delta=.3)
    del el

    center = (5, 1)
    el = geom.Ellipse(center, (r1, r2+.5), rot=-np.pi/8)
    X_trace2 = el.get_trace()
    inside_pts2 = el.get_point_inside(5000, delta=.3)
    del el

    center = (8, 1)
    el = geom.Ellipse(center, (r1, r2))
    X_trace3 = el.get_trace()
    inside_pts31 = el.get_point_inside(5000, delta=.3)
    inside_pts32 = el.get_point_inside(300, delta=.3)
    del el



    # R
    r1 = 2
    r2 = 8

    center = (10.7, 5.8)
    ci = geom.Circle(center, 3.7)
    X_trace4= ci.get_trace()
    inside_pts4 = ci.get_point_inside(5000, delta=.3)
    del ci

    center = (12.5, -1.7)
    el = geom.Ellipse(center, (r1, 5), rot=-np.pi/8)
    X_trace5 = el.get_trace()
    inside_pts5 = el.get_point_inside(5000, delta=.3)
    del el



    # V
    center = (18, 1)
    el = geom.Ellipse(center, (r1, r2+.5), rot=-np.pi/10)
    X_trace6 = el.get_trace()
    inside_pts6 = el.get_point_inside(5000, delta=.3)
    del el

    center = (23, 1)
    el = geom.Ellipse(center, (r1, r2+.5), rot=np.pi/10)
    X_trace7 = el.get_trace()
    inside_pts7 = el.get_point_inside(5000, delta=.3)
    del el



    ax.plot(*X_trace6, color="#593869")
    ax.plot(*X_trace7, color="#593869")
    ax.scatter(*inside_pts6.T, color= "#5938698C")
    ax.scatter(*inside_pts7.T, color= "#5938698C")
    
    ax.plot(*X_trace4, color="#146B6B")
    ax.plot(*X_trace5, color="#146B6B")
    ax.scatter(*inside_pts4.T, color= "#146B6B8C")
    ax.scatter(*inside_pts5.T, color= "#146B6B8C")

    ax.plot(*X_trace1, color="#1E4B94")
    ax.plot(*X_trace2, color="#1E4B94")
    ax.plot(*X_trace3, color="#1E4B94")
    ax.plot(X_trace3[0][:25], X_trace3[1][:25], color="#146B6B")
    ax.plot(X_trace3[0][-25:], X_trace3[1][-25:], color="#146B6B")

    ax.scatter(*inside_pts1.T, color= "#1E4B948C")
    ax.scatter(*inside_pts31.T, color= "#1E4B948C")
    ax.scatter(*inside_pts32.T, color= "#146B6B8C")
    ax.scatter(*inside_pts2.T, color= "#1E4B948C")
    
    
    
    plt.xlim(-1, 30)
    plt.ylim(-15, 15)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title('Ellipse Test')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.savefig(figdir+"A.png")


if __name__ == "__main__":
    nrv_geom()
    print("All tests passed successfully.")

    # plt.show()
