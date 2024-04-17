import matplotlib.pyplot as plt
import nrv

outer_d = 5 # mm
nerve_d = 500 # um
nerve_l = 5000 # um

fasc1_d = 200 # um
fasc1_y = -100
fasc1_z = 0

fasc2_d = 100 # um
fasc2_y = 100
fasc2_z = 0

nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

fascicle_1 = nrv.fascicle(diameter=fasc1_d,ID=1)      #we can add diameter here / no need to call define_circular_contour (not tested)
fascicle_2 = nrv.fascicle(diameter=fasc2_d, ID=2)

nerve.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)
nerve.add_fascicle(fascicle=fascicle_2, y=fasc2_y, z=fasc2_z)

fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve.plot(ax)

n_ax1 = 100
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax1, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
fascicle_1.fill_with_population(axons_diameters, axons_type, delta=5)

n_ax1 = 100
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax1, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
fascicle_2.fill_with_population(axons_diameters, axons_type, delta=5, )

fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve.plot(ax)

fascicle_1.fit_population_to_size(delta = 1)        #else set True in fill_with_population - Note: Pb with "barycenter"
fig, ax = plt.subplots(1, 1, figsize=(6,6))     
nerve.plot(ax)

life_d = 25
life_length = 1000
life_x_offset = (nerve_l-life_length)/2

life_y_c_0 = 0
life_z_c_0 = 100
life_y_c_1 = fasc1_y
life_z_c_1 = fasc1_z
life_y_c_2 = fasc2_y
life_z_c_2 = fasc2_z

dummy_stim = nrv.stimulus()
dummy_stim.pulse(0.1, 0.2, 5)

# LIFE in neither of the two fascicles
stims = nrv.FEM_stimulation()

elec_0 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_offset, life_y_c_0, life_z_c_0)
stims.add_electrode(elec_0, dummy_stim)

# LIFE in the fascicle 1
elec_1 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_offset, life_y_c_1, life_z_c_1)
stims.add_electrode(elec_1, dummy_stim)

# LIFE in the fascicle 2
elec_2 = nrv.LIFE_electrode("LIFE", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2)
stims.add_electrode(elec_2, dummy_stim)


nerve.attach_extracellular_stimulation(stims)
fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve.plot(ax)

plt.show()
exit()
nerve.simulate(t_sim=1)#, save_path='./', postproc_script="default")

