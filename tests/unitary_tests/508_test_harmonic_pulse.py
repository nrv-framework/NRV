import nrv
import matplotlib.pyplot as plt
import time
import numpy as np

single_tone = nrv.stimulus()

start = 1
t_pulse = 1
amp_list = [1]
phase_list = [0]
amp = 1
single_tone.harmonic_pulse(start, t_pulse,amp, amp_list, phase_list)
plt.figure()
plt.step(single_tone.t, single_tone.s,where='post')
plt.savefig('./unitary_tests/figures/508_A.png')

three_tone = nrv.stimulus()
start = 1
t_pulse = 1
amp_list = [1,1.0,1.0,1.0]
phase_list = [0,0.0,0.0,0]
amp = 1
three_tone.harmonic_pulse(start, t_pulse,amp, amp_list, phase_list)
plt.figure()
plt.step(three_tone.t, three_tone.s,where='post')
plt.savefig('./unitary_tests/figures/508_B.png')

square_pulse = nrv.stimulus()
start = 1
t_pulse = 0.5
amp_list = [1,0,1/3,0,1/5,0,1/7,0,1/9,0,1/11]
phase_list = [0,0,0,0,0,0,0,0,0,0,0]
amp = 1
square_pulse.harmonic_pulse(start=start, t_pulse=t_pulse,amplitude=amp, amp_list=amp_list, phase_list=phase_list)
plt.figure()
plt.step(square_pulse.t, square_pulse.s,where='post')
plt.savefig('./unitary_tests/figures/508_C.png')
