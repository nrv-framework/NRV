import nrv 
import matplotlib.pyplot as plt

if __name__ == "__main__":
    test_num = 535
    source_file = './unitary_tests/sources/56_fasc.json'
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(test_num)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=1, y=20, z=-20)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=2, y=-20, z=-20)
    nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=3, z=35, intracel_context=True)
    nerve.fit_circular_contour()

    position = 0.5
    t_start = 0.2
    duration = 0.5
    amplitude = 4
    nerve.insert_I_Clamp(position, t_start, duration, amplitude)

    nerve.save_results = False
    nerve.return_parameters_only = False
    nerve.verbose = True

    nerve_results = nerve.simulate(t_sim=3, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 1)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig('./unitary_tests/figures/535_clear_clamps_nerve_A.png')

    nerve.clear_I_clamp()
    nerve_results = nerve.simulate(t_sim=3, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 0)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig('./unitary_tests/figures/535_clear_clamps_nerve_B.png')

    nerve.insert_I_Clamp(position, t_start, duration, amplitude)
    nerve_results = nerve.simulate(t_sim=3, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 1)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig('./unitary_tests/figures/535_clear_clamps_nerve_C.png')

    #plt.show()