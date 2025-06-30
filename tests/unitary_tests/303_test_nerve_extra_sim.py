import nrv
import matplotlib.pyplot as plt
import time
import numpy as np
import os

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

if __name__ == "__main__":
    t0 = time.time()
    source_file = './unitary_tests/sources/300_fascicle_1.json'
    nerve = nrv.nerve(diameter=1_000)
    nerve.set_ID(int(test_num))

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
    freq = 10
    amp = 10
    start = 0
    duration = 10
    stim1 = nrv.stimulus()
    stim1.sinus(start=start, duration=duration, amplitude=amp, freq=freq, dt=0.005)
    stim1.t = np.round(stim1.t, 4)
    LIFE_stim.add_electrode(elec_1, stim1)

    nerve.attach_extracellular_stimulation(LIFE_stim)
    #nerve.compute_electrodes_footprints()


    start = 0
    I_cathod = 40
    I_anod = I_cathod/5
    T_cathod = 100e-3
    T_inter = 50e-3
    stim2 = nrv.stimulus()
    stim2.biphasic_pulse(start, I_cathod, T_cathod, I_anod, T_inter)
    stim2.t = np.round(stim2.t, 4)
    nerve.change_stimulus_from_electrode(1,stimulus=stim2)

    t1 = time.time()
    print("Nerve preparation time "+str(t1-t0))



    res = nerve.simulate(t_sim=5, postproc_script="is_recruited")
    t2 = time.time()
    print("Nerve simulation time "+str(t2-t1))
    
    fig, axs = plt.subplots(1,2,figsize=(8,4))
    nerve.plot(axs[0])
    res.plot_recruited_fibers(axes=axs[1])
    plt.savefig(figdir+'_A.png')

    # plt.show()
