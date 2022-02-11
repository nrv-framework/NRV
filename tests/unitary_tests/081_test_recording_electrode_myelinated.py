import nrv
import matplotlib.pyplot as plt
## Axon def
y = 0
z = 0
d = 10.7
L = nrv.get_length_from_nodes(d,40)
model = "MRG" # Rattay_Aberham if not precised

axon1 = nrv.myelinated(y, z, d, L, model=model)

## test pulse
t_start = 1
duration = 0.1
amplitude = 1
axon1.insert_I_Clamp(0.01, t_start, duration, amplitude)

# test recording
testrec = nrv.recorder('endoneurium_bhadra')
testrec.set_recording_point(axon1.x_nodes[10], 100, 0,'LSA')
testrec.set_recording_point(axon1.x_nodes[10], 100, 0)



axon1.attach_extracellular_recorder(testrec)
results = axon1.simulate(t_sim=20)

plt.figure()
for rec in testrec.recording_points:
	plt.plot(results['x_rec'], rec.footprints['0'])
plt.savefig('./unitary_tests/figures/080_A.png')

plt.figure()
for rec in testrec.recording_points:
	plt.plot(results['t'],rec.recording)
plt.savefig('./unitary_tests/figures/080_B.png')

plt.figure()
map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
plt.xlabel('time (ms)')
plt.ylabel('position (µm)')
cbar = plt.colorbar(map)
cbar.set_label('membrane voltage')
plt.savefig('./unitary_tests/figures/080_C.png')

plt.show()
