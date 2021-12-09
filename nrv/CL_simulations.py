"""
NRV-Cellular Level simulations
Authors: Florian Kolbl / Roland Giraud / Louis Regnacq
(c) ETIS - University Cergy-Pontoise - CNRS
"""
from .axons import *
from .unmyelinated import *
from .myelinated import *
from .extracellular import *
from .electrodes import *
from .materials import *
from .stimulus import *
from .CL_postprocessing import *
from .MCore import *
from .log_interface import rise_error, rise_warning, pass_info
import numpy as np
import time
import sys

unmyelinated_models=['HH','Rattay_Aberham','Sundt','Tigerholm','Schild_94','Schild_97']
myelinated_models=['MRG','gaines_motor','gaines_sensory']
thin_myelinated_models=['extended_Gaines','RGK']

def firing_threshold(diameter,L,material,dist_elec,cath_first=True,cath_time = 60e-3,t_inter = 40e-3,cath_an_ratio = 5,position_elec=0.5,model='MRG',amp_max=2000,amp_min=0,amp_tol=15,verbose=True,f_dlambda =100,dt=0.005,Nseg_per_sec=None): #f_dlambda=100
    amplitude_max_th=amp_max
    amplitude_min_th=amp_min
    amplitude_tol=amp_tol
    # axon
    y = 0
    z = 0
    # extra cellular
    extra_material = load_material(material)
    #Dichotomy initialization
    previous_amp=amp_min
    delta_amp=np.abs(amp_max-amp_min)
    current_amp=amp_max
    Niter = 1
    while (delta_amp>amplitude_tol):
        if verbose:
            pass_info('Iteration number '+str(Niter)+', testing firing current amplitude '+str(current_amp)+' uA')
        # create axon
        if model in unmyelinated_models:
            if Nseg_per_sec:
                axon1 = unmyelinated(y,z,diameter,L,dt=dt,model=model,Nseg_per_sec=Nseg_per_sec) #freq=f_dlambda
            else:
                axon1 = unmyelinated(y,z,diameter,L,dt=dt,freq=f_dlambda,model=model)
        elif model in myelinated_models:
            if Nseg_per_sec:
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,model=model,Nseg_per_sec=Nseg_per_sec) #freq=f_dlambda
            else:
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        elif model in thin_myelinated_models:
            axon1 = thin_myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        else:
            if Nseg_per_sec:
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,model=model,Nseg_per_sec=Nseg_per_sec) #freq=f_dlambda
            else: 
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        # extra-cellular stimulation
        x_elec = L*position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec,y_elec,z_elec)

        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        I_anod = I_cathod/cath_an_ratio
        T_cathod = cath_time
        T_inter = t_inter
        stim_1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1,stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=5)
        del axon1
        # post-process results
        rasterize(results,'V_mem')
        delta_amp=np.abs(current_amp-previous_amp)
        previous_amp=current_amp
        # test simulation results, update dichotomy
        if (len(results['V_mem_raster_position'])>0):
            if (current_amp==amp_min):
                rise_warning("Minimum Stimulation Current is too High!")
                break
            if (verbose):
                pass_info("... Spike triggered")
            amplitude_max_th=previous_amp
            current_amp=(delta_amp/2)+amplitude_min_th
        else:
            if (current_amp==amp_max):
                rise_warning("Maximum Stimulation Current is too Low!")
                break
            if (verbose):
                pass_info("... Spike not triggered")
            current_amp=amplitude_max_th-delta_amp/2
            amplitude_min_th=previous_amp

        if (previous_amp==amp_max):
            current_amp=amp_min

        Niter += 1
    return current_amp

def para_firing_threshold(diameter,L,material,dist_elec,cath_first=True,cath_time = 60e-3,t_inter = 40e-3,cath_an_ratio = 5,position_elec=0.5,model='MRG',amp_max=2000,amp_min=0,amp_tol=1,verbose=False,f_dlambda = 100,dt=0.005):
    if MCH.is_alone() or MCH.size < 3:
        if MCH.do_master_only_work():
            rise_error('Error: parallel evaluation of a threshold by binary search needs at least 3 parallel processes, but only', MCH.size, 'launched')
        sys.exit(1)
    amplitude_max_th=amp_max
    amplitude_min_th=amp_min
    amplitude_tol=amp_tol
    # axon
    y = 0
    z = 0
    # extra cellular
    extra_material = load_material(material)
    #Dichotomy initialization
    Niter = 1
    values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size)
    delta_amp = values[-1] - values[0]
    current_amp = (values[-1] - values[0])/2
    all_values = values
    while (delta_amp>amplitude_tol or Niter == 1):
        # update toledance
        delta_amp = values[1] - values[0]
        # split job
        current_amp = values[MCH.rank]
        # create axon
        if model in unmyelinated_models:
            axon1 = unmyelinated(y,z,diameter,L,dt=dt,freq=f_dlambda,model=model)
        elif model in myelinated_models:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        elif model in thin_myelinated_models:
            axon1 = thin_myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        else:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        # extra-cellular stimulation
        x_elec = L*position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec,y_elec,z_elec)

        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        I_anod = I_cathod/cath_an_ratio
        T_cathod = cath_time
        T_inter = t_inter
        stim_1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1,stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=5)
        del axon1
        # post-process results
        rasterize(results,'V_mem')
        # test simulation results, gather results to master
        if (len(results['V_mem_raster_position'])>0):
            spike = np.asarray([True])
        else:
            spike = np.asarray([False])
        all_spikes = MCH.gather_jobs_as_array(spike)
        if MCH.do_master_only_work():
            # add the extrema (False at start, True at the end) already computed at the previous step if Niter > 1
            if Niter > 1:
                all_spikes = np.insert(np.append(all_spikes, True), 0, False)
            # find the zone where the spike appears, update min max
            appear_index = np.argmax(all_spikes==True)
            amplitude_max_th = all_values[appear_index]
            amplitude_min_th = all_values[appear_index-1]
            # update current amp
            current_amp = amplitude_min_th + (amplitude_max_th-amplitude_min_th)/2
            # compute new values
            all_values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size+3)
            values = all_values[1:-1]
        # share new values
        values = MCH.master_broadcasts_array_to_all(values)
        Niter += 1
    # adapt Niter for correct return
    Niter -= 1
    # share master current amp to all process
    current_amp = MCH.master_broadcasts_array_to_all(current_amp)
    return current_amp, Niter

def blocking_threshold(diameter,L,material,dist_elec,block_freq,position_elec=0.5,model='MRG',
    amp_max=2000,amp_min=0,amp_tol=15,Nseg_per_sec=None,verbose=True,f_dlambda = 100,dt=0.005, t_start_test=20):

    amplitude_max_th=amp_max
    amplitude_min_th=amp_min
    amplitude_tol=amp_tol
    # axon
    y = 0
    z = 0
    # test spike
    t_start = t_start_test
    duration = 0.1
    amplitude = 5
    # extra cellular
    extra_material = load_material(material)
    block_start=3 #ms
    block_duration=20 #ms
    if t_start > block_duration:
        block_duration = t_start
    #Dichotomy initialization
    previous_amp=amp_min
    delta_amp=np.abs(amp_max-amp_min)
    current_amp=amp_max
    Niter = 1
    while (delta_amp>amplitude_tol):
        if verbose:
            pass_info('Iteration number '+str(Niter)+', testing block current amplitude '+str(current_amp)+' uA')
        # create axon
        if model in unmyelinated_models:
            if Nseg_per_sec:
                axon1 = unmyelinated(y,z,diameter,L,dt=dt,Nseg_per_sec=Nseg_per_sec,model=model)
            else:
                axon1 = unmyelinated(y,z,diameter,L,dt=dt,freq=f_dlambda,model=model)
        elif model in myelinated_models:
            if Nseg_per_sec:
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,Nseg_per_sec=Nseg_per_sec,model=model)
            else:
                axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        elif model in thin_myelinated_models:
            axon1 = thin_myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        else:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        # insert test spike
        axon1.insert_I_Clamp(0, t_start, duration, amplitude)
        # extra-cellular stimulation
        if position_elec >= 1 and (model not in unmyelinated_models):
            x_elec = axon1.x_nodes[position_elec]
        else:
            x_elec = L*position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec,y_elec,z_elec)
        stim_1 = stimulus()
        stim_1.sinus(block_start, block_duration, current_amp, block_freq ,dt=1/(block_freq*20))
        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1,stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        t_sim = block_duration + block_start + 2
        results = axon1.simulate(t_sim=t_sim)
        del axon1
        pass_info('... Iteration simulation performed in '+str(results['sim_time'])+' s')
        # post-process results
        rasterize(results,'V_mem')
        delta_amp=np.abs(current_amp-previous_amp)
        previous_amp=current_amp
        # test simulation results, update dichotomy
        if block(results, t_start=t_start) == False:
            if (current_amp == amp_max):
                rise_warning("Maximum Stimulation Current is too Low!",verbose=verbose)
                return -1
            pass_info("... Spike not blocked",verbose=verbose)
            amplitude_min_th = current_amp
            current_amp = (delta_amp/2)+amplitude_min_th
        else:
            if (current_amp == amp_min):
                rise_warning("Minimum Stimulation Current is too High!",verbose=verbose)
                break
            pass_info("... Spike blocked",verbose=verbose)
            amplitude_max_th = current_amp
            current_amp = amplitude_max_th-delta_amp/2

        if (previous_amp == amp_max):
                current_amp = amp_min
        Niter += 1
    return current_amp

def para_blocking_threshold(diameter,L,material,dist_elec,block_freq,position_elec=0.5,model='MRG',amp_max=2000,amp_min=0,amp_tol=15,verbose=True,f_dlambda = 100,dt=0.005):
    amplitude_max_th=amp_max
    amplitude_min_th=amp_min
    amplitude_tol=amp_tol
    # axon
    y = 0
    z = 0
    # test spike
    t_start = 20
    duration = 0.1
    amplitude = 3
    # extra cellular
    extra_material = load_material(material)
    block_start=3 #ms
    block_duration=20 #ms
    #Dichotomy initialization
    Niter = 1
    values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size)
    delta_amp = values[-1] - values[0]
    current_amp = (values[-1] - values[0])/2
    all_values = values
    while (delta_amp>amplitude_tol or Niter == 1):
        # update toledance
        delta_amp = values[1] - values[0]
        # split job
        current_amp = values[MCH.rank]
        # create axon
        if model in unmyelinated_models:
            axon1 = unmyelinated(y,z,diameter,L,dt=dt,freq=f_dlambda,model=model)
        elif model in myelinated_models:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        elif model in thin_myelinated_models:
            axon1 = thin_myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        else:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        # insert test spike
        axon1.insert_I_Clamp(0, t_start, duration, amplitude)
        # extra-cellular stimulation
        x_elec = L*position_elec
        y_elec = dist_elec
        z_elec = 0
        elec_1 = point_source_electrode(x_elec,y_elec,z_elec)
        stim_1 = stimulus()
        stim_1.sinus(block_start, block_duration, current_amp, block_freq ,dt=1/(block_freq*20))
        stim_extra = stimulation(extra_material)
        stim_extra.add_electrode(elec_1,stim_1)
        axon1.attach_extracellular_stimulation(stim_extra)
        # simulate axon activity
        results = axon1.simulate(t_sim=25)
        del axon1
        # post-process results
        rasterize(results,'V_mem')

        # test simulation results, gather results to master
        blocked = [block(results)]
        all_blocks = MCH.gather_jobs_as_array(blocked)
        if MCH.do_master_only_work():
            # add the extrema (False at start, True at the end) already computed at the previous step if Niter > 1
            if Niter > 1:
                all_blocks = np.insert(np.append(all_blocks, True), 0, False)
            # find the zone where the blocking appears, update min max
            appear_index = np.argmax(all_blocks==True)
            amplitude_max_th = all_values[appear_index]
            amplitude_min_th = all_values[appear_index-1]
            # update current amp
            current_amp = amplitude_min_th + (amplitude_max_th-amplitude_min_th)/2
            # compute new values
            all_values = np.linspace(amplitude_min_th, amplitude_max_th, num=MCH.size+3)
            values = all_values[1:-1]
        # share new values
        values = MCH.master_broadcasts_array_to_all(values)
        Niter += 1
    # adapt Niter for correct return
    Niter -= 1
    # share master current amp to all process
    current_amp = MCH.master_broadcasts_array_to_all(current_amp)
    return current_amp, Niter

def LIFE_firing_threshold(extra_model, diameter,L,dist_elec,cath_first=True,cath_time=60e-3,t_inter=40e-3,cath_an_ratio=5,model='MRG',amp_max=500,amp_min=0,amp_tol=1,verbose=False,f_dlambda = 100,dt=0.001,t_sim=5):
    amplitude_max_th=amp_max
    amplitude_min_th=amp_min
    amplitude_tol=amp_tol
    #Dichotomy initialization
    previous_amp=amp_min
    delta_amp=np.abs(amp_max-amp_min)
    current_amp=amp_max
    # axon
    y = 0
    z = dist_elec

    # Binayr search
    Niter = 1
    while (delta_amp>amplitude_tol):
        pass_info('Iteration number '+str(Niter)+', testing firing current amplitude '+str(current_amp)+' uA')
        # create axon
        if model in unmyelinated_models:
            axon1 = unmyelinated(y,z,diameter,L,dt=dt,freq=f_dlambda,model=model)
        elif model in myelinated_models:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        else:
            axon1 = myelinated(y,z,diameter,L,rec='nodes',dt=dt,freq=f_dlambda,model=model)
        # stimulus def
        stim_1 = stimulus()
        start = 1
        I_cathod = current_amp
        I_anod = I_cathod/cath_an_ratio
        T_cathod = cath_time
        T_inter = t_inter
        stim_1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
        extra_model.reset_stimuli()
        extra_model.stimuli.append(stim_1)
        extra_model.synchronise_stimuli()
        axon1.attach_extracellular_stimulation(extra_model)
        # simulate axon activity
        results = axon1.simulate(t_sim=t_sim)
        del axon1
        del stim_1
        pass_info('... Iteration simulation performed in '+str(results['sim_time'])+' s')
        # post-process results
        rasterize(results,'V_mem')
        delta_amp=np.abs(current_amp-previous_amp)
        previous_amp=current_amp
        # test simulation results, update dichotomy
        if (len(results['V_mem_raster_position'])>0):
            if (current_amp==amp_min):
                rise_warning("Minimum Stimulation Current is too High!")
                break
            if (verbose):
                pass_info("... Spike triggered")
            amplitude_max_th=previous_amp
            current_amp=(delta_amp/2)+amplitude_min_th
        else:
            if (current_amp==amp_max):
                rise_warning("Maximum Stimulation Current is too Low!")
                break
            if (verbose):
                pass_info("... Spike not triggered")
            current_amp=amplitude_max_th-delta_amp/2
            amplitude_min_th=previous_amp

        if (previous_amp==amp_max):
            current_amp=amp_min

        Niter += 1
    return current_amp
