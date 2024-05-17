import nrv
import time

t0 = time.time()
source_file = './unitary_tests/sources/56_fasc.json'
Ntest = 144
###########################
## extracellular context ##
###########################

# ### Simulation box size
Outer_D = 5
#### Nerve and fascicle geometry
L = 10000
Nerve_D = 250
Fascicle_D = 220
##### electrode and stimulus definition
D_1 = 25
length_1 = 1000
y_c_1 = 50
z_c_1 = 50
x_1_offset = 4500

# stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.FEM_stimulation(Ncore=False)
stim1.reshape_outerBox(Outer_D)
stim1.reshape_nerve(Nerve_D, L)
stim1.reshape_fascicle(Fascicle_D)#, res=220/10)
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
stim = nrv.stimulus()
stim.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
stim1.add_electrode(elec_1, stim)


fascicle_1 = nrv.fascicle()
fascicle_1.load(source_file)
fascicle_1.define_length(L)
fascicle_1.set_ID(Ntest*10)
fascicle_1.attach_extracellular_stimulation(stim1)
fascicle_2 = nrv.load_any(fascicle_1.save(save=False))


#print(fascicle_1.extra_stim.model.is_multi_proc)
fascicle_1.compute_electrodes_footprints()

if nrv.MCH.do_master_only_work():
    _, _, _, t_fem = fascicle_1.extra_stim.model.get_timers(verbose=False)
del fascicle_1



#stim2 = nrv.load_any(stim1.save())
stim2 = nrv.FEM_stimulation(Ncore=True)
stim2.reshape_outerBox(Outer_D)
stim2.reshape_nerve(Nerve_D, L)
stim2.reshape_fascicle(Fascicle_D)
stim2.add_electrode(elec_1, stim)

fascicle_2.set_ID(Ntest*10+1)
fascicle_2.attach_extracellular_stimulation(stim2)
fascicle_2.compute_electrodes_footprints()
if nrv.MCH.do_master_only_work():
    _, _, _, t_fem_mp = fascicle_2.extra_stim.model.get_timers(verbose=False)
    n_proc = fascicle_2.extra_stim.model.Ncore
    print(f"Single proc simulation : {t_fem} s\n {n_proc}-proc simulation:{t_fem_mp} s")


#fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/',postproc_script='is_excited')

nrv.synchronize_processes()
