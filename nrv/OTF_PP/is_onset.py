################################
## rasterize membrane voltage ##
################################
nrv.rasterize(sim_results,'V_mem')

###############################
## remove non nevessary data ##
###############################
list_keys = ['ID', 'L', 'V_mem_raster_position', 'V_mem_raster_x_position', 'V_mem_raster_time_index', \
'V_mem_raster_time', 'myelinated', 'y', 'z','diameter','tstop','intra_stim_positions','extracellular_electrode_x','x_nodes','rec']

removable_keys = []
for key in sim_results:
    if not key in list_keys:
        removable_keys += [key]
for key in removable_keys:
    nrv.remove_key(sim_results,key, verbose=False)

####################################
## check if the axon fired or not ##
####################################
file_object = open(folder_name+'/onset_summary.csv', 'a')

ax_state = axon_state(sim_results, save=False)

N_AP=ax_state['onset number']
print(N_AP)
line = str(sim_results['ID'])+'\t'+\
		str(sim_results['y'])+'\t'+\
		str(sim_results['z'])+'\t'+\
		str(sim_results['diameter'])+'\t'+\
		str(sim_results['myelinated'])+'\t'+\
		str(N_AP)+'\n'
file_object.write(line)
file_object.close()
