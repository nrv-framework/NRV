import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    gnafbar_motor = 3.0 # S.cm-2
    gnapbar_motor = 0.01 # S.cm-2
    gksbar_motor = 0.08  # S.cm-2
    gkbar_motor = 0.02568
    gl_motor = 0.007  # S.cm-2

    gnafbar_sensory = gnafbar_motor
    gnapbar_sensory = gnapbar_motor
    gksbar_sensory = 0.04106  # S.cm-2
    gkbar_sensory = 0.02737
    gl_sensory = 0.006005  # S.cm-2
    cm= 2 # uF

    y = 0
    z = 0
    d = 10
    L = nrv.get_length_from_nodes(d, 15)

    print('Check Gaines_motor')
    axon1 = nrv.myelinated(y,z,d,L,dt=0.0005 ,Nseg_per_sec=1,rec='nodes', model='Gaines_motor')

    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp_node(2, t_start, duration, amplitude)

    t_sim=15
    results = axon1.simulate(t_sim=t_sim, record_particles=True, record_g_mem=True, record_g_ions=True)
    del axon1

    #### Check results

    gnaf_motor = gnafbar_motor*np.multiply(np.power(results['m'],3),results['h'])
    gnap_motor = gnapbar_motor*np.power(results['mp'],3)
    gks_motor = gksbar_motor*results['s']
    gk_motor = gkbar_motor * np.power(results['n'],4)

    gm_motor = gnaf_motor + gnap_motor + gks_motor + gk_motor + gl_motor  # en S.cm-2
    rm_motor = 1/gm_motor
    fc_motor = gm_motor/(2*np.pi*cm) * nrv.MHz


    print(np.allclose(gnaf_motor[:,:-1],results['g_na'][:,1:]))
    print(np.allclose(gnap_motor[:,:-1],results['g_nap'][:,1:]))
    print(np.allclose(gks_motor[:,:-1],results['g_k'][:,1:]))
    print(np.allclose(gks_motor[:,:-1],results['g_k'][:,1:]))

    print(np.allclose(gm_motor[:,:-1],results['g_mem'][:,1:]))

    print('Check Gaines_sensory')
    axon2 = nrv.myelinated(y,z,d,L,dt=0.0005 ,Nseg_per_sec=1,rec='nodes', model='Gaines_sensory')
    axon2.insert_I_Clamp_node(2, t_start, duration, amplitude)
    results2 = axon2.simulate(t_sim=t_sim, record_particles=True, record_g_mem=True, record_g_ions=True)
    del axon2

    #### Check results

    gnaf_sensory = gnafbar_sensory*np.multiply(np.power(results2['m'],3),results2['h'])
    gnap_sensory = gnapbar_sensory*np.power(results2['mp'],3)
    gks_sensory = gksbar_sensory*results2['s']
    gk_sensory = gkbar_sensory * np.power(results2['n'],4)

    gm_sensory = gnaf_sensory + gnap_sensory + gks_sensory + gk_sensory + gl_sensory  # en S.cm-2
    rm_sensory = 1/gm_sensory
    fc_sensory = gm_sensory/(2*np.pi*cm) * nrv.MHz

    print(np.allclose(gnaf_sensory[:,:-1],results2['g_na'][:,1:]))
    print(np.allclose(gnap_sensory[:,:-1],results2['g_nap'][:,1:]))
    print(np.allclose(gks_sensory[:,:-1],results2['g_k'][:,1:]))
    print(np.allclose(gks_sensory[:,:-1],results2['g_k'][:,1:]))

    print(np.allclose(gm_sensory[:,:-1],results2['g_mem'][:,1:]))


    results.compute_f_mem()
    print(np.allclose(fc_motor[:,:-1],results['f_mem'][:,1:]))
    results2.compute_f_mem()
    print(np.allclose(fc_sensory[:,:-1],results2['f_mem'][:,1:]))


    ##### Plots results

    mid_node = 5

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('time (ms)')
    ax1.plot(results['t'],results['V_mem'][mid_node]-results['V_mem'][mid_node][0], 'k',label='Vmem variation')
    ax1.set_ylabel('Mem. Voltage (mV)')
    ax2 = ax1.twinx()
    ax1.legend(loc=2)

    ax2.plot(results['t'], results['g_na'][mid_node]*1000, label=r'$g_{Na}$')
    ax2.plot(results['t'], results['g_nap'][mid_node]*1000, label=r'$g_{Nap}$')
    ax2.plot(results['t'], results['g_k'][mid_node]*1000, label=r'$g_{K}$')
    ax2.plot(results['t'], results['g_k'][mid_node]*1000, label=r'$g_{K}$')
    ax2.plot(results['t'], results['g_l'][mid_node]*1000, label=r'$g_{l}$')
    ax2.plot(results['t'], results['g_mem'][mid_node]*1000, label=r'$g_{mem}$')
    ax2.set_ylabel(r'conductance ($mS.cm^{-2}$)')
    ax2.legend()
    plt.xlim([0,5])
    plt.savefig('./unitary_tests/figures/93_A.png')



    fig, ax1 = plt.subplots()
    ax1.set_xlabel('time (ms)')
    ax1.plot(results['t'],results['V_mem'][mid_node]-results['V_mem'][mid_node][0], 'k',label='Vmem variation')
    ax1.set_ylabel('Mem. Voltage (mV)')
    ax2 = ax1.twinx()
    ax1.legend(loc=2)

    ax2.plot(results2['t'], results2['g_na'][mid_node]*1000, label=r'$g_{Na}$')
    ax2.plot(results2['t'], results2['g_nap'][mid_node]*1000, label=r'$g_{Nap}$')
    ax2.plot(results2['t'], results2['g_k'][mid_node]*1000, label=r'$g_{K}$')
    ax2.plot(results2['t'], results2['g_k'][mid_node]*1000, label=r'$g_{K}$')
    ax2.plot(results2['t'], results2['g_l'][mid_node]*1000, label=r'$g_{l}$')
    ax2.plot(results2['t'], results2['g_mem'][mid_node]*1000, label=r'$g_{mem}$')
    ax2.set_ylabel(r'conductance ($mS.cm^{-2}$)')
    ax2.legend()
    plt.xlim([0,5])
    plt.savefig('./unitary_tests/figures/93_B.png')


    plt.figure(figsize=(9,7))
    plt.subplot(3,1,1)
    plt.plot(results['t'],results['V_mem'][mid_node], label='motor')
    plt.plot(results2['t'],results2['V_mem'][mid_node], label='sensory')
    plt.xlabel('time (ms)')
    plt.ylabel('Mem. Voltage (mV)')
    plt.grid()
    plt.legend(title = 'polarisation')
    plt.subplot(3,1,2)
    plt.semilogy(results['t'],results['g_mem'][mid_node], label='motor')
    plt.semilogy(results2['t'],results2['g_mem'][mid_node], label='sensory')
    plt.xlabel('time (ms)')
    plt.ylabel(r'$g_m$ ($mS\cdot cm^{-2}$)')
    plt.grid()
    plt.subplot(3,1,3)
    plt.semilogy(results['t'],results['f_mem'][mid_node], label='motor')
    plt.semilogy(results2['t'],results2['f_mem'][mid_node], label='sensory')
    plt.xlabel('time (ms)')
    plt.ylabel(r'$f_{mem}$ ($Hz$)')
    plt.grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/93_C.png')

    #plt.show()