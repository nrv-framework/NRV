

import nrv
import numpy as np 
import matplotlib.pyplot as plt

if __name__ == "__main__":
    stim1 = nrv.stimulus()

    tstart = 10
    tstop = 100
    standard_dev = 5
    offset = 10

    stim1.gaussian_noise(tstart, tstop, standard_dev, offset=offset, dt=0.005)

    plt.figure()
    plt.step(stim1.t, stim1.s,where='post')


    plt.show()