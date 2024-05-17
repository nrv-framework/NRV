Example 8: KES propagation Block of unmyelinated fiber
======================================================

This file shows an example of action potential propagation block with an
unmyelinated fiber.

.. code:: ipython3

    import nrv
    import numpy as np
    import matplotlib.pyplot as plt
    
    
    model = 'Tigerholm'
    diam = 1
    y = 0
    z = 0
    print(diam)
    
    L = 10000
    
    t_sim = 50
    t_position=0.05
    t_start=20
    t_duration=1
    t_amplitude=1
    
    b_start = 3
    b_duration = t_sim
    block_amp = 20000
    block_freq = 10
    dt = 1/(20*block_freq)
    nseg_per_l = 50
    n_seg = np.int32(nseg_per_l*L/1000)
    print(n_seg)
    material = nrv.load_material('endoneurium_bhadra')
    
    y_elec = 500
    z_elec = 0
    x_elec = L/2
    
    axon1 = nrv.unmyelinated(y,z,diam,L,model=model,Nseg_per_sec=n_seg,dt=dt)
    
    
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    stim_1=nrv.stimulus()
    stim_1.sinus(b_start, b_duration, block_amp, block_freq ,dt=1/(block_freq*20))
    stim_extra = nrv.stimulation(material)
    stim_extra.add_electrode(E1,stim_1)
    axon1.attach_extracellular_stimulation(stim_extra)
    
    axon1.insert_I_Clamp(t_position, t_start, t_duration, t_amplitude)       
    
    
    # simulate axon activity
    results = axon1.simulate(t_sim=t_sim)
    nrv.filter_freq(results,'V_mem',block_freq)
    nrv.rasterize(results,'V_mem_filtered',t_refractory=1,t_stop=b_duration)
    position_list = []
    position_list.append(np.array((results['V_mem_filtered_raster_position'])))
    position_list=np.concatenate(position_list)
    spike_number=nrv.count_spike(position_list)
    print(spike_number)
    
    #nrv.filter_freq(results,'V_mem',block_freq)
    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem_filtered'] ,shading='auto')
    plt.xlabel('Time (ms)')
    plt.ylabel('x-position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('Membrane Voltage $V_m$  (mV)')
    plt.tight_layout()
    plt.show()
    
    



.. parsed-literal::

    1
    500
    2



.. image:: 8_KES_block_unmyelinated_files/8_KES_block_unmyelinated_1_1.png

