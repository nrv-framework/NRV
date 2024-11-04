
import nrv
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

if __name__ == "__main__":
    N_test = "208"
    figdir = "./unitary_tests/figures/" + N_test + "_"

    dt = 0.005
    t_sim = 6
    t_end = t_sim-2
    t_bound = (0, t_end)
    I_bound = (-500, 0)

    kwrgs_interp = {
        "dt": dt,
        "amp_start": 0,
        "amp_stop": 0,
        "intertype": "Spline",
        "bounds": I_bound,
        "fixed_order": False,
        "t_end": t_end,
        "t_sim":t_sim,
        }

    X = [t_end, 0, t_end, -500, t_end, -500, t_end, -500]
    nrv.interpolate_Npts(position=X, save=True, fname=figdir + "A.png", **kwrgs_interp)

    X2 = [2, -20, 1, -40, 1.5, -30]
    nrv.interpolate_Npts(position=X2, save=True, fname=figdir + "B.png", **kwrgs_interp)

    X3 = [2, -20, 1, -40, 1.001, -45, 1.5, -30]
    nrv.interpolate_Npts(position=X3, save=True, fname=figdir + "C.png", **kwrgs_interp)

    X4 = [0, -20, 0, -40, 0, -45, 0, -30, 0, -30, 0, -30]
    nrv.interpolate_Npts(position=X4, strict_bounds=True, save=True, fname=figdir + "d.png", **kwrgs_interp)

    X = [t_end, 0, t_end, -500]
    nrv.interpolate_Npts(position=X, save=True, fname=figdir + "E.png", **kwrgs_interp)

    # Spline 2pts


    dt = 0.005
    t_sim = 1
    t_end = 0.5
    I_max_abs = 100
    t_bound = (0, 1)
    I_bound = (-I_max_abs, 0)

    kwrgs_interp = {
        "dt": dt,
        "amp_start": 0,
        "amp_stop": 0,
        "intertype": "Spline",
        "bounds": I_bound,
        "fixed_order": False,
        "t_end": t_end,
        "t_sim":t_sim,
        "strict_bounds":True,
        "intertype":"spline",
        }



    bounds = [t_bound, I_bound, t_bound, I_bound, (0.01,0.5)]


    plt.figure()
    for i in range(10):
        X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
        #print(X)
        waveform2 = nrv.interpolate_Npts(X, plot=True, generatefigure=False, **kwrgs_interp)
    plt.savefig(figdir + "F.png")
    bounds = [t_bound, I_bound, t_bound, I_bound, t_bound, I_bound, t_bound, I_bound, t_bound, I_bound, (0.01,0.5)]


    for i in tqdm(range(100000)):
        X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
        waveform2 = nrv.interpolate_Npts(X, plot=False, generatefigure=False, **kwrgs_interp)

    #plt.show()
