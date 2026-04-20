import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    t_start = 0.1       #start of the pulse, in ms
    t_pulse = 0.1       #duration of the pulse, in ms
    amp_pulse = 60     #amplitude of the pulse, in uA 
    pulse_stim = nrv.stimulus()
    pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      #cathodic pulse

    pulse_stim2 = nrv.stimulus()
    pulse_stim2.pulse(t_start*3, amp_pulse, t_pulse/2)      #cathodic pulse

    pulse_stim3 = pulse_stim + pulse_stim2


    fig, ax = plt.subplots()
    pulse_stim.plot(ax)
    pulse_stim2.plot(ax)
    fig.savefig('./unitary_tests/figures/519_plot_stim.png')
    fig, ax = plt.subplots()
    pulse_stim3.plot(ax)
    fig.savefig('./unitary_tests/figures/519_plot_stim2.png')
    # plt.show()