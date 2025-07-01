import nrv 
import matplotlib.pyplot as plt


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
sfile = './unitary_tests/sources/56_fasc.json'

if __name__ == "__main__":

    nerve = nrv.nerve(Length=1000)
    # !BUG automation of nseg: uncoment 
    # nerve = nrv.nerve(Length=10_000)
    nerve.set_ID(test_num)
    nerve.add_fascicle(sfile, ID=1, y=20, z=-20)
    nerve.add_fascicle(sfile, ID=2, y=-20, z=-20)
    nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=3, z=35, intracel_context=True)
    nerve.fit_circular_contour()

    position = 0.5
    t_start = 0
    duration = 0.5
    amplitude = 10
    nerve.insert_I_Clamp(position, t_start, duration, amplitude)

    # nerve.save_path = "nerve"
    # nerve.save_results = True
    # nerve.return_parameters_only = False
    # nerve.verbose = True

    # !BUG automation of nseg: following line should be automated
    nerve.set_axons_parameters(unmyelinated_nseg=200)
    # !when unmyelinated_nseg to low no AP cannot be trigered
    nerve_results = nerve.simulate(t_sim=10, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 1)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig(figdir+'A.png')

    nerve.clear_I_clamp()
    nerve_results = nerve.simulate(t_sim=3, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 0)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig(figdir+'B.png')

    nerve.insert_I_Clamp(position, t_start, duration, amplitude)
    nerve_results = nerve.simulate(t_sim=3, postproc_script='is_recruited')
    assert (nerve_results.get_recruited_axons(normalize=True) == 1)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    fig.savefig(figdir+'C.png')

    plt.show()