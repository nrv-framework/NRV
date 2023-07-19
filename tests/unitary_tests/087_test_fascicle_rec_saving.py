import nrv
import matplotlib.pyplot as plt

fascicle_file = "./unitary_tests/figures/087_fascicle.json"

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
fascicle_1 = nrv.fascicle(dt=5e-3)
fascicle_1.load(source_file)
fascicle_1.define_length(L)
fascicle_1.set_ID(82)
# intra cellular stimulation
fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)
fascicle_1.attach_extracellular_recorder(testrec)

#save/load

fascicle_1.save(fname=fascicle_file, intracel_context=True, rec_context=True)
print('fascicle saved')
fascicle_2, loadedrec = nrv.load_any_fascicle(fascicle_file, intracel_context=True, rec_context=True)
print('fascicle loaded')

# simulation
fascicle_2.simulate(t_sim=15, save_path='./unitary_tests/figures/')

if nrv.MCH.do_master_only_work():
    fig = plt.figure(figsize=(8,6))
    axs = []
    for k in range(len(loadedrec.recording_points)):
        axs.append(plt.subplot(3,1,k+1))
        axs[k].plot(loadedrec.t,loadedrec.recording_points[k].recording)
        axs[k].set_xlabel('time (ms)')
        axs[k].set_ylabel('elec. '+str(k)+' potential (mV)')
        axs[k].set_ylim(-0.06,0.03)
        axs[k].set_xlim(0,15)
        axs[k].grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/082.png')

    #plt.show()
