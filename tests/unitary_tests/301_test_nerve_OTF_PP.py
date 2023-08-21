import nrv
import matplotlib.pyplot as plt
import numpy as np
import sys

test_num = 301
postproc = ['default', 'rmv_keys', 'Rmv_keys.py', './unitary_tests/sources/test_OTF_PP.py']

fascicle = nrv.fascicle(ID=test_num)

# SHAM 1 axon fascicle
fascicle.axons_diameter = np.asarray([5.7])
fascicle.axons_type = np.asarray([1])
fascicle.axons_y = np.asarray([0])
fascicle.axons_z = np.asarray([0])
fascicle.define_circular_contour(D=6)
fascicle.N = 1 
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
        print(postproc[i] + ' OFT_PP ok')
        sys.stdout.flush()
#plt.show()