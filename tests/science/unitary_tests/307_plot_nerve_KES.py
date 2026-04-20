import nrv
import matplotlib.pyplot as plt
import time
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
source_file = './unitary_tests/sources/300_fascicle_1.json'

if __name__ == "__main__":
    t0 = time.time()
    nerve = nrv.nerve(length= 10000, diameter= 500)
    nerve.set_ID(test_num)

    t_sim = 10
    nerve.add_fascicle(source_file, ID=0, y=-20, z=-60)#, extracel_context=True)
    nerve.add_fascicle(source_file, ID=1, z=65, extracel_context=True)
    nerve.fit_circular_contour()



    LIFE_stim = nrv.FEM_stimulation()
    ##### electrode and stimulus definition
    D_1 = 25
    length_1 = 1000
    y_c_1 = 0
    z_c_1 = 0
    x_1_offset = (length_1)/2
    elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset, y_c_1, z_c_1)
    # stimulus def
    freq = 5
    amp = 100
    start = 1
    duration = t_sim
    stim1 = nrv.stimulus()
    stim1.sinus(start=start, duration=duration, amplitude=amp, freq=freq, dt=0.005)
    LIFE_stim.add_electrode(elec_1, stim1)

    nerve.attach_extracellular_stimulation(LIFE_stim)

    # !BUG Shoud be done in the script
    nerve.extra_stim.synchronise_stimuli(snap_time=True)

    # nerve.extra_stim.model.build_and_mesh()
    # nerve.extra_stim.model.get_meshes()

    position = 0.05
    t_start = 5
    duration = 0.1
    amplitude = 5
    nerve.insert_I_Clamp(position, t_start, duration, amplitude)

    nerve.simulate(t_sim=t_sim, save_path='./unitary_tests/figures/', postproc_script="vmem_plot", postproc_kwargs={'freq': freq},dt =0.0025)
