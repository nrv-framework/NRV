import nrv
import time

diam = 10
L = 50000
dist_elec = 1000
freq = 10


start_time = time.time()
threshold = nrv.blocking_threshold_point_source(diam,L,dist_elec,freq,model='MRG',amp_max=1000,amp_tol=5,dt=0.005,Nseg_per_sec=1)
comput_time = time.time() - start_time
print(threshold)
print(comput_time)