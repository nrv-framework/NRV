import nrv.eit as eit
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_id = __fname__[:__fname__.find("_")]

if __name__ == "__main__":
    nerves_fname = "./unitary_tests/sources/400_1uax_nerve.json"
    i_e = np.arange(8)
    res_fname_1  = f"./unitary_tests/sources/SA_1_fem.json"
    res_fname_2  = f"./unitary_tests/sources/SA_1_fem.json"

    fem_res_1 = eit.results.eit_forward_results(data=res_fname_1)
    fem_res_2 = eit.results.eit_forward_results(data=res_fname_2)
    l_res = eit.results.eit_results_list(results=[fem_res_1, fem_res_2])


    print(l_res.shape==l_res.v_eit(i_res=None, i_e=i_e).shape)
    print(l_res.v_eit(i_res=0, i_e=i_e).shape)
    print(l_res.dv_eit(i_res=0, i_e=i_e).shape)


    
    print("all ok")
    
    # plt.show()