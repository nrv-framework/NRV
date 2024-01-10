import nrv
import matplotlib.pyplot as plt
import time
import numpy as np

def bound_generator(amp_b,relative_amp_b,phase_b,n_tones):
    bounds = [amp_b]
    for k in range(n_tones):
        bounds.append(relative_amp_b)
        bounds.append(phase_b)

    return(bounds)

amp_bounds = (10,100)
relative_amp_bounds = (0,1)
phase_bounds = (np.pi,0)

start = 1
t_pulse = 100e-3
test_stim_CM = nrv.harmonic_stimulus_CM(start = start,t_pulse=t_pulse)
t_sim=5
static_context = "./unitary_tests/sources/202_axon.json"


plt.figure()
n_tones = 1
for i in range(10):
    bounds = bound_generator(amp_bounds,relative_amp_bounds,phase_bounds,n_tones)
    print(bounds)
    X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
    ax = test_stim_CM(X, static_context)
    test_stim = ax.extra_stim.stimuli[0]
    plt.step(test_stim.t, test_stim.s,where='post')
    print(X)
   # waveform2 = nrv.interpolate_Npts(X, plot=True, generatefigure=False, **kwrgs_interp)
plt.savefig('./unitary_tests/figures/509_A.png')

plt.figure()
n_tones = 2
for i in range(10):
    bounds = bound_generator(amp_bounds,relative_amp_bounds,phase_bounds,n_tones)
    print(bounds)
    X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
    ax = test_stim_CM(X, static_context)
    test_stim = ax.extra_stim.stimuli[0]
    plt.step(test_stim.t, test_stim.s,where='post')
    print(X)
   # waveform2 = nrv.interpolate_Npts(X, plot=True, generatefigure=False, **kwrgs_interp)
plt.savefig('./unitary_tests/figures/509_B.png')

plt.figure()
n_tones = 3
for i in range(10):
    bounds = bound_generator(amp_bounds,relative_amp_bounds,phase_bounds,n_tones)
    print(bounds)
    X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
    ax = test_stim_CM(X, static_context)
    test_stim = ax.extra_stim.stimuli[0]
    plt.step(test_stim.t, test_stim.s,where='post')
    print(X)
   # waveform2 = nrv.interpolate_Npts(X, plot=True, generatefigure=False, **kwrgs_interp)
plt.savefig('./unitary_tests/figures/509_C.png')

plt.figure()
n_tones = 7
for i in range(10):
    bounds = bound_generator(amp_bounds,relative_amp_bounds,phase_bounds,n_tones)
    print(bounds)
    X = np.array([np.random.uniform(low=bounds[k][0], high=bounds[k][1]) for k in range(len(bounds))])
    ax = test_stim_CM(X, static_context)
    test_stim = ax.extra_stim.stimuli[0]
    plt.step(test_stim.t, test_stim.s,where='post')
    print(X)
   # waveform2 = nrv.interpolate_Npts(X, plot=True, generatefigure=False, **kwrgs_interp)
plt.savefig('./unitary_tests/figures/509_D.png')
#plt.show()
