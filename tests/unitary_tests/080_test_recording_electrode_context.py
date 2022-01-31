import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 1
L = 5000

t_start = 1
duration = 0.5
amplitude = 5

# test recording
testrec = nrv.recorder()
testrec.set_recording_point(L/4, 0, 100)
testrec.set_recording_point(L/2, 0, 100)
testrec.set_recording_point(3*L/4, 0, 100)
print(len(testrec.recording_points))
print(testrec.is_empty())


# test 1: 1 section stim in middle
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nrec=100)
axon1.insert_I_Clamp(0.01, t_start, duration, amplitude)
axon1.attach_extracellular_recorder(testrec)
results = axon1.simulate(t_sim=10)

plt.figure()
for rec in testrec.recording_points:
	print(rec.recording)
	plt.plot(results['x_rec'], rec.footprints['0'])

plt.show()