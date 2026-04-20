import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # axon def
    y = 0                                # axon y position, in [um]
    z = 0                                # axon z position, in [um]
    d = 10                                # axon diameter, in [um]
    L = nrv.get_length_from_nodes(d,51)    # get length to have exactly 51 nodes
    dt = 0.005
    axon1 = nrv.myelinated(y,z,d,L,T=37,rec='nodes',dt=0.005,model='Gaines_sensory')


    # load material properties
    epineurium = nrv.load_material('endoneurium_bhadra')

    #print(axon1.axonnodes)
    #stimulus Block
    block_start=0.1 #ms
    block_duration=0.9 #ms
    block_amp=900 #µA
    block_freq=10 #kHz

    # Block electrode
    x_elec = axon1.x_nodes[25]
    y_elec = 1000
    z_elec = 0
    E = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    stim = nrv.stimulus()
    stim.sinus(block_start, block_duration, block_amp, block_freq,dt=1/(block_freq*40))

    ### define extra cellular stimulation
    extra_stim = nrv.stimulation(epineurium)
    extra_stim.add_electrode(E, stim)
    extra_stim.synchronise_stimuli()
    axon1.attach_extracellular_stimulation(extra_stim)


    results = axon1.simulate(t_sim=30, record_particles=True,record_I_ions=True,)
    #del axon1
    print('Simulation performed in '+str(results['sim_time'])+' s')


    delta_t = np.diff(results['t'])
    print(axon1.dt<dt)
    print(np.min(delta_t))
    print(np.max(delta_t))
    plt.figure()
    plt.plot(delta_t-axon1.dt)
    plt.savefig('./unitary_tests/figures/39_A.png')

    # plt.show()