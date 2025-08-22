# deprecated since at least v1.2.2

import nrv
import time

if __name__ == "__main__":
    diam = 10
    L = 50000
    material = 'endoneurium_bhadra'
    dist_elec = 1000
    start_time = time.time()
    threshold, Niter = nrv.para_firing_threshold(diam,L,material,dist_elec)
    comput_time = time.time() - start_time
    print(threshold)
    print(comput_time)