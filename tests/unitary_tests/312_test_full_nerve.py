import nrv
import matplotlib.pyplot as plt

def create_nerve():
    ## parameters
    # nerve parameters
    outer_d = 5         # in mm
    nerve_d = 500       # in um
    nerve_l = 5000      # in um
    # first fascicle
    fasc1_d = 200       # in um
    fasc1_y = -100      # in um
    fasc1_z = 0         # in um
    # second fascicle
    fasc2_d = 100       # in um
    fasc2_y = 100       # in um
    fasc2_z = 0         # in um
    # stimulus
    t_start = 0.1       #start of the pulse, in ms
    t_pulse = 0.1       #duration of the pulse, in ms
    amp_pulse = 60      #amplitude of the pulse, in uA 

    # create objects
    nerve = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)
    fascicle_1 = nrv.fascicle(diameter=fasc1_d, ID=1)
    fascicle_2 = nrv.fascicle(diameter=fasc2_d, ID=2)
    nerve.add_fascicle(fascicle=fascicle_1, y=fasc1_y, z=fasc1_z)
    nerve.add_fascicle(fascicle=fascicle_2, y=fasc2_y, z=fasc2_z)

    # create axon population
    n_ax = 100      #size of the axon population
    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
    fascicle_1.fill_with_population(axons_diameters, axons_type, delta=5)

    axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(n_ax, percent_unmyel=0.7, M_stat="Ochoa_M", U_stat="Ochoa_U",)
    fascicle_2.fill_with_population(axons_diameters, axons_type, delta=5)
    fascicle_1.fit_population_to_size(delta=2)

    ## add electrode and stimulation
    # electrode
    extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck",peri_mat="perineurium", epi_mat="epineurium", ext_mat="saline")
    life_d = 25                                 # LIFE diamter in um
    life_length = 1000                          # LIFE active-site length in um
    life_x_offset = (nerve_l-life_length)/2     # x position of the LIFE (centered)
    life_y_c_2 = fasc2_y                        # LIFE_2 y-coordinate (in um)
    life_z_c_2 = fasc2_z                        # LIFE_1 z-coordinate (in um)
    elec_2 = nrv.LIFE_electrode("LIFE_2", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2) # LIFE in the fascicle 2
    # stimulus
    pulse_stim = nrv.stimulus()
    pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      #cathodic
    #Attach electrodes to the extra_stim object 
    extra_stim.add_electrode(elec_2, pulse_stim)
    nerve.attach_extracellular_stimulation(extra_stim)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve.plot(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig("nerve_example.png", dpi=300)
    plt.close(fig)
    return nerve


def simulate_nerve(nerve, nproc=4):
    nrv.parameters.set_nmod_ncore(nproc)
    results = nerve(t_sim=3,postproc_script = "is_recruited")
    return results


def prostprocessing(results):
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig("nerve_postproc.png", dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    #################
    # PREPROCESSING #
    #################

    # This is not compultationally intensive,
    # so we can use only on processes
    sim_nerve = create_nerve()

    ##############
    # SIMULATION #
    ##############

    # This is computationally intensive,
    # so we can use multiple processes
    results = simulate_nerve(sim_nerve, nproc=4)

    ##################
    # POSTPROCESSING #
    ##################

    # This is not compultationally intensive,
    # so we can use only on processes
    prostprocessing(results)