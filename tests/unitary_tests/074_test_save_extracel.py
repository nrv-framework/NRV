import nrv

# electrode def
x_elec = 10000/2				# electrode x position, in [um]
y_elec = 100				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]
E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)

# load material properties
endoneurium = nrv.load_material("endoneurium_ranck")
print(endoneurium.save_material())
# stimulus def
start = 1
I_cathod = 50
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3
stim1 = nrv.stimulus()
stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
#stim1.pulse(start, -I_cathod, duration = T_cathod)


# extracellular stimulation setup
extra_stim = nrv.stimulation(endoneurium)
extra_stim.add_electrode(E1, stim1)


extra_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/074_pointsources.json')

model = 'Nerve_1_Fascicle_1_LIFE'
FEM_stim = nrv.FEM_stimulation(model)
D_1 = 25
length_1 = 1000
y_c_1 = 0
z_c_1 = 0
x_1_offset = 4500
elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
stim = nrv.stimulus()
FEM_stim.add_electrode(elec_1, stim)

FEM_stim.save_extracel_context(save=True, fname='./unitary_tests/figures/074_LIFE.json')


