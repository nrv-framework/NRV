import nrv
import matplotlib.pyplot as plt

#nrv.parameters.set_nrv_verbosity(4)
test_num = 304
fname = "./unitary_tests/figures/"+str(test_num)+"_nerve.json"
nerve = nrv.nerve(Length=10000)
nerve.set_ID(test_num)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=0, y=-20, z=-60, intracel_context=True, rec_context=True)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=1, z=65, intracel_context=True)
nerve.fit_circular_contour()
L = nerve.L



##################################
##### Intracellular context ######
##################################
position = 0.
t_start = 1
duration = 0.5
amplitude = 4
nerve.insert_I_Clamp(position, t_start, duration, amplitude)

##################################
####### recording context ########
##################################
testrec = nrv.recorder('endoneurium_bhadra')
testrec.set_recording_point(L/4, 0, 100)
testrec.set_recording_point(L/2, 0, 100)
testrec.set_recording_point(3*L/4, 0, 100)
nerve.attach_extracellular_recorder(testrec)
##################################
##### extracellular context ######
##################################
LIFE_stim = nrv.FEM_stimulation()
# ### Simulation box size
Outer_D = 5
LIFE_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
Nerve_D = 250
Fascicle_D = 220
LIFE_stim.reshape_nerve(Nerve_D, L)
LIFE_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 0
z_c_1 = 0
x_1_offset = (L-length_1)/2
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
LIFE_stim.add_electrode(elec_1, stim1)
nerve.attach_extracellular_stimulation(LIFE_stim)

nerve.save(save=True, fname=fname,intracel_context=True, extracel_context=True, rec_context=True)
del nerve

nrv.synchronize_processes()
nerve2 = nrv.nerve()
nerve2.load(data="./unitary_tests/figures/"+str(test_num)+"_nerve.json",intracel_context=True, extracel_context=True, rec_context=True)

nerve2.simulate(t_sim=10, save_path='./unitary_tests/figures/', postproc_script='rmv_keys')
loaded_rec = nerve2.recorder
if nrv.MCH.do_master_only_work():
    fig, ax = plt.subplots(figsize=(8,8))
    nerve2.plot(ax)
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

    fig = plt.figure(figsize=(8,6))
    axs = []
    for k in range(len(loaded_rec.recording_points)):
        axs.append(plt.subplot(3,2,k+1))
        axs[k].plot(loaded_rec.t,loaded_rec.recording_points[k].recording)
        axs[k].set_xlabel('time (ms)')
        axs[k].set_ylabel('elec. '+str(k)+' potential (mV)')
        axs[k].grid()
    plt.tight_layout()
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_C.png')
#plt.show()