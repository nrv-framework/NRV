nrv.rasterize(axon_sim, "V_mem")


list_keys = [
    "ID",
    "L",
    "V_mem_raster_position",
    "V_mem_raster_x_position",
    "V_mem_raster_time_index",
    "V_mem_raster_time",
    "myelinateds",
    "intra_stim_starts",
    "intra_stim_positions",
]

removable_keys = []
for key in axon_sim:
    if not key in list_keys:
        removable_keys += [key]

for key in removable_keys:
    nrv.remove_key(axon_sim, key, verbose=self.verbose)
