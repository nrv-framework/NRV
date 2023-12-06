
import nrv
import matplotlib.pyplot as plt
import numpy as np

N_test = "215"
figdir = "./unitary_tests/figures/" + N_test + "_"

t_sim = 6
t_end = t_sim-2
t_bound = (0, t_end)
I_bound = (-500, 0)

kwrgs_interp = {
    "dt": 0.005,
    "amp_start": 0,
    "amp_stop": 0,
    "intertype": "Spline",
    "bounds": I_bound,
    "fixed_order": False,
    "t_end": t_end,
    "t_sim":t_sim,
    }

X = [t_end, 0, t_end, -500]
nrv.interpolate_Npts(position=X, save=True, fname=figdir + "A.png", **kwrgs_interp)

X2 = [2, -20, 1, -40, 1.5, -30]
nrv.interpolate_Npts(position=X2, save=True, fname=figdir + "B.png", **kwrgs_interp)

X3 = [2, -20, 1, -40, 1.001, -45, 1.5, -30]
nrv.interpolate_Npts(position=X3, save=True, fname=figdir + "C.png", **kwrgs_interp)

X4 = [0, -20, 0, -40, 0, -45, 0, -30]
nrv.interpolate_Npts(position=X4, strict_bounds=True, save=True, fname=figdir + "D.png", **kwrgs_interp)

X = [t_end, 0, t_end, -500]
nrv.interpolate_2pts(position=X, save=True, fname=figdir + "A.png", **kwrgs_interp)
plt.show()
print()