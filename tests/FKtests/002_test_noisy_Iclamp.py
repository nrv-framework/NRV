import nrv
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter

if __name__ == "__main__":
    np.random.seed(123456789)
    y = 0
    z = 0
    d = 1
    L = 5000

    stim1 = nrv.stimulus()

    tstart = 10
    tstop = 100
    standard_dev = 5
    offset = 10

    stim1.gaussian_noise(tstart, tstop, standard_dev, offset=offset, dt=0.01)
    
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100, model='HH')
    axon1.insert_intra_stim(0.5, stim1) #self, position, stimulus

    t_start = 30
    duration = 0.5
    amplitude = 5
    axon1.insert_I_Clamp(0.1, t_start, duration, amplitude)
    print('lets see... ')
    t0 = perf_counter()
    results = axon1.simulate(t_sim=tstop)
    t1 = perf_counter() - t0
    print(f'... done in {t1}s')
    print('... done')
    del axon1

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')

    plt.show()