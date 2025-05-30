#pragma parallel
import nrv
import time

if __name__ == "__main__":
    diam = 10
    L = 50000
    material = 'endoneurium_bhadra'
    dist_elec = 1000
    freq = 10
    start_time = time.time()
    threshold = nrv.para_blocking_threshold(diam,L,material,dist_elec,freq,amp_tol=1)
    comput_time = time.time() - start_time
    print(threshold)
    print(comput_time)