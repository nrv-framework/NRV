import nrv
import time

diam = 10
L = 50000
material = 'endoneurium_bhadra'
dist_elec = 1000

start_time = time.time()
threshold = nrv.firing_threshold(diam,L,material,dist_elec,amp_tol=1)
comput_time = time.time() - start_time
print(threshold)
print(comput_time)