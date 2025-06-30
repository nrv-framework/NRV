import nrv
import matplotlib.pyplot as plt
import numpy as np

def plot_stim(stim, t_stop=None, N_plot=1000):
    stim = nrv.load_any(stim)
    if t_stop is None:
        t_stop = stim.t[-1]
    stim2 = nrv.stimulus()
    stim2.s = np.zeros(N_plot)
    stim2.t = np.linspace(0, t_stop, N_plot)
    stim2 += stim
    plt.plot(stim2.t, stim2.s)

if __name__ == "__main__":
    test_stim_CM = nrv.biphasic_stimulus_CM(start="0", s_cathod="1")


    t_sim=5
    static_context = "./unitary_tests/sources/202_axon.json"
    X = np.array([
        [1, 1],
        [1, 20],
        [1, 40],
        [1, 60],
        [1, 80],
        [1, 100],
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
        plt.figure(2)
        plt.subplot(2,3,i+1)
        map = plt.pcolormesh(results['t'], results['x_rec'], results['V_mem'] ,shading='auto')
        plt.xlabel('time (ms)')
        plt.ylabel('position (µm)')


    cbar = plt.colorbar(map)
    cbar.set_label('membrane voltage (mV)')
    plt.figure(1)
    plt.savefig('./unitary_tests/figures/202_A.png')
    plt.figure(2)
    plt.savefig('./unitary_tests/figures/202_B.png')

    # plt.show()