nrv.rasterize(sim_results,'V_mem')
nrv.filter_freq(sim_results,'V_mem',10)

plt.figure()
for node in range(len(sim_results['x_rec'])):
	plt.plot(sim_results['t'],sim_results['V_mem_filtered'][node]+100*node,color='k')
plt.xlabel('time (ms)')
plt.yticks([])
plt.ylabel('membrane voltage at Nodes of Ranvier allong axon')
title = 'Axon '+str(k)+', myelination is '+str(sim_results['myelinated'])+', '+str(sim_results['diameter'])+' um diameter'
plt.title(title)
plt.xlim(0,sim_results['tstop'])
plt.tight_layout()
fig_name = folder_name + '/Vmem_axon_'+str(k)+'.pdf'
plt.savefig(fig_name)
plt.close()

nrv.remove_key(sim_results,'V_mem', verbose=verbose)
nrv.remove_key(sim_results,'V_mem_filtered', verbose=verbose)
