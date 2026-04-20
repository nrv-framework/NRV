import nrv
import numpy as np
import matplotlib.pyplot as plt

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


if __name__ == "__main__":
    np.random.seed(444)

    outer_d = 5         # in mm
    nerve_d = 500       # in um
    nerve_l = 5000      # in um
    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)

    ## Nerve creation
    fasc1_vertices = [[-100, -60],
                      [100, -60],
                      [100, 60],
                      [-100, 60],
        ]       # in um
    fasc1_y = -100      # in um
    fasc1_z = 0         # in um

    fasc2_vertices = [[-50, -30],
                      [50, -30],
                      [50, 30],
                      [-50, 30],
        ]       # in um
    fasc2_y = 100       # in um
    fasc2_z = 0         # in um

    #create the fascicle objects
    fascicle_1 = nrv.fascicle(ID=1)
    fascicle_1.set_geometry(geometry=nrv.create_cshape(vertices=fasc1_vertices))
    fascicle_2 = nrv.fascicle(ID=2)
    fascicle_2.set_geometry(geometry=nrv.create_cshape(vertices=fasc2_vertices))
    #Add the fascicles to the nerve
    nerve.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)
    nerve.add_fascicle(fascicle=fascicle_2, y=fasc2_y, z=fasc2_z, rot=90, degree=True)

    n_ax = 100      #size of the axon population
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
    
    fascicle_1.fill(n_ax=n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U", delta=2, delta_trace=10)

    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
    fascicle_2.fill(n_ax=n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U", delta=2)
    # fascicle_1.fit_population_to_size(delta=2)


    extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck",peri_mat="perineurium", epi_mat="epineurium", ext_mat="saline")

    life_d = 25                                 #LIFE diamter in um
    life_length = 1000                          #LIFE active-site length in um
    life_x_offset = (nerve_l-life_length)/2     #x position of the LIFE (centered)
    life_y_c_2 = fasc2_y                        #LIFE_2 y-coordinate (in um)
    life_z_c_2 = fasc2_z                        #LIFE_1 z-coordinate (in um)

    elec_2 = nrv.LIFE_electrode("LIFE_2", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2) # LIFE in the fascicle 2

    # stimulus
    t_start = 0.1       #start of the pulse, in ms
    t_pulse = 0.1       #duration of the pulse, in ms
    amp_pulse = 60      #amplitude of the pulse, in uA 

    pulse_stim = nrv.stimulus()
    pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      #cathodic

    #Attach electrodes to the extra_stim object 
    extra_stim.add_electrode(elec_2, pulse_stim)
    nerve.attach_extracellular_stimulation(extra_stim)


    #Plot the nerve again.
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve.plot(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig(figdir+"A.png")
    nerve_ppt = nerve.save(save=False,extracel_context=True)
    del nerve

    ##################
    ## Simulations ###
    ##################
    # Default nproc (in nrv/_misc/NRV.ini)
    ner1 = nrv.load_nerve(nerve_ppt, extracel_context=True)
    n_res1 = ner1(t_sim=3,postproc_script = "is_recruited")
    del ner1

    fig, ax = plt.subplots(figsize=(10,5))
    n_res1.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig(figdir+"B.png")

    # plt.show()
