import nrv
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    model='Tigerholm'
    y = 0
    z = 0
    d = 1
    L = 5000
    Nrec = 100
    t_start = 1
    duration = 0.5
    amplitude = 2

    # test 1: 1 section stim in middle
    axon1 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
    axon1.insert_I_Clamp(0.5, t_start, duration, amplitude)
    results = axon1.simulate(t_sim=10,record_I_ions=True, record_particles=True)
    print(axon1.T == 37)
    del axon1

    if results['Simulation_state'] == 'Unsuccessful':
        print(results['Error_from_prompt'])

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/35_A.png')

    plt.figure()
    plt.plot(results['t'],results['V_mem'][25], label=str(round(results['x_rec'][25]))+'um')
    plt.plot(results['t'],results['V_mem'][50], label=str(round(results['x_rec'][50]))+'um')
    plt.plot(results['t'],results['V_mem'][75], label=str(round(results['x_rec'][75]))+'um')
    plt.xlabel('time (ms)')
    plt.ylabel('V membrane (mV)')
    plt.legend()
    plt.savefig('./unitary_tests/figures/35_B.png')

    fig, axs = plt.subplots(3)

    axs[0].plot(results['t'],results['V_mem'][25])
    axs[1].plot(results['t'],results['I_na'][25],label='I_na')
    axs[1].plot(results['t'],results['I_k'][25],label='I_k')
    axs[1].plot(results['t'],results['I_ca'][25],label='I_ca')

    axs[2].plot(results['t'], results['m_nav18'][25],label='m_nav18')
    axs[2].plot(results['t'], results['h_nav18'][25],label='h_nav18')
    axs[2].plot(results['t'], results['s_nav18'][25],label='s_nav18')
    axs[2].plot(results['t'], results['u_nav18'][25],label='u_nav18')
    axs[2].plot(results['t'], results['m_nav19'][25],label='m_nav19')
    axs[2].plot(results['t'], results['h_nav19'][25],label='h_nav19')
    axs[2].plot(results['t'], results['s_nav19'][25],label='s_nav19')
    axs[2].plot(results['t'], results['m_nattxs'][25],label='m_nattxs')
    axs[2].plot(results['t'], results['h_nattxs'][25],label='h_nattxs')
    axs[2].plot(results['t'], results['s_nattxs'][25],label='s_nattxs')
    axs[2].plot(results['t'], results['n_kdr'][25],label='m_kdr')
    axs[2].plot(results['t'], results['m_kf'][25],label='m_kf')
    axs[2].plot(results['t'], results['h_kf'][25],label='h_kf')
    axs[2].plot(results['t'], results['ns_ks'][25],label='ns_ks')
    axs[2].plot(results['t'], results['nf_ks'][25],label='nf_ks')
    axs[2].plot(results['t'], results['w_kna'][25],label='w_kna')
    axs[2].plot(results['t'], results['ns_h'][25],label='ns_h')
    axs[2].plot(results['t'], results['nf_h'][25],label='nf_h')
    plt.savefig('./unitary_tests/figures/35_C.png')
    del results

    # test 2: gmem for stim in left side
    cmtiger = 1
    gnabar_hh = 0.120
    gkbar_hh = 0.036
    gl_hh = 0.0003

    axon2 = nrv.unmyelinated(y,z,d,L,model=model,dt=0.001,Nrec=Nrec)
    axon2.insert_I_Clamp(0, t_start, duration, amplitude)
    results = axon2.simulate(t_sim=10, record_particles=True, record_g_ions=True, record_g_mem=True)
    print(axon2.T == 37)

    cm = axon2.get_membrane_capacitance()
    print(np.allclose(cm, cmtiger))
    del axon2

    #### Check results
    fc2 = results.compute_f_mem()
    fig2, ax1 = plt.subplots()
    ax1.set_xlabel('time (ms)')

    ax1.plot(results['t'],results['V_mem'][Nrec//2]-results['V_mem'][Nrec//2][0], 'k',label='Vmem variation')
    ax1.set_ylabel('Mem. Voltage (mV)')
    ax2 = ax1.twinx()
    ax1.legend(loc=2)

    ax2.plot(results['t'], results['g_nav17'][Nrec//2]*1000, label=r'$g_{nav17}$')
    ax2.plot(results['t'], results['g_nav18'][Nrec//2]*1000, label=r'$g_{nav18}$')
    ax2.plot(results['t'], results['g_nav19'][Nrec//2]*1000, label=r'$g_{nav19}$')
    ax2.plot(results['t'], results['g_kA'][Nrec//2]*1000, label=r'$g_{kA}$')
    ax2.plot(results['t'], results['g_kM'][Nrec//2]*1000, label=r'$g_{kM}$')
    ax2.plot(results['t'], results['g_kdr'][Nrec//2]*1000, label=r'$g_{kdr}$')
    ax2.plot(results['t'], results['g_kna'][Nrec//2]*1000, label=r'$g_{kna}$')
    ax2.plot(results['t'], results['g_h'][Nrec//2]*1000, label=r'$g_{h}$')
    ax2.plot(results['t'], results['g_naleak'][Nrec//2]*1000, label=r'$g_{naleak}$')
    ax2.plot(results['t'], results['g_kleak'][Nrec//2]*1000, label=r'$g_{kleak}$')
    ax2.plot(results['t'], results['g_mem'][Nrec//2]*1000, label=r'$g_{mem}$')
    ax2.set_ylabel(r'conductance ($mS.cm^{-2}$)')
    ax2.legend()
    fig2.savefig('./unitary_tests/figures/35_D.png')

    plt.figure(figsize=(9,7))
    plt.subplot(3,1,1)
    plt.plot(results['t'],results['V_mem'][Nrec//2])
    plt.xlabel('time (ms)')
    plt.ylabel('Mem. Voltage (mV)')
    plt.grid()
    plt.legend(title = 'polarisation')
    plt.subplot(3,1,2)
    plt.semilogy(results['t'],results['g_mem'][Nrec//2])
    plt.xlabel('time (ms)')
    plt.ylabel(r'$g_m$ ($mS\cdot cm^{-2}$)')
    plt.grid()
    plt.subplot(3,1,3)
    plt.semilogy(results['t'],results['f_mem'][Nrec//2])
    plt.xlabel('time (ms)')
    plt.ylabel(r'$f_{mem}$ ($Hz$)')
    plt.grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/35_E.png')

    #plt.show()