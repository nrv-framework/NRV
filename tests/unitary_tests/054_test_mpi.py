#pragma parallel
import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":
    t0 = time.time()
    if nrv.MCH.do_master_only_work():
        time.sleep(4)

    if nrv.MCH.rank == 2:
        time.sleep(2)

    if nrv.MCH.rank == 1:
        time.sleep(10)

    t1 = time.time()
    nrv.synchronize_processes()
    t2 = time.time()

    print('I am PID '+str(nrv.MCH.rank)+' and I finish my task in '+str(round(t1-t0))+'s and I waited for my friends ' +str(round(t2-t1))+ 's')

    nrv.synchronize_processes()

    if nrv.MCH.do_master_only_work():
        test = np.arange(20)
    else:
        test = None
    result = nrv.MCH.master_broadcasts_array_to_all(test)
    print('I am PID '+str(nrv.MCH.rank)+' and I recieved'+str(result))

