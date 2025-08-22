# deprecated since at least v1.2.2
import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    diam = np.array([15,5,10,18,10])
    axon_type = np.array([1,1,1,1,1])

    delta  = 0

    y_axon = np.array([0,50,-40,10,-35])
    z_axon = np.array([0,10,-30,6,-30])

    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(y_axon))

    nrv.plot_population(diam, y_axon, z_axon,ax,size_plot,axon_type)
    fig.savefig('./unitary_tests/figures/514_pop_with_collisions.png')

    diam,y_axon,z_axon,axon_type = nrv.remove_collision(diam,y_axon,z_axon, axon_type, delta)

    fig, ax = plt.subplots(figsize=(8, 8))
    size_plot = 3*np.max(np.abs(y_axon))
    nrv.plot_population(diam, y_axon, z_axon,ax,size_plot,axon_type)

    diam,y_axon,z_axon,axon_type = nrv.remove_collision(diam,y_axon,z_axon, axon_type, delta)
    fig.savefig('./unitary_tests/figures/514_collisions_removed.png')
