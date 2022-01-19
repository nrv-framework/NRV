from pandas.core.construction import extract_array
import nrv



# load material properties
endoneurium = nrv.load_material('endoneurium_ranck')



# extracellular stimulation setup
extra_stim = nrv.stimulation(endoneurium)
extra_stim.load_extracel_context(data='./unitary_tests/figures/074_pointsources.json')

extra_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/075_pointsources.json')

my_model = 'Nerve_1_Fascicle_1_LIFE'
FEM_stim = nrv.FEM_stimulation(my_model)
FEM_stim.load_extracel_context(data='./unitary_tests/figures/074_LIFE.json')
FEM_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/075_LIFE.json')
