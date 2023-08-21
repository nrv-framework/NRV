import nrv
import matplotlib.pyplot as plt
import time
import numpy as np


#nrv.parameters.set_nrv_verbosity(4)
L=10000
d=10
ax1 = nrv.myelinated(L=L, d=d)


LIFE_stim = nrv.FEM_stimulation()
# ### Simulation box size
Outer_D = 5
LIFE_stim.reshape_outerBox(Outer_D)
#### Nerve and fascicle geometry
Nerve_D = 250
Fascicle_D = 220
LIFE_stim.reshape_nerve(Nerve_D=Nerve_D, Length=L)
LIFE_stim.reshape_fascicle(Fascicle_D)
##### electrode and stimulus definition
D = 25
length = 1000
y_c = 0
z_c = 50
x_1_offset = (L-length)/2
elec_1 = nrv.LIFE_electrode('LIFE_1', D, length, x_1_offset, y_c, z_c)
# stimulus def
freq = 10
amp = 10
start = 0
duration = 10
stim1 = nrv.stimulus()
stim1.sinus(start=start, duration=duration, amplitude=amp, freq=freq, dt=0.001)
LIFE_stim.add_electrode(elec_1, stim1)

x_2_offset = (length)/2
elec_2 = nrv.LIFE_electrode('LIFE_1', D, length, x_2_offset, y_c, z_c)
start = 0
I_cathod = 40
I_anod = I_cathod/5
T_cathod = 100e-3
T_inter = 50e-3
stim2 = nrv.stimulus()
stim2.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
LIFE_stim.add_electrode(elec_2, stim2)


plt.plot(LIFE_stim.stimuli[0].t[1:],np.diff(LIFE_stim.stimuli[0].t), '.-')
#plt.plot(LIFE_stim.stimuli[1].t[1:],np.diff(LIFE_stim.stimuli[1].t), '.-')
#plt.show()
exit()

ax1.attach_extracellular_stimulation(LIFE_stim)

print(ax1.extra_stim.stimuli[0].t, ax1.extra_stim.stimuli[1].t)
print(min(abs(ax1.extra_stim.stimuli[0] -ax1.extra_stim.stimuli[1].t)))

#nerve.compute_electrodes_footprints()
ax1.simulate(t_sim=50)



#plt.show()