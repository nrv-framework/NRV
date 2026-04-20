import nrv
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # axon def
    y = 0                        # axon y position, in [um]
    z = 0                        # axon z position, in [um]
    d = 1                        # axon diameter, in [um]
    L = 5000                    # axon length, along x axis, in [um]
    axon1 = nrv.unmyelinated(y,z,d,L)

    # electrode def
    x_elec1 = L/2
    x_elec2 = L*5/8
    x_elec3 = L*3/8
    y_elec = 100                # electrode y position, in [um]
    z_elec = 0                    # electrode y position, in [um]
    E1 = nrv.point_source_electrode(x_elec1,y_elec,z_elec)
    E2 = nrv.point_source_electrode(x_elec2,y_elec,z_elec)
    E3 = nrv.point_source_electrode(x_elec3,y_elec,z_elec)

    # load material properties
    epineurium = nrv.load_material('endoneurium_bhadra')

    # stimulus def
    start_1 = 1
    start_2 = 3
    start_3 = 3.1
    I_cathod = 500
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start_1, I_cathod, T_cathod, I_anod, T_inter)
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(start_2, I_cathod, T_cathod, I_anod, T_inter)
    stim3 = nrv.stimulus()
    stim3.biphasic_pulse(start_3, I_cathod, T_cathod, I_anod, T_inter)


    # extracellular stimulation setup
    extra_stim = nrv.stimulation(epineurium)
    extra_stim.add_electrode(E1, stim1)
    extra_stim.add_electrode(E2, stim2)
    extra_stim.add_electrode(E3, stim3)
    axon1.attach_extracellular_stimulation(extra_stim)

    # simulate the axon
    results = axon1.simulate(t_sim=5)
    del axon1

    plt.figure()
    map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('position (µm)')
    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.savefig('./unitary_tests/figures/16_A.png')
    # plt.show()