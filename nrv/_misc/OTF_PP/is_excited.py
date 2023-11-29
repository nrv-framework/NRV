################################
## rasterize membrane voltage ##
################################
nrv.rasterize(axon_sim, "V_mem")

###############################
## remove non nevessary data ##
###############################
list_keys = [
    "ID",
    "L",
    "V_mem_raster_position",
    "V_mem_raster_x_position",
    "V_mem_raster_time_index",
    "V_mem_raster_time",
    "myelinated",
    "y",
    "z",
    "diameter",
]
removable_keys = []
for key in axon_sim:
    if not key in list_keys:
        removable_keys += [key]
for key in removable_keys:
    nrv.remove_key(axon_sim, key, verbose=False)

####################################
## check if the axon fired or not ##
####################################
if len(axon_sim["V_mem_raster_position"]) == 0:
    # no spike
    axon_sim['spike'] = 0
else:
    axon_sim['spike'] = 1

################################
## Save results in a csv file ##
################################
if self.save_results:
    if "in_nerve" in kwargs:  # Nerve Simulation
        file_object = open(self.save_path + "/spike_summary.csv", "a")
        line = str(self.ID)
    else:  # Fascicle Simulation
        file_object = open(folder_name + "/spike_summary.csv", "a")
        line = ""


    line += (
        str(axon_sim["ID"])
        + "\t"
        + str(axon_sim["y"])
        + "\t"
        + str(axon_sim["z"])
        + "\t"
        + str(axon_sim["diameter"])
        + "\t"
        + str(axon_sim["myelinated"])
        + "\t"
        + str(axon_sim['spike'])
        + "\n"
    )

    file_object.write(line)
    file_object.close()
