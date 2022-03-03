import nrv
import numpy as np

partial_result = np.arange(nrv.MCH.rank*100, nrv.MCH.rank*100 + 10)
print('Process '+str(nrv.MCH.rank)+'generated data ', partial_result)
global_result =  nrv.MCH.sum_jobs(partial_result)


print(global_result)