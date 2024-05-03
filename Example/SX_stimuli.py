import nrv
import matplotlib.pyplot as plt
from numpy import exp

#####################################
# Example of combination of stimuli #
#####################################
stim1, stim2 = nrv.stimulus(), nrv.stimulus()

# stim1 parameters
t_start = 1
duration = 10
amp1 = 1
f_stim1 = 1
stim1.square(t_start, duration, amp1, f_stim1, 0, 0.5)
# stim2 parameters
f_stim2 = 5
amp2 = 0.5
stim2.sinus(0, t_start+duration, amp2, f_stim2)

# computations with +,-,*
stim3 = stim1 + stim2
stim4 = stim2 - stim1
stim5 = (stim1 + 1) * stim2

#print(dir(biphasic_stim))
fig, axs = plt.subplots(1, 2, layout='constrained', figsize=(10, 4))
stim1.plot(axs[0], label='stim1')
stim2.plot(axs[0], label='stim2')
axs[0].legend()
axs[0].set_title('stim1 and stim2')
stim3.plot(axs[1], label='stim1+stim2')
stim4.plot(axs[1], label='stim2-stim1')
stim5.plot(axs[1], label='(stim1+1)*stim2')
axs[1].set_title('mathematical combinations')
axs[1].legend()

###################################
# Example of amplitude modulation #
###################################
stim1, stim2 = nrv.stimulus(), nrv.stimulus()

f_stim = 1
t_start = 1
duration = 99
amp = 0.5

t_ramp_stop = 90
amp_start = 0
amp_max = 1

stim1.sinus(t_start, duration, amp, f_stim)
stim2.ramp_lim(t_start, t_ramp_stop, amp_start, amp_max, duration, dt=1)

stim3 = stim1*stim2
fig, axs = plt.subplots(1, 2, layout='constrained', figsize=(10, 4))

stim1.plot(axs[0])
stim2.plot(axs[0])
axs[0].set_title('signal and and envelope')
stim3.plot(axs[1])
axs[1].set_title('amplitude modulated signal')

#################################################
## Example of a complex custom stimulus design ##
##                                             ##
## simple pulse with a prepulse and charge     ##
## balance                                     ##
## modulation with a gaussian of borst of 10   ##
## patterns                                    ##
## repetition of the bursts                    ##
#################################################

start = 0
fig, axs = plt.subplots(2, 2, layout='constrained', figsize=(10, 8))

# waveform parameters
complex_stim = nrv.stimulus()
prepulse_amp = -10              # in uA
t_prepulse = 120e-3             # in ms
cath_amp = -100                 # in uA
t_cath = 60e-3                  # in ms
deadtime = 60e-3                # in ms
an_amp = 20                     # in uA
# prepulse and cathodic pulse
complex_stim.pulse(start, prepulse_amp)
complex_stim.pulse(start + t_prepulse, cath_amp, t_cath)
complex_stim.s[-1] = 0
# compute the balancing time and anodic pulse
an_duration = abs(prepulse_amp*t_prepulse + cath_amp*t_cath)/an_amp
complex_stim.pulse(complex_stim.t[-1] + deadtime, an_amp, an_duration)
# plot the pattern
complex_stim.plot(axs[0, 0])
axs[0, 0].set_title('pattern with prepulse')
axs[0, 0].set_xlabel('time (ms)')
axs[0, 0].set_ylabel('amplitude (uA)')

# create burst of 10 patterns
freq = 1.                       # in kHz
# finish the period
t_blank = 1/freq - (t_prepulse + t_cath + deadtime + an_duration)
N_patterns = 10
s_pattern, t_pattern = complex_stim.s, complex_stim.t
for i in range(N_patterns-1):
    complex_stim.concatenate(s_pattern, t_pattern, t_shift=t_blank)
# plot the pattern
complex_stim.plot(axs[0, 1])
axs[0, 1].set_title('burst of 10 patterns')
axs[0, 1].set_xlabel('time (ms)')
axs[0, 1].set_ylabel('amplitude (uA)')

# multiply by gaussian
def my_gaussian(t, f, N_patterns):
    return exp(-((t - ((N_patterns/2)-1)*(1/f))**2)/4)
envelope = nrv.stimulus()
for k in range(N_patterns):
    envelope.pulse(k*(1/freq), my_gaussian(k*(1/freq), freq, N_patterns))
#envelope.pulse(envelope.t[-1], 0, (1/freq)
#envelope.plot(axs[1, 0], color='r', label='enveloppe')
modulated_pattern = complex_stim * envelope
modulated_pattern.plot(axs[1,0])
#complex_stim.plot(axs[1, 0], color='b', label='stimulus')
axs[1, 0].set_title('Burst modulation')
#axs[1, 0].legend()
axs[1, 0].set_xlabel('time (ms)')
axs[1, 0].set_ylabel('amplitude (uA)')

plt.show()