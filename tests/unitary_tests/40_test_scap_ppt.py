import eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
from time import perf_counter

__fname__ = __file__[__file__.find("tests/")+6:]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./nerves/u1_nerve.json"
    res_dir  = f"./results/{test_id}/"
    src_f = [f"./sources/SA_{i}_fem.json" for i in range(3)]
    overwrite_rfile = False

    r_list = eit.eit_results_list(results=src_f)
    i_r_ = np.arange(r_list.shape[0])

    t0 = perf_counter()
    cap_ppt=r_list.get_acap_v_ppt(i_res=None)
    t1 = perf_counter()
    print(cap_ppt)
