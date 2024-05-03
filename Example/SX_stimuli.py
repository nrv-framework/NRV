import nrv
import matplotlib.pyplot as plt

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


plt.show()