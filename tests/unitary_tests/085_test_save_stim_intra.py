import nrv
import matplotlib.pyplot as plt
import numpy as np

unm_axon_file = "./unitary_tests/figures/085_unm_axon.json"

m_axon_file = "./unitary_tests/figures/085_m_axon.json"


y = 0
z = 0
d = 1
L = 5000

t_start = 1
duration = 0.5
amplitude = 5



# test 3: 10 sections multiple stims
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100,Nsec=10)
axon1.insert_I_Clamp(0.25, t_start, duration, amplitude)
axon1.insert_I_Clamp(0.75, t_start, duration, amplitude)
axon1.insert_I_Clamp(0.5, t_start+7, duration, amplitude)

axon1.save(save=True, fname=unm_axon_file, intracel_context=True)
print("Axon saved")
axon2 = nrv.load_any_axon(unm_axon_file, intracel_context=True)
print("Axon loaded")


results = axon1.simulate(t_sim=12)
del axon1
plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/85_A.png')


axon2.insert_I_Clamp(0, t_start, duration, amplitude)

results = axon2.simulate(t_sim=12)

del axon2


plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage (mV)')
plt.savefig('./unitary_tests/figures/85_B.png')


y = 0
z = 0
d = 10
L = nrv.get_length_from_nodes(d, 20)


axon3 = nrv.myelinated(y,z,d,L,dt=0.005,Nseg_per_sec=1,rec='nodes')

# Voltage clamp
clamp_node = 10
v_stim = nrv.datfile_2_stim('./unitary_tests/sources/065_V_env.dat', dt=0.005)
axon3.insert_V_Clamp_node(10, v_stim)


plt.figure()
plt.step(v_stim.t, v_stim.s, where='post')
plt.savefig('./unitary_tests/figures/85_C.png')



## IClamp for spike initiation
'''
t_start = 90
duration = 0.1
amplitude = 2
axon3.insert_I_Clamp_node(1, t_start, duration, amplitude)
'''

axon3.save(save=True,fname=m_axon_file, intracel_context=True)
print("Axon saved")
axon4 = nrv.load_any_axon(m_axon_file, intracel_context=True)
print("Axon loaded")
results = axon3.simulate(t_sim=100)

plt.figure()
for k in range(len(results['x_rec'])):
    plt.plot(results['t'],results['V_mem'][k]+k*100, color='k')
plt.yticks([])
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/85_D.png')



results = axon4.simulate(t_sim=100)

plt.figure()
for k in range(len(results['x_rec'])):
    plt.plot(results['t'],results['V_mem'][k]+k*100, color='k')
plt.yticks([])
plt.xlabel('time ($ms$)')
plt.savefig('./unitary_tests/figures/85_E.png')


#plt.show()

