import nrv 
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 20000

    ########## test A : myelinated record all #############
    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')

    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+0.5, duration, amplitude)
    #axon1.insert_I_Clamp(0.5, t_start+1.0, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+2.5, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+5.5, duration, amplitude)

    results = axon1.simulate(t_sim=8)
    x = results["t"]
    y = results["V_mem"][0]
    height = [0,70]

    t_refractory = 0.5
    dt = x[1]-x[0]
    dis = int(t_refractory/dt)

    t_min_AP=0.1
    width = int(t_min_AP/dt)
    peaks, _ = find_peaks(y, height=height,distance=dis, width=width)



    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)
    fig.savefig('./unitary_tests/figures/533_peaks_A.png')

    results.rasterize()
    fig, ax = plt.subplots(1)
    results.raster_plot(ax)
    fig.savefig('./unitary_tests/figures/533_peaks_B.png')

    #plt.show()