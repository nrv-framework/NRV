
import nrv
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    t_sim=7


    kwrgs_interp = {
        "dt": 0.005,
        "amp_start": 0,
        "amp_stop": 0,
        "intertype": "Spline",
        "bounds": (0, 0),
        "fixed_order": False,
        "t_end": t_sim-1,
        }
    test_stim_CM = nrv.stimulus_CM(interpolator=nrv.interpolate_Npts, intrep_kwargs=kwrgs_interp, t_sim=t_sim)


    static_context = "./unitary_tests/sources/202_axon.json"
    X = np.array([
        [1, -.1, 4, .1],
        [1, -20, 4, .1],
        [1, -40, 4, .1],
        [1, -60, 4, .1],
        [.5, -20, 1, .1],
        [.5, -20, 4, .1],
    ])


    results = []
    # simulate the axon
    plt.figure(1)
    plt.figure(2)
    for i, x in enumerate(X):
        print(x)
        ax = test_stim_CM(x, static_context)
        results = ax(t_sim=t_sim)
        del ax


        plt.figure(1)
        results.plot_stim(0, t_stop=t_sim)
        plt.plot(x[::2], x[1::2], 'ok')
        plt.figure(2)
        plt.subplot(2,3,i+1)
        map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
        plt.xlabel('time (ms)')
        plt.ylabel('position (µm)')


    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.figure(1)
    plt.savefig('./unitary_tests/figures/203_A.png')
    plt.figure(2)
    plt.savefig('./unitary_tests/figures/203_B.png')
    # plt.show()