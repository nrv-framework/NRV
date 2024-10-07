import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

DIR = './unitary_tests/'


LIFEfile = DIR + 'figures/76_fascicle_LIFE.json'

PSfile = DIR + 'figures/76_fascicle_PS.json'

N = 75
t_start = time.time()
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N, M_stat="Ochoa_M")


t1 = time.time()

print('Population of '+str(N)+' axons generated in '+str(t1 - t_start)+' s')


D = 500				# diameter, in um
L = 10000 			# length, in um

fascicle_1 = nrv.fascicle(ID=76)
fascicle_1.define_length(L)
fascicle_1.define_circular_contour(D)
fascicle_1.fill_with_population(axons_diameters, axons_type, delta=0.4)
fascicle_1.fit_circular_contour(delta = 0.1)
fascicle_1.generate_random_NoR_position()
t2 = time.time()

print('Filled fascicle generated in '+str(t2 - t1)+' s')



## Point source electrode definition
x_elec = L/2				# electrode x position, in [um]
y_elec = 500				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]
elec_2 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
# load material properties
epineurium = nrv.load_material('endoneurium_bhadra')
extra_stim = nrv.stimulation(epineurium)
# stimulus def
stim1 = nrv.stimulus()

extra_stim.add_electrode(elec_2, stim1)

fascicle_1.attach_extracellular_stimulation(extra_stim)
footprints = fascicle_1.compute_electrodes_footprints()
fascicle_1.save_fascicle_configuration(PSfile,extracel_context=True)



t5 = time.time()
print('PS fascicle saved '+str(t5 - t_start)+' s')

fig, ax = plt.subplots(figsize=(6,6))
fascicle_1.plot(ax, num=True)
plt.savefig(DIR + 'figures/76_A.png')

my_model = 'Nerve_1_Fascicle_1_LIFE'

###########################
##### LIFE elecrtode ######
###########################

if nrv.COMSOL_Status:
    LIFE_stim = nrv.FEM_stimulation(my_model)
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
    stim1 = nrv.stimulus()
    LIFE_stim.add_electrode(elec_1, stim1)
    fascicle_1.attach_extracellular_stimulation(LIFE_stim)
    ##########################
    ## Fascicle declaration ##
    ##########################

    t3 = time.time()
    print('Extracel context generated in '+str(t3 - t2)+' s')
    #Footprint saving
    footprints = fascicle_1.compute_electrodes_footprints()

    t4 = time.time()
    print('Electrod footprint generated in '+str(t4 - t3)+' s')

    fascicle_1.save_fascicle_configuration(LIFEfile,extracel_context=True)

    t6 = time.time()
    print('Total time '+str(t6 - t_start)+' s')

    fig, ax = plt.subplots(figsize=(6,6))
    fascicle_1.plot( ax, num=True)
    plt.savefig(DIR + 'figures/76_B.png')
else:
    nrv.pass_info('not connected to COMSOL, parts of the test have been skiped')
