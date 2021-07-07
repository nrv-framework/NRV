nrv.rasterize(sim_results,'V_mem')
nrv.remove_key(sim_results,'V_mem')

plt.figure()
plt.scatter(sim_results['V_mem_raster_time'],sim_results['V_mem_raster_x_position'])
plt.xlabel('time (ms)')
plt.ylabel('position along the axon($\mu m$)')
title = 'Axon '+str(k)+', myelination is '+str(sim_results['myelinated'])+', '+str(sim_results['diameter'])+' um diameter'
plt.title(title)
plt.xlim(0,sim_results['tstop'])
plt.ylim(0,sim_results['L'])
plt.tight_layout()
fig_name = './unitary_tests/figures/Fascicle_59/Activity_axon_'+str(k)+'.pdf'
plt.savefig(fig_name)
plt.close()