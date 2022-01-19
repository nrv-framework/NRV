import nrv

DIR = './unitary_tests/'
source_file = DIR + 'figures/76_fascicle_1.json'

## Fascicle declaration
fascicle_1 = nrv.fascicle()
fascicle_1.load_fascicle_configuration(source_file,extracel_context=True)
fascicle_1.set_ID(75)


## stimulus def
start = 1
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

fascicle_1.change_stimulus_from_elecrode(0,stim1)

# simulation
fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/',postproc_script='Raster_plot', verbose=True, footprints=fascicle_1.footprints)
