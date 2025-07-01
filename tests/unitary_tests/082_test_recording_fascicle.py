import nrv
import matplotlib.pyplot as plt


if __name__ == '__main__':

    # Fascicle config
    L = 10000           # length, in um
    source_file = './unitary_tests/sources/56_fasc.json'
    # intra cellular stimulation parameters
    position = 0.
    t_start = 1
    duration = 0.5
    amplitude = 4


    # test recording
    testrec = nrv.recorder('endoneurium_bhadra')
    testrec.set_recording_point(L/4, 0, 100)
    testrec.set_recording_point(L/2, 0, 100)
    testrec.set_recording_point(3*L/4, 0, 100)


    # Fascicle declaration
    fascicle_1 = nrv.fascicle()
    fascicle_1.load(source_file)
    fascicle_1.define_length(L)
    fascicle_1.set_ID(82)
    # intra cellular stimulation
    fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)
    fascicle_1.attach_extracellular_recorder(testrec)
    # simulation
    fascicle_1.simulate(t_sim=15, dt=5e-3)
    print(fascicle_1.unmyelinated_param)
    fig = plt.figure(figsize=(8,6))
    axs = []
  
    for k in range(len(testrec.recording_points)):
        axs.append(plt.subplot(3,1,k+1))
        axs[k].plot(testrec.t,testrec.recording_points[k].recording)
        axs[k].set_xlabel('time (ms)')
        axs[k].set_ylabel('elec. '+str(k)+' potential (mV)')
        axs[k].set_ylim(-0.06,0.03)
        axs[k].set_xlim(0,15)
        axs[k].grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/082_A.png')

    del fascicle_1, testrec


    # Fascicle declaration
    testrec2 = nrv.recorder('endoneurium_bhadra')
    for d in [ 300, 500]:
        testrec2.set_recording_point(L/4, 0, d)
        testrec2.set_recording_point(L/2, 0, d)
        testrec2.set_recording_point(3*L/4, 0, d)

    fascicle_1 = nrv.load_fascicle(source_file)
    fascicle_1.define_length(L)
    fascicle_1.set_ID(82)
    # intra cellular stimulation
    fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)
    fascicle_1.attach_extracellular_recorder(testrec2)
    # simulation
    fascicle_1.simulate(t_sim=15, dt=5e-3)

    # fig = plt.figure(figsize=(8,6))
    # axs = []
  
    for k in range(len(testrec2.recording_points)):
        # axs.append(plt.subplot(3,1,k+1))
        axs[k%len(axs)].plot(testrec2.t,testrec2.recording_points[k].recording)
        axs[k%len(axs)].set_xlabel('time (ms)')
        axs[k%len(axs)].set_ylabel('elec. '+str(k)+' potential (mV)')
        # axs[k%len(axs)].set_ylim(-0.01,0.01)
        # axs[k%len(axs)].set_xlim(2,15)
        axs[k%len(axs)].grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/082_B.png')

    # plt.show()
    del fascicle_1, testrec2


