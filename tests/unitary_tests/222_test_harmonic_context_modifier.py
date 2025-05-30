import nrv
import matplotlib.pyplot as plt
import numpy as np

def plot_stim(stim, t_stop=None, N_plot=10000):
    '''
    stim = nrv.load_any(stim)
    if t_stop is None:
        t_stop = stim.t[-1]
    stim2 = nrv.stimulus()
    stim2.s = np.zeros(N_plot)
    stim2.t = np.linspace(0, t_stop, N_plot)
    stim2 += stim
    plt.plot(stim2.t, stim2.s)
    '''
    plt.step(stim.t, stim.s,where='post')

if __name__ == "__main__":
    start = 1
    t_pulse = 100e-3
    amplitude = 200

    test_stim_CM = nrv.harmonic_stimulus_CM(start=start,t_pulse=t_pulse)


    t_sim=5
    static_context = "./unitary_tests/sources/202_axon.json"
    X = [
        [amplitude,0.2,0],
        [amplitude,0.2,0,0.4,0],
        [amplitude,0.2,0,0.4,0,0.6,0],
        [amplitude,0.8,0,0.4,0,0.6,0,0.8,0]
    ]

    results = []
    # simulate the axon
    plt.figure(1)
    plt.figure(2)
    for i, x in enumerate(X):
        print(x)
        ax = test_stim_CM(x, static_context)
        test_stim = ax.extra_stim.stimuli[0]
        '''
        plt.plot(test_stim.t,test_stim.s)
        #plt.show()
        exit()
        '''
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
    plt.savefig('./unitary_tests/figures/222_A.png')
    plt.figure(2)
    plt.savefig('./unitary_tests/figures/222_B.png')

    #plt.show()