import nrv 
import numpy as np
import matplotlib.pyplot as plt

outer_d = 5         # in mm
nerve_d = 500       # in um
nerve_l = 5000      # in um
nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

fasc1_d = 300       # in um
fasc1_y = 0      # in um
fasc1_z = 0         # in um


#create the fascicle objects
fascicle_1 = nrv.fascicle(diameter=fasc1_d,ID=1)      
nerve.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)

n_ax = 500      #size of the axon population
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
fascicle_1.fill_with_population(axons_diameters, axons_type, delta=5, fit_to_size=True)

m_model = 'MRG'
um_model = 'Rattay_Aberham'
u_param = {"model": um_model}
m_param = {"model": m_model}

#For fascicle1
fascicle_1.set_axons_parameters(unmyelinated_only=True,**u_param)
fascicle_1.set_axons_parameters(myelinated_only=True,**m_param)


extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck",      #endoneurium conductivity
                                 peri_mat="perineurium",            #perineurium conductivity
                                 epi_mat="epineurium",              #epineurium conductivity
                                 ext_mat="saline")                  #saline solution conductivity

life_d = 25                                 #LIFE diamter in um
life_length = 1000                          #LIFE active-site length in um
life_x_offset = (nerve_l-life_length)/2     #x position of the LIFE (centered)

life_y_c_1 = fasc1_y                        #LIFE_1 y-coordinate (in um)
life_z_c_1 = fasc1_z                        #LIFE_1 z-coordinate (in um)


elec_1 = nrv.LIFE_electrode("LIFE_1", life_d, life_length, life_x_offset, life_y_c_1, life_z_c_1, ID = 1) # LIFE in the fascicle 1

t_start = 0.1       #start of the pulse, in ms
t_pulse = 0.1       #duration of the pulse, in ms
amp_pulse = 60      #amplitude of the pulse, in uA 

pulse_stim = nrv.stimulus()
pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      #cathodic pulse
extra_stim.add_electrode(elec_1, pulse_stim)
nerve.attach_extracellular_stimulation(extra_stim)
nerve.save("nerve_benchmark.json",intracel_context=True, extracel_context=True, rec_context=True)
