import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":
    start_time = time.time()
    L = 10000             # length, in um
    fascicle_1 = nrv.fascicle()
    fascicle_1.load('./unitary_tests/sources/56_fasc.json')
    fascicle_1.define_length(L)
    #fascicle_1.generate_random_NoR_position()
    fascicle_1.simulate(save_path='./unitary_tests/figures/')

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax)
    plt.savefig('./unitary_tests/figures/56_A.png')
    #plt.show()
