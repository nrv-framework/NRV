import nrv

import numpy as np
import matplotlib.pyplot as plt
if __name__ == '__main__':
        
    test_num = "164"
    fig_file = f"./unitary_tests/figures/{test_num}_"

    mat1 = nrv.material()

    sig_0 = 0.0002
    eps_r = 100
    mat1.set_isotropic_conductivity(sig_0)
    mat1.set_permitivity(eps_r)
    print(mat1.sigma == sig_0)

    fc = sig_0 / (2 * nrv.pi * nrv.epsilon_0 * eps_r)
    mat1.set_frequency(fc) 
    sig_fc = mat1.sigma
    print(mat1.sigma != sig_0)

    freqs = np.logspace(1, 6, 100)
    sig1 = []

    for f in freqs:
        mat1.set_frequency(f)
        sig1 += [mat1.sigma]
    mat1.clear_frequency()
    print(mat1.sigma == sig_0)

    plt.figure()
    plt.vlines(fc, sig_0, sig_fc, "r")
    plt.loglog(freqs, sig1)
    plt.savefig(fig_file+"A.png")


    mat2 = nrv.load_material("perineurium_horn")
    mat3 = nrv.load_material("epineurium_horn")
    sig2 = []
    for f in freqs:
        mat2.set_frequency(f)
        mat3.set_frequency(f)
        sig2 += [[mat2.sigma, mat3.sigma]]

    plt.figure()
    plt.loglog(freqs, sig2)
    plt.savefig(fig_file+"B.png")
    #plt.show()




