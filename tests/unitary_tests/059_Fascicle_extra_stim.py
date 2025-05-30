import nrv
from sources.OTF_PP_stim_intra import stim_intra

if __name__ == '__main__':
    # Fascicle config
    L = 10000             # length, in um
    source_file = './unitary_tests/sources/56_fasc.json'
    # extra cellular stimulation parameters
    # electrode def
    x_elec = L/2                # electrode x position, in [um]
    y_elec = 12                # electrode y position, in [um]
    z_elec = 0                    # electrode y position, in [um]
    E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
    # load material properties
    epineurium = nrv.load_material('endoneurium_ranck')
    # stimulus def
    start = 1
    I_cathod = 50
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    # extracellular stimulation setup
    extra_stim = nrv.stimulation(epineurium)
    extra_stim.add_electrode(E1, stim1)


    # Fascicle declaration
    fascicle_1 = nrv.fascicle()
    fascicle_1.load_fascicle_configuration(source_file)
    fascicle_1.define_length(L)
    fascicle_1.set_ID(59)
    # extra cellular stimulation
    fascicle_1.attach_extracellular_stimulation(extra_stim)
    # simulation
    fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/',postproc_script=stim_intra)