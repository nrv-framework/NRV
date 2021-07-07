import nrv
import numpy as np
import matplotlib.pyplot as plt



# parameters for the test fascicle
L = 10000 			# length, in um

fascicle_1 = nrv.fascicle(ID=57)
fascicle_1.define_length(L)
# SHAM 1 axon fascicle
fascicle_1.axons_diameter = np.asarray([5.7])
fascicle_1.axons_type = np.asarray([1])
fascicle_1.axons_y = np.asarray([0])
fascicle_1.axons_z = np.asarray([0])
fascicle_1.N = 1 

# launch sim with
fascicle_1.simulate(save_path='./unitary_tests/figures/',postproc_script='./unitary_tests/sources/test_OTF_PP.py')