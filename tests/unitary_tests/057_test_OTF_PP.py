import nrv
import numpy as np
import matplotlib.pyplot as plt

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_oft_pp(results:nrv.axon_results, num=0):
    results["comment"] = "Custom PP accessed"
    results["num"] = num
    results.remove_key(keys_to_keep={"ID", "comment", "num"})
    return results

key_to_check_default = {"L", "ID", "myelinated", "intra_stim_positions", "V_mem_raster_position"}
key_to_check_custom = {"ID", "comment", "num"}

def create_fascicle(_id):
    fasc = nrv.fascicle(return_parameters_only=False, ID=int(test_num)*10+_id)
    fasc.define_length(10000)
    fasc.fill(data=np.array([1, 5.7, 0, 0]).reshape((4,1)))
    return fasc



def test_default_OFT_PP():
    fasc = create_fascicle(_id=0)
    res = fasc.simulate(save_path='./unitary_tests/figures/')

    assert len(key_to_check_default - set(res["axon0"].keys())) == 0,  "Wrong keys removed from default OFT PP"


def test_rmv_keys_OFT_PP():
    fasc = create_fascicle(_id=1)
    res = fasc.simulate(save_path='./unitary_tests/figures/', postproc_script='rmv_keys')

    assert len(key_to_check_default - set(res["axon0"].keys())) == 0, "Wrong keys removed from rmv_key OFT PP"

def test_custom_OFT_PP():
    fasc = create_fascicle(_id=2)
    res = fasc.simulate(save_path='./unitary_tests/figures/', postproc_script=test_oft_pp)
    print(key_to_check_custom, set(res["axon0"].keys()))

    assert len(key_to_check_custom - set(res["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP"


def test_custom_OFT_PP_with_kwargs():
    # set in simulation
    fasc = create_fascicle(_id=2)
    res = fasc.simulate(save_path='./unitary_tests/figures/',postproc_script=test_oft_pp, postproc_kwargs={"num":1, "unvalid_arg":404})


    assert len(key_to_check_custom - set(res["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP set with kwargs"


    # set in istantiation
    fasc = nrv.fascicle(return_parameters_only=False, ID=57*10+4,save_path='./unitary_tests/figures/',postproc_script=test_oft_pp, postproc_kwargs={"num":2, "unvalid_arg":404})
    fasc.define_length(10000)
    fasc.fill(data=np.array([1, 5.7, 0, 0]).reshape((4,1)))
    res = fasc()

    assert len(key_to_check_custom - set(res["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP set with kwargs set in the istantiation"

if __name__ == "__main__":
    test_default_OFT_PP()

    test_rmv_keys_OFT_PP()
    test_custom_OFT_PP()
    test_custom_OFT_PP_with_kwargs()