if PostProc_Filtering is not None:
    filter_freq(sim_results, 'V_mem', PostProc_Filtering)
rasterize(sim_results, 'V_mem')
if not(save_V_mem) and record_V_mem:
    remove_key(sim_results, 'V_mem', verbose=verbose)
