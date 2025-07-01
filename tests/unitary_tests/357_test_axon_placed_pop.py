from nrv.utils import geom, sci_round
from nrv.nmod._axon_population import axon_population
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_axon_pop_placer():
    center = (100, 200)
    r = 300, 100
    angle = -np.pi/12
    n_ax = 400

    pop_1 = axon_population()
    pop_1.set_geometry(center=center, radius=r, rot=angle)
    pop_1.create_population_from_stat(n_ax=n_ax)
    assert not pop_1.has_placed_pop, "Axon population should not contain placed population at the creation."


    pop_1.place_population(delta=1, delta_trace=10)
    print(pop_1.get_ppop_info(verbose=True))
    assert pop_1.has_placed_pop, "Axon population should contain placed population."

    fig, ax = plt.subplots()
    pop_1.plot(ax)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(figdir+"A.png")


    pop_1.clear_population_placement()
    assert not pop_1.has_placed_pop, "Should not be placed."



def test_axon_pop_placer_packer():
    center = (100, 200)
    r = 300
    n_ax = 400

    pop_1 = axon_population()
    pop_1.set_geometry(center=center, radius=r)
    pop_1.create_population_from_stat(n_ax=n_ax)
    assert not pop_1.has_placed_pop, "Axon population should not contain placed population at the creation."

    t_0 = perf_counter()
    pop_1.place_population(method="packing", delta=1, fit_to_size=True)
    t_pack = perf_counter() - t_0
    print(pop_1.get_ppop_info(verbose=True))
    assert pop_1.has_placed_pop, "Axon population should contain placed population."

    pop_2 = axon_population()
    pop_2.set_geometry(center=center, radius=r)
    pop_2.create_population_from_data((pop_1.axon_pop["types"], pop_1.axon_pop["diameters"]))

    t_0 = perf_counter()
    pop_2.place_population(method="default", delta=10)
    t_plac = perf_counter() - t_0




    fig, axs = plt.subplots(1,2)
    pop_1.plot(axs[0])
    axs[0].set_aspect('equal', adjustable='box')
    axs[0].set_title(f"Axon Packer: {sci_round(t_pack)}s")
    pop_2.plot(axs[1])
    axs[1].set_aspect('equal', adjustable='box')
    axs[1].set_title(f"Axon Placer: {sci_round(t_plac)}s")
    fig.savefig(figdir+"B.png")


def test_axon_generate():
    center = (100, 200)
    r = 300, 100
    angle = -np.pi/12
    n_ax = 400
    delta=1, 
    delta_trace=10

    pop_1 = axon_population(center=center, radius=r, rot=angle, n_ax=n_ax, delta=delta, delta_trace=delta_trace)

    fig, ax = plt.subplots()
    pop_1.plot(ax)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig(figdir+"AC.png")


    pop_1.clear_population_placement()
    assert not pop_1.has_placed_pop, "Should not be placed."



if __name__ == "__main__":
    test_axon_generate()
    test_axon_pop_placer()
    test_axon_pop_placer_packer()
    print("All tests passed successfully.")

    # plt.show()
