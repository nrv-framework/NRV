import nrv
import matplotlib.pyplot as plt
import numpy as np
import sys

def test_oft_pp(results:nrv.axon_results, num=0):
    results["comment"] = "Custom PP accessed"
    results["num"] = num
    results.remove_key(keys_to_keep={"ID", "comment", "num"})
    return results

test_num = 301
postproc = ['default', 'rmv_keys', test_oft_pp, test_oft_pp]
postproc_kwargs = [{}, {}, {}, {"num":1, "unvalid_arg":404}]
fascicle = nrv.fascicle(ID=test_num)

# SHAM 1 axon fascicle
fascicle.axons_diameter = np.asarray([5.7])
fascicle.axons_type = np.asarray([1])
fascicle.axons_y = np.asarray([0])
fascicle.axons_z = np.asarray([0])
fascicle.define_circular_contour(D=6)
fasc_dic = fascicle.save(save=False)

for i in range(len(postproc)):
    id = test_num*10 + i
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(id)
    nerve.add_fascicle(fasc_dic, ID=1, y=-6)
    nerve.add_fascicle(fasc_dic, ID=2, y=6)
    nerve.add_fascicle(fasc_dic, ID=3, z=-6)
    nerve.add_fascicle(fasc_dic, ID=4, z=6)
    nerve.fit_circular_contour()


    # launch sim with
    nerve.simulate(save_path='./unitary_tests/figures/', postproc_script=postproc[i])
    if nrv.MCH.do_master_only_work():
        print(nerve.postproc_label + ' OFT_PP ok')
        sys.stdout.flush()
    del nerve

#plt.show()
