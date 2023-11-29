nrv.rasterize(axon_sim, "V_mem")
nrv.remove_key(axon_sim, "V_mem", verbose=self.verbose)

plt.figure()
plt.scatter(axon_sim["V_mem_raster_time"], axon_sim["V_mem_raster_x_position"])
plt.xlabel("time (ms)")
plt.ylabel("position along the axon($\mu m$)")
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
plt.ylim(0, axon_sim["L"])
if self.save_results:
    plt.tight_layout()
    fig_name = folder_name + "/Activity_axon_" + str(k) + ".pdf"
    plt.savefig(fig_name)
    plt.close()
