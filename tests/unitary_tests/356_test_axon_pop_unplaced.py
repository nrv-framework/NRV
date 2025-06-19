from nrv.utils import geom
from nrv.nmod._axon_population import axon_population
import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"


def test_axon_pop_set_from_stat():
    # 
    center = 1000, 2000
    r = 3000, 2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)

    pop_1 = axon_population()

    n_ax = 20
    assert not pop_1.has_pop, "Axon population should not contain population at the creation."
    assert pop_1.n_ax == 0, "Wrong number of axons."

    pop_1.set_geometry(ellipse)
    pop_1.create_population_from_stat(n_ax=n_ax)
    assert pop_1.has_pop, "Axon population should contain population after setting."
    assert pop_1.n_ax == n_ax, "Wrong number of axons."
    assert all(pop_1.axon_pop["diameters"] == pop_1["diameters"]), "Issue with getitems"
    assert all(pop_1.axon_pop.loc[[0]] == pop_1.axon_pop.loc[[0]]), "Issue with loc"




def test_axon_pop_set_from_data():
    # 
    center = (1000, 2000)
    r = 3000, 2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)
    n_ax = 10
    # Randomly generate axon types and diameters
    ax_type = np.random.randint(0,1,n_ax)
    ax_diameters = np.random.random(n_ax)*20

    # as tupple
    pop_1 = axon_population()
    pop_1.set_geometry(ellipse)
    pop_1.create_population_from_data((ax_type, ax_diameters))

    # as np.ndarray
    data = np.vstack((ax_type, ax_diameters))
    pop_2 = axon_population()
    pop_2.set_geometry(ellipse)
    pop_2.create_population_from_data(data)

    assert pop_1.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_1.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_1.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."

    assert pop_2.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_2.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_2.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."



def test_axon_pop_set_from_file():
    # 
    center = 1000, 2000
    r = 3000, 2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)
    
    fname = test_dir + "sources/52_test.pop"
    # as tupple
    pop_1 = axon_population()
    pop_1.set_geometry(ellipse)
    pop_1.create_population_from_data(data=fname)


    assert pop_1.has_pop, "Axon population should contain population after setting."
    assert pop_1.n_ax == 250, "Wrong number of axons."



if __name__ == "__main__":
    test_axon_pop_set_from_stat()
    test_axon_pop_set_from_data()
    test_axon_pop_set_from_file()
    print("All tests passed successfully.")


