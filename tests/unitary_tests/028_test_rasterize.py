import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 20000

    ########## test A : myelinated record all #############
    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')

    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+0.5, duration, amplitude)
    #axon1.insert_I_Clamp(0.5, t_start+1.0, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+2.5, duration, amplitude)
    axon1.insert_I_Clamp(0.5, t_start+5.5, duration, amplitude)

    results = axon1.simulate(t_sim=8)
    del axon1
    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/28_A.png')

    results.rasterize()

    plt.figure()
    plt.scatter(results['V_mem_raster_time'],results['V_mem_raster_x_position'])
    plt.xlabel('time (ms)')
    plt.ylabel(r'position along the axon($\mu m$)')
    plt.xlim(0,results['tstop'])
    plt.savefig('./unitary_tests/figures/28_B.png')


    ########## test B : myelinated record nodes #############
    axon2 = nrv.myelinated(y,z,d,L,dt=0.001,rec='nodes')
    axon2.insert_I_Clamp(0.5, t_start, duration, amplitude)

    results2 = axon2.simulate(t_sim=6)
    del axon2

    plt.figure()
    for k in range(len(results2['x_rec'])):
        plt.plot(results2['t'],results2['V_mem'][k]+100*k)
    plt.yticks([])
    plt.savefig('./unitary_tests/figures/28_C.png')

    results2.rasterize(t_min_AP=0.1,t_refractory=2, threshold = -10)

    plt.figure()
    plt.scatter(results2['V_mem_raster_time'],results2['V_mem_raster_x_position'])
    plt.xlabel('time (ms)')
    plt.ylabel(r'position along the axon($\mu m$)')
    plt.xlim(0,results2['tstop'])
    plt.savefig('./unitary_tests/figures/28_D.png')

    ########## test C : unmyelinated #############
    y = 0
    z = 0
    d = 1
    L = 500

    t_start = 1
    duration = 0.2
    amplitude = 1

    axon3 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nseg_per_sec = 99)
    axon3.insert_I_Clamp(0.5, t_start, duration, amplitude)
    results3 = axon3.simulate(t_sim=4)
    del axon3

    plt.figure()
    map = plt.pcolormesh(results3['t'], results3['x_rec'], results3['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/28_E.png')

    results3.rasterize()

    plt.figure()
    plt.scatter(results3['V_mem_raster_time'],results3['V_mem_raster_x_position'])
    plt.xlabel('time (ms)')
    plt.ylabel(r'position along the axon($\mu m$)')
    plt.xlim(0,results3['tstop'])
    plt.savefig('./unitary_tests/figures/28_F.png')


    # plt.show()