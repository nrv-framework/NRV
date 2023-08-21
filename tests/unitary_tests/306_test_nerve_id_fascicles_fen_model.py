import nrv
import matplotlib.pyplot as plt

#nrv.parameters.set_nrv_verbosity(4)
test_num = 304
fname = "./unitary_tests/figures/"+str(test_num)+"_nerve.json"
nerve = nrv.nerve()
nerve.set_ID(test_num)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=1, y=-20, z=-60, intracel_context=True, rec_context=True)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=3, z=65, intracel_context=True)
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
start = 0
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
LIFE_stim.add_electrode(elec_1, stim1)
nerve.attach_extracellular_stimulation(LIFE_stim)


if nrv.MCH.do_master_only_work():
    nerve.compute_electrodes_footprints()
