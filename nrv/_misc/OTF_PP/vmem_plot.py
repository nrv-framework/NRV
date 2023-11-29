nrv.rasterize(axon_sim, "V_mem")
nrv.filter_freq(axon_sim, "V_mem", 10)

plt.figure()
for node in range(len(axon_sim["x_rec"])):
    plt.plot(
        axon_sim["t"], axon_sim["V_mem_filtered"][node] + 100 * node, color="k"
    )
plt.xlabel("time (ms)")
plt.yticks([])
plt.ylabel("membrane voltage at Nodes of Ranvier allong axon")
title = (
    "Axon "
    + str(k)
    + ", myelination is "
    + str(axon_sim["myelinated"])
    + ", "
    + str(axon_sim["diameter"])
    + " um diameter"
)
plt.title(title)
plt.xlim(0, axon_sim["tstop"])
plt.tight_layout()
if self.save_results:
    fig_name = folder_name + "/Vmem_axon_" + str(k) + ".pdf"
    plt.savefig(fig_name)
    plt.close()

nrv.remove_key(axon_sim, "V_mem", verbose=self.verbose)
nrv.remove_key(axon_sim, "V_mem_filtered", verbose=self.verbose)
