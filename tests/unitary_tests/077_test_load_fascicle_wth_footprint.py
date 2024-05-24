import nrv
import matplotlib.pyplot as plt

nrv.parameters.set_nrv_verbosity(2)
DIR = './unitary_tests/'
source_file = DIR + 'sources/77_fascicle_1.json'
#source_file =  DIR + 'figures/76_fascicle_PS.json'
figfile = DIR + 'figures/77_A.png'

## Fascicle declaration
fascicle_1 = nrv.fascicle()
fascicle_1.load(source_file,extracel_context=True)
fascicle_1.set_ID(77)
fig, ax = plt.subplots(figsize=(6,6))
fascicle_1.plot(ax, num=True)
plt.savefig(figfile)



## stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

fascicle_1.change_stimulus_from_electrode(0,stim1)
# simulation

fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/', verbose=True, loaded_footprints=True)
