import nrv
import matplotlib.pyplot as plt
import numpy as np
import sys

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

def create_nerve(_id):
    fasc = nrv.fascicle()
    fasc.define_length(10000)
    fasc.set_geometry(diameter=50)
    fasc.fill(data=np.array([1, 5.7, 0, 0]).reshape((4,1)))
    fasc_dic = fasc.save(save=False)
    id = int(test_num)*10 + _id
    nerve = nrv.nerve(diameter=500, Length=10_000, return_parameters_only=False)
    nerve.set_ID(id)
    nerve.add_fascicle(fasc_dic, ID=1, y=-100)
    nerve.add_fascicle(fasc_dic, ID=2, y=100)
    nerve.add_fascicle(fasc_dic, ID=3, z=-100)
    nerve.add_fascicle(fasc_dic, ID=4, z=100)
    return nerve




def test_default_OFT_PP():
    ner = create_nerve(_id=0)
    fig, ax = plt.subplots()
    ner.plot(ax)
    res = ner.simulate()

    assert len(key_to_check_default - set(res["fascicle1"]["axon0"].keys())) == 0,  "Wrong keys removed from default OFT PP"


def test_rmv_keys_OFT_PP():
    ne = create_nerve(_id=1)
    res = ne.simulate(postproc_script='rmv_keys')

    assert len(key_to_check_default - set(res["fascicle1"]["axon0"].keys())) == 0,  "Wrong keys removed from rmv_key OFT PP"

def test_custom_OFT_PP():
    ne = create_nerve(_id=2)
    res = ne.simulate(postproc_script=test_oft_pp)

    assert len(key_to_check_custom - set(res["fascicle1"]["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP"


def test_custom_OFT_PP_with_kwargs():
    # set in simulation
    ne = create_nerve(_id=2)
    res = ne.simulate(postproc_script=test_oft_pp, postproc_kwargs={"num":1, "unvalid_arg":404})


    assert len(key_to_check_custom - set(res["fascicle1"]["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP set with kwargs"

    # set in istantiation
    fasc = nrv.fascicle()
    fasc.fill(data=np.array([1, 5.7, 0, 0]).reshape((4,1)))
    fasc_dic = fasc.save(save=False)
    nerve = nrv.nerve(ID=int(test_num)*10, Length=10000, return_parameters_only=False,postproc_script=test_oft_pp, postproc_kwargs={"num":2, "unvalid_arg":404})
    nerve.set_ID(id)
    nerve.add_fascicle(fasc_dic, ID=1, y=-50)
    nerve.add_fascicle(fasc_dic, ID=2, y=50)
    nerve.add_fascicle(fasc_dic, ID=3, z=-50)
    nerve.add_fascicle(fasc_dic, ID=4, z=50)

    assert len(key_to_check_custom - set(res["fascicle1"]["axon0"].keys())) == 0,  "Wrong keys removed from custom OFT PP set with kwargs set in the istantiation"


if __name__ == "__main__":
    test_default_OFT_PP()
    test_rmv_keys_OFT_PP()
    test_custom_OFT_PP()
    test_custom_OFT_PP_with_kwargs()
    # plt.show()
