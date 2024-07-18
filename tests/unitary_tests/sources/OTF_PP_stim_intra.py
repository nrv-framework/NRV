import nrv
import matplotlib.pyplot as plt

def stim_intra(results:nrv.axon_results, save:bool=False, fpath:str=""):
    results.rasterize('V_mem')
    results.remove_key('V_mem')

    fig, ax = plt.subplots()
    ax.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'])
    plt.xlabel('time (ms)')
    plt.ylabel(r'position along the axon($\mu m$)')
    title = 'Axon '+str(results.ID)+', myelination is '+str(results['myelinated'])+', '+str(results['diameter'])+' um diameter'
    plt.title(title)
    plt.xlim(0,results['tstop'])
    plt.ylim(0,results['L'])
    plt.tight_layout()
    if save:
        fig_name = fpath + f'/Activity_axon_{results.ID}.pdf'
        plt.savefig(fig_name)
    plt.close()
    return results
