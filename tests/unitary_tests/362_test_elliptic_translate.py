import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"

L = 10000             # length, in um


def test_translate_cir_fascicle():
    start_time = time.time()
    fascicle_1 = nrv.load_fascicle('./unitary_tests/sources/56_fasc.json')
    fascicle_1.define_length(L)
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True, contour_color=("k",.1), unmyel_color=("r", .1), myel_color=("b", .1))
    fascicle_1.translate(30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.2), unmyel_color=("r", .2), myel_color=("b", .2))
    fascicle_1.translate(y=-30, z=-30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.4), unmyel_color=("r", .4), myel_color=("b", .4))
    fascicle_1.translate(y=30)

    fascicle_1.simulate(t_sim=2)

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fascicle_1.plot(ax, num=True)
    fig.savefig(figdir + 'A.png')

def test_translate_el_fascicle():
    start_time = time.time()
    fascicle_1 = nrv.load_fascicle('./unitary_tests/sources/360_fascicle_e0.json')
    fascicle_1.define_length(L)
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True, contour_color=("k",.1), unmyel_color=("r", .1), myel_color=("b", .1))
    fascicle_1.translate(30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.2), unmyel_color=("r", .2), myel_color=("b", .2))
    fascicle_1.translate(y=-30, z=-30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.4), unmyel_color=("r", .4), myel_color=("b", .4))
    fascicle_1.translate(y=30)

    fascicle_1.simulate(t_sim=2)

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fascicle_1.plot(ax, num=True)
    fig.savefig(figdir + 'B.png')

def test_translate_el_fascicle_with_elec():
    start_time = time.time()
    fascicle_1 = nrv.load_fascicle('./unitary_tests/sources/360_fascicle_e0.json', extracel_context=True)
    fascicle_1.define_length(L)
    fig, ax = plt.subplots(figsize=(8,8))
    fascicle_1.plot(ax, num=True, contour_color=("k",.1), unmyel_color=("r", .1), myel_color=("b", .1), elec_color=("gold", .1))
    fascicle_1.translate(30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.2), unmyel_color=("r", .2), myel_color=("b", .2), elec_color=("gold", .2))
    fascicle_1.translate(y=-30, z=-30)
    fascicle_1.plot(ax, num=True, contour_color=("k",.4), unmyel_color=("r", .4), myel_color=("b", .4), elec_color=("gold", .4))
    fascicle_1.translate(y=30)

    fascicle_1.simulate(t_sim=2)

    sim_time = time.time() - start_time
    print('simulation performed in '+str(sim_time)+' s')
    fascicle_1.plot(ax, num=True)
    fig.savefig(figdir + 'C.png')

if __name__ == "__main__":
    test_translate_cir_fascicle()
    test_translate_el_fascicle()
    test_translate_el_fascicle_with_elec()
    # plt.show()
