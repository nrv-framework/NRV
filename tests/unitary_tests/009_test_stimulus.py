import nrv
import numpy as np 
import matplotlib.pyplot as plt

stim1 = nrv.stimulus()

start = 1
I_cathod = 100
I_anod = I_cathod/5
T_cathod = 60e-3
T_inter = 40e-3

stim1.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

plt.figure()
plt.step(stim1.t, stim1.s,where='post')
plt.savefig('./unitary_tests/figures/09_A.png')

t_bis = np.linspace(0,2)

stim1.insert_samples(t_bis)
stim2 = -stim1
stim3 = abs(stim1)
stim4 = stim1 + 50
stim5 = stim1 + stim3
stim6 = stim1 - stim4
stim7 = stim1 - 50
stim8 = stim1*2
plt.figure()
plt.step(stim1.t, stim1.s,where='post',label='1')
plt.step(stim2.t, stim2.s,where='post',label='2')
plt.step(stim3.t, stim3.s,where='post',label='3')
plt.step(stim4.t, stim4.s,where='post',label='4')
plt.step(stim5.t, stim5.s,where='post',label='5')
plt.step(stim6.t, stim6.s,where='post',label='6')
plt.step(stim7.t, stim7.s,where='post',label='7')
plt.step(stim8.t, stim8.s,where='post',label='8')
plt.legend()
plt.savefig('./unitary_tests/figures/09_B.png')

stima = nrv.stimulus()
stima.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)

print(nrv.is_stim(stim1))
print(stima == stim1)
print(stim2 != stim3)

freq = 4
amp = 10
start = 0.5
duration = 10
stim_HF = nrv.stimulus()
stim_HF.sinus(start, duration, amp, freq)

stim_combined = stim_HF + stima

plt.figure()
plt.step(stim_HF.t, stim_HF.s,where='post',label='1')
plt.step(stim_combined.t, stim_combined.s,where='post',label='combined')
plt.savefig('./unitary_tests/figures/09_C.png')
#plt.show()