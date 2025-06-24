import nrv
import matplotlib.pyplot as plt
import numpy as np

np.random.seed(1234)

test_dir = "source_generators/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]

ofname = f"../{nrv.rmv_ext(__fname__)}.json"
n_ax = 22
l_f = 10000
d_f = 60


fascicle_1 = nrv.fascicle(diameter=d_f)
fascicle_1.define_length(l_f)
fascicle_1.fill(n_ax=n_ax)
print(fascicle_1.n_ax)


extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck",peri_mat="perineurium", epi_mat="epineurium", ext_mat="saline")

life_d = 25                                 #LIFE diamter in um
life_length = 1000                          #LIFE active-site length in um
life_x_offset = l_f/2     #x position of the LIFE (centered)
life_y_c_2 = 0                        #LIFE_2 y-coordinate (in um)
life_z_c_2 = 0                        #LIFE_1 z-coordinate (in um)

elec_2 = nrv.LIFE_electrode("LIFE_2", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2)

dummy_stim = nrv.stimulus()

#Attach electrodes to the extra_stim object 
extra_stim.add_electrode(elec_2, dummy_stim)
fascicle_1.attach_extracellular_stimulation(extra_stim)

fig, axs = plt.subplots(1, 2)

fascicle_1.plot(axes=axs[0])


fascicle_1.save(ofname, save=True)

del fascicle_1

plt.show()
