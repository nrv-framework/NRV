import nrv
import matplotlib.pyplot as plt

# Generating full results
ax = nrv.myelinated(L=21000)

ax.insert_I_Clamp(0, 0, 0.1, 2)
res = ax(t_sim=5, record_I_mem=True, record_g_mem=True)


fig, axs = plt.subplots(3, 1)
res.plot_x_t(axs[0], "V_mem")
axs[0].set_xticks([])
axs[0].set_yticks([])
axs[0].set_ylabel("$V_{mem}$ along axon")

res.plot_x_t(axs[1], "I_mem")
axs[1].set_xticks([])
axs[1].set_yticks([])
axs[1].set_ylabel("$I_{mem}$ along axon")

res.plot_x_t(axs[2], "g_mem")
axs[2].set_yticks([])
axs[2].set_xlabel("time (ms)")
axs[2].set_ylabel("$g_{mem}$ along axon")
fig.savefig('./unitary_tests/figures/530_A.png')

fig, ax = plt.subplots()
res.raster_plot(ax, "V_mem")
ax.set_xlabel("time (ms)")
ax.set_ylabel("Spikes along axon")
fig.savefig('./unitary_tests/figures/530_B.png')


#plt.show()
