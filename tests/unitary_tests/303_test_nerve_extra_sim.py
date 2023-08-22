import nrv
import matplotlib.pyplot as plt
import time
import numpy as np

#nrv.parameters.set_nrv_verbosity(4)

t0 = time.time()
test_num = 303
source_file = './unitary_tests/sources/56_fasc.json'
nerve = nrv.nerve()
nerve.set_ID(test_num)

nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=0, y=-20, z=-60)#, extracel_context=True)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=1, z=65, extracel_context=True)
nerve.fit_circular_contour()



LIFE_stim = nrv.FEM_stimulation()
#### Simulation box size
Outer_D = 5
LIFE_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
Nerve_D = 250
Fascicle_D = 220
LIFE_stim.reshape_nerve(Nerve_D, 10000)
LIFE_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 0
z_c_1 = 0
x_1_offset = (length_1)/2
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
# stimulus def
freq = 10
amp = 10
start = 0
duration = 10
stim1 = nrv.stimulus()
stim1.sinus(start=start, duration=duration, amplitude=amp, freq=freq, dt=0.001)
stim1.t = np.round(stim1.t, 4)
LIFE_stim.add_electrode(elec_1, stim1)

nerve.attach_extracellular_stimulation(LIFE_stim)
#nerve.compute_electrodes_footprints()


start = 0
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 100e-3
T_inter = 50e-3
stim2 = nrv.stimulus()
stim2.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
stim2.t = np.round(stim2.t, 4)
nerve.change_stimulus_from_elecrode(1,stimulus=stim2)

t1 = time.time()
if nrv.MCH.do_master_only_work():
    print("Nerve preparation time "+str(t1-t0))

nerve.simulate(t_sim=5, save_path='./unitary_tests/figures/', postproc_script="vmem_plot")
t2 = time.time()
if nrv.MCH.do_master_only_work():
    print("Nerve simulation time "+str(t2-t1))
    
    fig, ax = plt.subplots(figsize=(8,8))
    nerve.plot(fig, ax)
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

#plt.show()
