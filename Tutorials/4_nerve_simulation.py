import matplotlib.pyplot as plt
import sys
sys.path.append("../")
import numpy as np
import nrv

outer_d = 5         # in mm
nerve_d = 500       # in um
nerve_l = 5000      # in um
nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

fasc1_d = 200       # in um
fasc1_y = -100      # in um
fasc1_z = 0         # in um

fasc2_d = 100       # in um
fasc2_y = 100       # in um
fasc2_z = 0         # in um

#create the fascicle objects
fascicle_1 = nrv.fascicle(diameter=fasc1_d,ID=1)      
fascicle_2 = nrv.fascicle(diameter=fasc2_d, ID=2)

#Add the fascicles to the nerve
nerve.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)
nerve.add_fascicle(fascicle=fascicle_2, y=fasc2_y, z=fasc2_z)

#plot
fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve.plot(ax)
ax.set_xlabel("z-axis (µm)")
ax.set_ylabel("y-axis (µm)")

n_ax = 100      #size of the axon population
axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)

fascicle_1.fill_with_population(axons_diameters, axons_type, delta=5)

axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
fascicle_2.fill_with_population(axons_diameters, axons_type, delta=5)

fascicle_1.fit_population_to_size(delta = 2)

#Plot the nerve again.
fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve.plot(ax)
ax.set_xlabel("z-axis (µm)")
ax.set_ylabel("y-axis (µm)")

m_model = 'MRG'
um_model = 'Rattay_Aberham'
u_param = {"model": um_model}
m_param = {"model": m_model}

#For fascicle1
fascicle_1.set_axons_parameters(unmyelinated_only=True,**u_param)
fascicle_1.set_axons_parameters(myelinated_only=True,**m_param)

#For fascicle2
fascicle_2.set_axons_parameters(unmyelinated_only=True,**u_param)
fascicle_2.set_axons_parameters(myelinated_only=True,**m_param)

extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck",      #endoneurium conductivity
                                 peri_mat="perineurium",            #perineurium conductivity
                                 epi_mat="epineurium",              #epineurium conductivity
                                 ext_mat="saline")                  #saline solution conductivity

life_d = 25                                 #LIFE diamter in um
life_length = 1000                          #LIFE active-site length in um
life_x_offset = (nerve_l-life_length)/2     #x position of the LIFE (centered)

life_y_c_0 = 0                              #LIFE_0 y-coordinate (in um)
life_z_c_0 = 150                            #LIFE_0 z-coordinate (in um)
life_y_c_1 = fasc1_y                        #LIFE_1 y-coordinate (in um)
life_z_c_1 = fasc1_z                        #LIFE_1 z-coordinate (in um)
life_y_c_2 = fasc2_y                        #LIFE_2 y-coordinate (in um)
life_z_c_2 = fasc2_z                        #LIFE_1 z-coordinate (in um)

elec_0 = nrv.LIFE_electrode("LIFE_0", life_d, life_length, life_x_offset, life_y_c_0, life_z_c_0, ID = 0) # LIFE in neither of the two fascicles
elec_1 = nrv.LIFE_electrode("LIFE_1", life_d, life_length, life_x_offset, life_y_c_1, life_z_c_1, ID = 1) # LIFE in the fascicle 1
elec_2 = nrv.LIFE_electrode("LIFE_2", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2, ID = 2) # LIFE in the fascicle 2

#Dummy stimulus
dummy_stim = nrv.stimulus()
dummy_stim.pulse(0, 0.1, 1)

#Attach electrodes to the extra_stim object 
extra_stim.add_electrode(elec_0, dummy_stim)
extra_stim.add_electrode(elec_1, dummy_stim)
extra_stim.add_electrode(elec_2, dummy_stim)

nerve.attach_extracellular_stimulation(extra_stim)
nerve.compute_electrodes_footprints()
exit()
nerve.save_results = False
nerve.return_parameters_only = False
nerve.verbose = True
nerve_results = nerve(t_sim=1,postproc_script = "AP_detection")         #Run the simulation


fig, ax = plt.subplots(1, 1, figsize=(6,6))
nerve_results.plot_recruited_fibers(ax)
ax.set_xlabel("z-axis (µm)")
ax.set_ylabel("y-axis (µm)")


t_start = 0.1       #start of the pulse, in ms
t_pulse = 0.1       #duration of the pulse, in ms
amp_pulse = 60      #amplitude of the pulse, in uA 

pulse_stim = nrv.stimulus()
pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      #cathodic pulse

if nrv.MCH.do_master_only_work():
    fig, ax = plt.subplots()                            #plot it
    pulse_stim.plot(ax) #
    ax.set_ylabel("Amplitude (µA)")
    ax.set_xlabel("Time (ms)")



nerve.change_stimulus_from_electrode(ID_elec=2,stimulus=pulse_stim)
nerve_results = nerve(t_sim=3,postproc_script = "AP_detection")

if nrv.MCH.do_master_only_work():
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")

fasc_results = nerve_results.get_fascicle_results(ID = 1)              #get results in fascicle 1
unmyel = fasc_results.get_recruited_axons('unmyelinated')              #get ratio of unmyelinated axon activated in fascicle 1
myel = fasc_results.get_recruited_axons('myelinated')                  #get ratio of myelinated axon activated in fascicle 1

print(f"Proportion of unmyelinated recruited in fascicle_1: {unmyel*100}%")
print(f"Proportion of myelinated recruited in fascicle_1: {myel*100}%")

fasc_results = nerve_results.get_fascicle_results(ID = 2)              #get results in fascicle 2
unmyel = fasc_results.get_recruited_axons('unmyelinated')              #get ratio of unmyelinated axon activated in fascicle 2
myel = fasc_results.get_recruited_axons('myelinated')                  #get ratio of myelinated axon activated in fascicle 2

print(f"Proportion of unmyelinated recruited in fascicle_2: {unmyel*100}%")
print(f"Proportion of myelinated recruited in fascicle_2: {myel*100}%")

fig, ax = plt.subplots(figsize=(8, 8))
nerve_results.plot_recruited_fibers(ax)
ax.set_xlabel("z-axis (µm)")
ax.set_ylabel("y-axis (µm)")

def get_recruitment_electrode(elec_ID:int, amp_vec:np.array) -> list:

    nerve.verbose = False

    #create empty list to store results
    unmyel_fasc1,myel_fasc1,unmyel_fasc2,myel_fasc2 = ([] for i in range(4))

    #Deactivate unused electrodes
    elec_IDs = [0,1,2]
    unused_elec = [x for x in elec_IDs if elec_ID != x]
    for elec in unused_elec:
        nerve.change_stimulus_from_electrode(ID_elec=elec,stimulus=dummy_stim)   

    #Loop throught amp_vec
    print(f"Stimulating nerve with LIFE_{elec_ID}")
    for idx,amp in enumerate(amp_vec):
        amp = np.round(amp,1)                                                       #get the amplitude
        print(f"Pulse amplitude set to {-amp}µA ({idx+1}/{len(amp_vec)})")
        pulse_stim = nrv.stimulus()                                                 #create a new empty stimulus
        pulse_stim.pulse(t_start, -amp, t_pulse)                                    #create a pulse with the new amplitude
        nerve.change_stimulus_from_electrode(ID_elec=elec_ID,stimulus=pulse_stim)    #attach stimulus to selected electrode
        nerve_results = nerve(t_sim=3,postproc_script = "AP_detection")             #run the simulation

        #add results to lists
        fasc_results = nerve_results.get_fascicle_results(ID = 1)
        unmyel_fasc1.append(fasc_results.get_recruited_axons('unmyelinated'))
        myel_fasc1.append(fasc_results.get_recruited_axons('myelinated'))
        fasc_results = nerve_results.get_fascicle_results(ID = 2)
        unmyel_fasc2.append(fasc_results.get_recruited_axons('unmyelinated'))
        myel_fasc2.append(fasc_results.get_recruited_axons('myelinated'))
    return(unmyel_fasc1,myel_fasc1,unmyel_fasc2,myel_fasc2)


amp_min = 0             #start at 0µA 
amp_max = 110           #ends at 150µA 
n_amp = 20              #20pts 
amp_vec = np.linspace(amp_min,amp_max,n_amp)

unmyel_fasc1_LIFE0,myel_fasc1_LIFE0,unmyel_fasc2_LIFE0, myel_fasc2_LIFE0 = get_recruitment_electrode(0,amp_vec)
unmyel_fasc1_LIFE1,myel_fasc1_LIFE1,unmyel_fasc2_LIFE1, myel_fasc2_LIFE1 = get_recruitment_electrode(1,amp_vec)
unmyel_fasc1_LIFE2,myel_fasc1_LIFE2,unmyel_fasc2_LIFE2, myel_fasc2_LIFE2 = get_recruitment_electrode(2,amp_vec)


c_LIFE_0 = "darkcyan"
c_LIFE_1 = "orangered"
c_LIFE_2 = "seagreen"

if nrv.MCH.do_master_only_work():
    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.plot(amp_vec,myel_fasc1_LIFE0, '-o', lw=2, color= c_LIFE_0, label = 'LIFE_0')
    ax1.plot(amp_vec,myel_fasc1_LIFE1, '-o', lw=2, color= c_LIFE_1, label = 'LIFE_1')
    ax1.plot(amp_vec,myel_fasc1_LIFE2, '-o', lw=2, color= c_LIFE_2, label = 'LIFE_2')
    ax1.set_title("Fascicle 1 - Myelinated")

    ax2.plot(amp_vec,myel_fasc2_LIFE0, '-o', lw=2, color= c_LIFE_0, label = 'LIFE_0')
    ax2.plot(amp_vec,myel_fasc2_LIFE1, '-o', lw=2, color= c_LIFE_1, label = 'LIFE_1')
    ax2.plot(amp_vec,myel_fasc2_LIFE2, '-o', lw=2, color= c_LIFE_2, label = 'LIFE_2')
    ax2.set_title("Fascicle 2 - Myelinated")

    for ax in ax1, ax2:
        ax.set_xlabel('Amplitude (µA)')
        ax.set_ylabel('Recruitment')
        ax.legend()
        
    fig.tight_layout()

    plt.show()