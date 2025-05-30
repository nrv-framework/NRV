import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    test_num = 304
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(test_num)
    nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=1, y=-20, z=-60, intracel_context=True, rec_context=True)
    nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=3, z=65, intracel_context=True)
    nerve.fit_circular_contour()
    L = nerve.L



    position = 0.5
    t_start = 1
    duration = 0.5
    amplitude = 4
    nerve.insert_I_Clamp(position, t_start, duration, amplitude)



    testrec = nrv.recorder('endoneurium_bhadra')
    testrec.set_recording_point(L/4, 0, 0)
    testrec.set_recording_point(L/2, 0, 0)
    testrec.set_recording_point(3*L/4, 0, 0)
    nerve.attach_extracellular_recorder(testrec)

    nerve.simulate(t_sim=10, save_path='./unitary_tests/figures/', postproc_script='rmv_keys')
    loaded_rec = nerve.recorder
    fig, ax = plt.subplots(figsize=(8,8))
    nerve.plot(ax)
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

    fig = plt.figure(figsize=(8,4))
    axs = []
    for k in range(len(loaded_rec.recording_points)):
        coordinate = (loaded_rec.recording_points[k].x, loaded_rec.recording_points[k].y, loaded_rec.recording_points[k].z)
        axs.append(plt.subplot(2, 3, k+1))
        axs[k].plot(loaded_rec.t,loaded_rec.recording_points[k].recording, label=str(coordinate))
        axs[k].set_xlabel('time (ms)')
        axs[k].set_ylabel(f'elec. potential (mV)')
        axs[k].legend()
        axs[k].grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_C.png')
#plt.show()