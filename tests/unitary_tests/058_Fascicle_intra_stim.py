import nrv
from sources.OTF_PP_stim_intra import stim_intra

# Fascicle config
L = 10000 			# length, in um
source_file = './unitary_tests/sources/56_fasc.json'
# intra cellular stimulation parameters
position = 0.5
t_start = 1
duration = 0.5
amplitude = 4

# Fascicle declaration
fascicle_1 = nrv.fascicle()
fascicle_1.load(source_file)
fascicle_1.define_length(L)
fascicle_1.set_ID(58)
# intra cellular stimulation 
fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)
# simulation
fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/',postproc_script=stim_intra)