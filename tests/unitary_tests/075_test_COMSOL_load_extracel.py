import nrv



# load material properties
endoneurium = nrv.load_material('endoneurium_ranck')



# extracellular stimulation setup
extra_stim = nrv.stimulation(endoneurium)
extra_stim.load_extracel_context(data='./unitary_tests/sources/075_pointsources.json')

extra_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/075_pointsources.json')

if nrv.COMSOL_Status:
    my_model = 'Nerve_1_Fascicle_1_LIFE'
    FEM_stim = nrv.FEM_stimulation(my_model)
    FEM_stim.load_extracel_context(data='./unitary_tests/sources/075_LIFE.json')
    FEM_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/075_LIFE.json')
else:
    nrv.pass_info('not connected to COMSOL, parts of the test have been skiped')
