import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    t_sim = 10
    y = 0
    z = 0
    d = 10
    L = 40000

    #No block
    t_KES = t_sim - 2
    f_KES = 10
    start_KES = 1
    I_KES = 30
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)

    test_start = 6
    duration = 0.1
    amplitude = 2
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)

    # electrode
    x_elec = L/2                # electrode x position, in [um]
    y_elec = 100                # electrode y position, in [um]
    z_elec = 0                  # electrode y position, in [um]
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)


    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)

    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")

    fig, (ax1, ax2) = plt.subplots(2, 1)

    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])

    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")

    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")

    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)


    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')

    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_A.png')

    #Close to block -- AP collision
    I_KES = 50
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)

    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)

    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])

    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")

    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")

    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)


    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')

    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])

    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_B.png')

    #During refractory period
    I_KES = 80
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)
    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])
    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")
    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)
    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_C.png')


    #above block - AP jump
    I_KES = 102
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)
    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])
    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")
    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)
    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_D.png')


    #above block
    I_KES = 110
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)
    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])
    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")
    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)
    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_E.png')

    #No test AP
    I_KES = 50
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    #axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=t_sim)
    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])
    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")
    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)
    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_F.png')

    #AP not reaching end of simulation
    I_KES = 110
    stim_KES = nrv.stimulus()
    stim_KES.sinus(start_KES,t_KES,I_KES,f_KES)
    axon0 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes',Nseg_per_sec=1)
    axon0.insert_I_Clamp(0.05, test_start, duration, amplitude)
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    extra_stim = nrv.stimulation("endoneurium_ranck")
    extra_stim.add_electrode(E1, stim_KES)
    axon0.attach_extracellular_stimulation(extra_stim)
    results = axon0.simulate(t_sim=6.5)
    results.filter_freq("V_mem",f_KES, Q= 2)
    results.rasterize(V_mem_key = "V_mem_filtered")
    x_APs,_,t_APs,_ = results.split_APs("V_mem_filtered")
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for k in range(len(results['x_rec'])):
        ax1.plot(results['t'],results['V_mem_filtered'][k]+k*100, color='k')
    ax1.set_yticks([])
    ax1.set_xlabel('time (ms)')
    ax1.set_xlabel('Vmembrane')
    ax1.set_xlim(0,results['tstop'])
    print(f"Test AP blocked: {results.is_blocked(test_start,f_KES)}")
    ax2.scatter(results['V_mem_filtered_raster_time'],results['V_mem_filtered_raster_x_position'],s=80)
    for x_AP,t_AP in zip(x_APs,t_APs):
        ax2.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax2.scatter(t_start,x_start,s=10,c = 'k')
        ax2.scatter(t_xmax,x_max,s=10,c = 'g')
        ax2.scatter(t_xmin,x_min,s=10,c = 'b')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('x-position (µm)')
    ax2.set_xlim(0,results['tstop'])
    fig.tight_layout()
    plt.savefig('./unitary_tests/figures/527_G.png')


    #plt.show()
