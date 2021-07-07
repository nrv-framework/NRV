#pragma parallel
import nrv
import numpy as np
import matplotlib.pyplot as plt

if nrv.MCH.do_master_only_work():
	test = np.arange(20)
else:
	test = None
result = nrv.MCH.master_broadcasts_array_to_all(test)
print('I am PID '+str(nrv.MCH.rank)+' and I recieved'+str(result))