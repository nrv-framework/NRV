import nrv
import numpy as np
import matplotlib.pyplot as plt

def test_oft_pp(results:nrv.axon_results, num=0):
    results["comment"] = "Custom PP accessed"
    results["num"] = num
    results.remove_key(keys_to_keep={"ID", "comment", "num"})
    return results

key_to_check_default = {"L", "ID", "myelinated", "intra_stim_positions", "V_mem_raster_position"}
key_to_check_custom = {"ID", "comment", "num"}

# parameters for the test fascicle
L = 10000 			# length, in um
fascicles = []
for i in range(4):
    fascicles += [nrv.fascicle(return_parameters_only=False, ID=57*10+i)]
    fascicles[i].define_length(L)
    # SHAM 1 axon fascicle
    fascicles[i].axons_diameter = np.asarray([5.7])
    fascicles[i].axons_type = np.asarray([1])
    fascicles[i].axons_y = np.asarray([0])
    fascicles[i].axons_z = np.asarray([0])


# launch sim with
res = fascicles[0].simulate(save_path='./unitary_tests/figures/')
if nrv.MCH.do_master_only_work():
    print('default OFT_PP:')
    print(len(key_to_check_default - set(res["axon0"].keys())) == 0)
del fascicles[0], res

res = fascicles[0].simulate(save_path='./unitary_tests/figures/',postproc_script='rmv_keys')
if nrv.MCH.do_master_only_work():
    print('rmv_keys OFT_PP:')
    print(len(key_to_check_default - set(res["axon0"].keys())) == 0)
del fascicles[0], res

res = fascicles[0].simulate(save_path='./unitary_tests/figures/',postproc_script=test_oft_pp)
if nrv.MCH.do_master_only_work():
    print('Custom OFT_PP:')
    print(len(key_to_check_custom - set(res["axon0"].keys())) == 0)
del fascicles[0], res

res = fascicles[0].simulate(save_path='./unitary_tests/figures/',postproc_script=test_oft_pp, postproc_kwargs={"num":1, "unvalid_arg":404})
if nrv.MCH.do_master_only_work():
    print('Custom OFT_PP with kwargs:')
    print(len(key_to_check_custom - set(res["axon0"].keys())) == 0)
del fascicles, res


fasc = nrv.fascicle(return_parameters_only=False, ID=57*10+i+1,save_path='./unitary_tests/figures/',postproc_script=test_oft_pp, postproc_kwargs={"num":2, "unvalid_arg":404})
fasc.define_length(L)
# SHAM 1 axon fascicle
fasc.axons_diameter = np.asarray([5.7])
fasc.axons_type = np.asarray([1])
fasc.axons_y = np.asarray([0])
fasc.axons_z = np.asarray([0])

res = fasc()
if nrv.MCH.do_master_only_work():
    print('Custom OFT_PP with kwargs (set when instantiated):')
    print(len(key_to_check_custom - set(res["axon0"].keys())) == 0)