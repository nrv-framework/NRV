
import nrv
from pathlib import Path
if __name__ == "__main__":
    t_sim = 10

    y_a = 0                                                                                     #axon y position, in [µm]
    z_a = 0                                                                                     #axon z position, in [µm]
    d_a = 10                                                                                    #axon diameter position, in [µm]
    n_NoR = 25                                                                                  #number of Node-of-Ranvier
    L_a = nrv.get_length_from_nodes(d_a, n_NoR)                                                 #Get the axon length from number of NoR
    axon_m = nrv.myelinated(y_a, z_a, d_a, L_a, model="MRG", rec="nodes", Nseg_per_sec=3)       #we recording only at the node of Ranvier

    extra_stim = nrv.FEM_stimulation()

    #nerve/fascicle shape
    d_outbox= 5        #in mm
    d_n = 1500         #in um
    d_f = 1000              #in um
    y_f = 0                 #y pos of the fascicle, in um
    z_f = 0                 #y pos of the fascicle, in um
    extra_stim.reshape_outerBox(d_outbox)
    extra_stim.reshape_nerve(d_n,L_a*1.2)
    extra_stim.reshape_fascicle(Fascicle_D = d_f, y_c=y_f, z_c= z_f)

    #LIFE
    LIFE_d = 25                         # LIFE's diameter, in um
    LIFE_l = 1000                       # LIFE's active-site length, in um
    x_LIFE = axon_m.x_nodes[n_NoR//2]   # LIFE x position, in [um]
    y_LIFE = 0                          # LIFE y position, in [um]
    z_LIFE = 100                        # LIFE z position, in [um]
    x_LIFE_offset = x_LIFE - (LIFE_l/2)
    LIFE = nrv.LIFE_electrode('LIFE_1', LIFE_d, LIFE_l, x_LIFE_offset, y_LIFE, z_LIFE)

    stim1 = nrv.stimulus() #dummy stim
    stim1.sinus(1,t_sim,100,10)
    extra_stim.add_electrode(LIFE, stim1)   

    ### Test pulse
    test_start = 7
    duration = 0.1
    amplitude = 2
    axon_m.insert_I_Clamp(0.05, test_start, duration, amplitude)  

    axon_m.attach_extracellular_stimulation(extra_stim)

    #Update function for KES sine block
    def KES_update(axon,amp, freq_KES, t_KES, start_KES = 1, elec_id = 0):
        stim_KES = nrv.stimulus()
        stim_KES.sinus(start_KES,t_KES,amp,freq_KES)
        axon.change_stimulus_from_electrode(elec_id, stim_KES)
        del stim_KES

    #parameters for the waveforms
    arg_stim = {'freq_KES':10, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}
    arg_stim2 = {'freq_KES':20, 'elec_id':0, 'start_KES':1, 't_KES':t_sim}
    max_amp = 100 #maximum search boundary

    save_path='./unitary_tests/figures/test_90A/'
    save_path2='./unitary_tests/figures/test_90B/'

    Path(save_path).mkdir(parents=True, exist_ok=True)
    Path(save_path2).mkdir(parents=True, exist_ok=True)


    threshold_10khz = nrv.axon_block_threshold(axon = axon_m,amp_max = max_amp,update_func = KES_update, args_update=arg_stim,
                                            AP_start = test_start, freq = arg_stim['freq_KES'], t_sim = t_sim, save_path=save_path)

    threshold_20khz = nrv.axon_block_threshold(axon = axon_m,amp_max = max_amp,update_func = KES_update, args_update=arg_stim2,
                                            AP_start = test_start, freq = arg_stim2['freq_KES'], t_sim = t_sim, save_path=save_path2)

    del axon_m