if PostProc_Filtering is not None:
    filter_freq(axon_sim, "V_mem", PostProc_Filtering)
rasterize(axon_sim, "V_mem")
if not (save_V_mem) and self.record_V_mem:
    remove_key(axon_sim, "V_mem", verbose=self.verbose)
