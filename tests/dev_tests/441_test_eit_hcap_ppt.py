import nrv.eit as eit
import numpy as np
import matplotlib.pyplot as plt
import os
from time import perf_counter


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_u1_nerve.json"
    res_dir  = f"./unitary_tests/results/outputs/"
    src_f = [f"./sources/HA_{i}_fem.json" for i in range(2)]
    overwrite_rfile = False



    r_list = eit.results.eit_results_list(results=src_f)
    i_r_ = np.arange(r_list.shape[0])


    t0 = perf_counter()
    cap_ppt=r_list.get_acap_v_ppt(i_res=None)
    t1 = perf_counter()
    print(cap_ppt)

    expr_1="i_e == 4 or i_e == 3"
    expr_2="i_cap == 0"
    print(cap_ppt.query(expr_1))
    print(cap_ppt.query(expr_2))
    print(f"get_acap_v_ppt: {t1-t0}s")

    t0 = perf_counter()
    cap_ppt=r_list.get_acap_v_ppt(i_res=None, store="overwrite", t_new_cap=4)
    t1 = perf_counter()
    print(cap_ppt.query(expr_1))
    print(f"get_acap_v_ppt: {t1-t0}s")


