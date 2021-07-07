#pragma parallel
import nrv
import time

diam = 10
L = 50000
material = 'endoneurium_bhadra'
dist_elec = 1000
freq = 10
start_time = time.time()
threshold = nrv.para_blocking_threshold(diam,L,material,dist_elec,freq,amp_tol=1)
comput_time = time.time() - start_time
if nrv.MCH.do_master_only_work():
    print(threshold)
    print(comput_time)