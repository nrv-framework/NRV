import nrv
import numpy as np
import matplotlib.pyplot as plt



# parameters for the test fascicle
L = 10000 			# length, in um
fascicles = []
for i in range(4):
    fascicles += [nrv.fascicle(ID=57*10+i)]
    fascicles[i].define_length(L)
    # SHAM 1 axon fascicle
    fascicles[i].axons_diameter = np.asarray([5.7])
    fascicles[i].axons_type = np.asarray([1])
    fascicles[i].axons_y = np.asarray([0])
    fascicles[i].axons_z = np.asarray([0])


# launch sim with
fascicles[0].simulate(save_path='./unitary_tests/figures/')
print('default OFT_PP ok')

fascicles[1].simulate(save_path='./unitary_tests/figures/',postproc_script='rmv_keys')
print('rmv_keys OFT_PP ok')

fascicles[2].simulate(save_path='./unitary_tests/figures/',postproc_script='Rmv_keys.py')
print('Rmv_keys.py OFT_PP ok')

fascicles[3].simulate(save_path='./unitary_tests/figures/',postproc_script='./unitary_tests/sources/test_OTF_PP.py')
print('Custom OFT_PP ok')

