import nrv

import numpy as np
import matplotlib.pyplot as plt

test_num = "165"
fig_file = f"./unitary_tests/figures/{test_num}_"


freqs = np.logspace(-1, 8, 100)

mat_lay = nrv.load_material("perineurium_horn")
mat_in = nrv.load_material("endoneurium_bhadra")
alpha = 0.03
mat = nrv.layered_material(mat_in=mat_in, mat_lay=mat_lay, alpha_lay=alpha)
sig = []
for f in freqs:
    sig += [[mat_lay.sigma, mat_in.sigma, mat.sigma]]
    mat_lay.set_frequency(f)
    mat.set_frequency(f)

print(np.isclose(alpha/sig[0][0] + (1-alpha)/sig[0][1], 1/sig[0][2]))
plt.figure()
plt.loglog(freqs, sig)
plt.savefig(fig_file+"A.png")

#plt.show()
