#pragma parallel
import nrv
import tqdm
import time
import sys
import numpy as np

N_it = 100

pos = nrv.MCH.rank * 2
log1 = tqdm.tqdm(total=0, position=pos, bar_format='{desc}')
outer = tqdm.tqdm(total=N_it, position=pos+1)
for i in range(N_it):
    s_time = np.random.rand(1)[0]
    log1.set_description_str(f'rank: {nrv.MCH.rank}, computing:{s_time}')
    time.sleep(s_time)
    sys.stdout.flush()
    outer.update(1)
