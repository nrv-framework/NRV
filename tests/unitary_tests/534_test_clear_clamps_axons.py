import nrv 
import matplotlib.pyplot as plt

if __name__ == "__main__":
    y = 0                       # axon y position, in [um]
    z = 0                       # axon z position, in [um]
    d = 1                       # axon diameter, in [um]
    L = 5000                    # axon length, along x axis, in [um]
    axon1 = nrv.unmyelinated(y,z,d,L)

    ##Unmyelinated
    t_start = 0.5               # starting time, in [ms]
    duration = 0.25             # duration, in [ms]
    amplitude = 5               # amplitude, in [nA]
    relative_position = 0.5
    axon1.insert_I_Clamp(relative_position, t_start, duration, amplitude)
    um_results_intra1 = axon1.simulate(t_sim=5)
    axon1.clear_I_Clamp()
    um_results_no_stim = axon1.simulate(t_sim=5)
    axon1.insert_I_Clamp(relative_position, t_start, duration, amplitude)
    um_results_intra2 = axon1.simulate(t_sim=5)
    del axon1

    ##Myelinated
    d = 10
    L = nrv.get_length_from_nodes(d, 21)
    axon1 = nrv.myelinated(y, z, d, L, model="MRG",rec="all")
    axon1.insert_I_Clamp(0, t_start, duration, amplitude)
    axon1.insert_I_Clamp(relative_position, t_start, duration, amplitude)
    m_results_intra1 = axon1.simulate(t_sim=5)
    axon1.clear_I_Clamp()
    m_results_no_stim = axon1.simulate(t_sim=5)
    axon1.insert_I_Clamp(relative_position, t_start, duration, amplitude)
    m_results_intra2 = axon1.simulate(t_sim=5)

    assert(um_results_intra1.is_recruited() == True)
    assert(um_results_no_stim.is_recruited() == False)
    assert(um_results_intra2.is_recruited() == True)

    assert(m_results_intra1.is_recruited() == True)
    assert(m_results_no_stim.is_recruited() == False)
    assert(m_results_intra2.is_recruited() == True)

    fig,axs = plt.subplots(3,2)
    um_results_intra1.colormap_plot(axs[0,0])
    um_results_no_stim.colormap_plot(axs[1,0])
    um_results_intra2.colormap_plot(axs[2,0])

    m_results_intra1.colormap_plot(axs[0,1])
    m_results_no_stim.colormap_plot(axs[1,1])
    m_results_intra2.colormap_plot(axs[2,1])
    # plt.show()
    fig.savefig('./unitary_tests/figures/534_clear_clamps_axons.png')