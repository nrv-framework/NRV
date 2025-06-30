import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

L = 10000             # length, in um


def test_load_fascicle():
    start_time = time.time()
    fascicle_1 = nrv.fascicle()
    fascicle_1.load('./unitary_tests/sources/56_fasc.json')
    fascicle_1.define_length(L)
    fascicle_1.simulate(t_sim=2)

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax)
    fig.savefig(figdir + 'A.png')

def test_load_deprecated_file():
    start_time = time.time()
    L = 10000             # length, in um
    fascicle_1 = nrv.fascicle()
    fascicle_1.load('./unitary_tests/sources/56_fasc_depr.json')
    fascicle_1.define_length(L)
    fascicle_1.simulate(t_sim=2)

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax)
    fig.savefig(figdir + 'B.png')

if __name__ == "__main__":
    test_load_fascicle()
    test_load_deprecated_file()
    # plt.show()
