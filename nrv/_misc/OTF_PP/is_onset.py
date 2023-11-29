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
    "tstop",
    "intra_stim_positions",
    "extracellular_electrode_x",
    "x_nodes",
    "rec",
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
ax_state = axon_state(axon_sim, save=False)
axon_sim["N_AP"] = ax_state["onset number"]
# print(N_AP)

################################
## Save results in a csv file ##
################################
if self.save_results:
    if "in_nerve" in kwargs:  # Nerve Simulation
        file_object = open(self.save_path + "/onset_summary.csv", "a")
        line = str(self.ID)
    else:  # Fascicle Simulation
        file_object = open(folder_name + "/onset_summary.csv", "a")
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
        + str(axon_sim["N_AP"])
        + "\n"
    )
    file_object.write(line)
    file_object.close()
