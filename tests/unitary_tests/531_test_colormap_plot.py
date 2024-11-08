import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Generating full results
    ax = nrv.myelinated(L=21000, rec='all')
    ax.insert_I_Clamp(0, 0, 0.1, 2)
    res = ax(t_sim=5)
    del ax
    ax2 = nrv.unmyelinated(L=2000)
    ax2.insert_I_Clamp(0, 0, 0.1, 2)
    res2 = ax2(t_sim=5)
    del ax2

    fig, axs = plt.subplots(2, 1)
    res.colormap_plot(axs[0], "V_mem")
    axs[0].set_title("Myelinated axon")

    res2.colormap_plot(axs[1], "V_mem")
    axs[1].set_title("Unmyelinated axon")

    fig.tight_layout()
    fig.savefig('./unitary_tests/figures/531_colormaps.png')
