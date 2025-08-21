# deprecated since at least v1.2.2
import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    N = 250
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N,M_stat="Schellens_1")#,U_stat="Ochoa_U")

    y_axons, z_axons = nrv.axon_packer(axons_diameters,delta = 5,n_iter=15000)


    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(y_axons))
    nrv.plot_population(axons_diameters, y_axons, z_axons,ax=ax,size = size_plot,axon_type=axons_type)
    fig.savefig('./unitary_tests/figures/513_base.png')


    y_axons,z_axons = nrv.expand_pop(y_axons,z_axons,0.5)

    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(y_axons))
    nrv.plot_population(axons_diameters, y_axons, z_axons,ax=ax,size = size_plot,axon_type=axons_type)
    fig.savefig('./unitary_tests/figures/513_expanded.png')