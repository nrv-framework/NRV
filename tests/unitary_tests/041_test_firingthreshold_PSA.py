import nrv
import time

diam = 10
L = 50000
dist_elec = 1000

start_time = time.time()

threshold = nrv.firing_threshold_point_source(diam,L,dist_elec,cath_time = 100e-3,model='MRG',amp_max=2000,amp_tol=5)
comput_time = time.time() - start_time
print(threshold)
print(comput_time)