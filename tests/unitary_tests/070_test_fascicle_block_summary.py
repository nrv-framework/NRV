import nrv
import numpy as np
import matplotlib.pyplot as plt

import nrv
import matplotlib.pyplot as plt

#nrv.parameters.set_nrv_verbosity(4)
# Fascicle config
dt = 0.001
t_sim = 25
L = 10000 			# length, in um
source_file = './unitary_tests/sources/56_fasc.json'
ID = 70


# extra cellular stimulation parameters
# electrode def
x_elec = L/2				# electrode x position, in [um]
y_elec = 0				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
# load material properties
epineurium = nrv.load_material('endoneurium_ranck')
# stimulus def

block_freq = 10
block_start=0 #ms
block_duration=t_sim #ms
block_amp=10 #µA
block_offset = 0
stim_modulated = nrv.stimulus()
stim_modulated.sinus(block_start, block_duration, block_amp, block_freq,dt=dt)


# extracellular stimulation setup
extra_stim = nrv.stimulation(epineurium)
extra_stim.add_electrode(E1, stim_modulated)

# Iclamp test
position = 0.01
t_start = 5
duration = 0.1
amplitude = 3


# Fascicle declaration
fascicle_1 = nrv.fascicle(dt=dt)
fascicle_1.load(source_file)
fascicle_1.define_length(L)
fascicle_1.set_ID(ID)
# HFBS extra stimulation
fascicle_1.attach_extracellular_stimulation(extra_stim)

# Iclamp test 
fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)

# simulation
fascicle_1.verbose = True
f_results = fascicle_1.simulate(t_sim=t_sim, verbose=False, postproc_script = "is_blocked", postproc_kwargs = {"freq":block_freq, "AP_start":t_start})#,save_path='./unitary_tests/figures/')

#f_results.save(save=True,fname="test.json")
#f_results = nrv.load_any("test.json")

if nrv.MCH.do_master_only_work():
    fig,ax = plt.subplots(1)
    fig.set_size_inches(5, 5)
    f_results.plot_block_summary(ax, AP_start = t_start, freq = block_freq, num=True)

    fig.tight_layout()
    fig.savefig("./unitary_tests/figures/70_A.png")
#plt.show()

#print(f_results)
#DIR = './unitary_tests/figures/Fascicle_'+str(ID)+'/'


"""
fasc_state = nrv.fascicular_state(DIR, save=True, saving_file=DIR+"70_Facsicular_state.json")

if nrv.MCH.do_master_only_work():
    fig, ax = plt.subplots(figsize=(8,8))
    nrv.plot_fasc_state(fasc_state, ax, num=True)
    plt.savefig("./unitary_tests/figures/70_A.png")

"""