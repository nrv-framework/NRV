import nrv
import numpy as np


def context_modifier(X_, static_context):
    local_context = nrv.load_any(static_context, extracel_context = True)
    start = 1
    I_cathod = X_
    I_anod = I_cathod/5
    T_cathod = 60e-3
    T_inter = 40e-3
    stim1 = nrv.stimulus()
    stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    local_context.extra_stim.stimuli[0] = stim1
    return local_context

def residual(results):
    '''# getting the cathodic current
    #print(results['extra_stim'])
    Icath = np.min(results['extra_stim']['stimuli'][0]['s'])
    # count spikes
    nrv.rasterize(results,'V_mem')
    spike_count = np.sum(results['V_mem_rasterized'])/results['Nseg']'''
    return 1


simulation_context = './unitary_tests/sources/200_simple_axon_sim.json'

cf = nrv.CostFunction(simulation_context, context_modifier, residual, t_sim=5)
print(cf(100))