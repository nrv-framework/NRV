import nrv
import matplotlib.pyplot as plt

# Fascicle config
L = 10000 			# length, in um
source_file = './unitary_tests/sources/56_fasc.json'
# intra cellular stimulation parameters
position = 0.
t_start = 1
duration = 0.5
amplitude = 4


# test recording
testrec = nrv.recorder('endoneurium_bhadra')
testrec.set_recording_point(L/4, 0, 100)
testrec.set_recording_point(L/2, 0, 100)
testrec.set_recording_point(3*L/4, 0, 100)


# Fascicle declaration
fascicle_1 = nrv.fascicle()
fascicle_1.load_fascicle_configuration(source_file)
fascicle_1.define_length(L)
fascicle_1.set_ID(82)
# intra cellular stimulation
fascicle_1.insert_I_Clamp(position, t_start, duration, amplitude)
fascicle_1.attach_extracellular_recorder(testrec)
# simulation
fascicle_1.simulate(t_sim=10, save_path='./unitary_tests/figures/')
plt.figure()
for rec in testrec.recording_points:
	plt.plot(testrec.t,rec.recording)

plt.show()