from nrv.utils import geom
from nrv.nmod._axon_population import axon_population
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame

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

    pop_stat = axon_population()

    n_ax = 20
    assert not pop_stat.has_pop, "Axon population should not contain population at the creation."
    assert pop_stat.n_ax == 0, "Wrong number of axons."

    pop_stat.set_geometry(ellipse)
    pop_stat.create_population_from_stat(n_ax=n_ax)
    assert pop_stat.has_pop, "Axon population should contain population after setting."
    assert pop_stat.n_ax == n_ax, "Wrong number of axons."
    assert all(pop_stat.axon_pop["diameters"] == pop_stat["diameters"]), "Issue with getitems"
    assert all(pop_stat.axon_pop.loc[[0]] == pop_stat.axon_pop.loc[[0]]), "Issue with loc"




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
    pop_tup = axon_population()
    pop_tup.set_geometry(ellipse)
    pop_tup.create_population_from_data((ax_type, ax_diameters))

    assert pop_tup.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_tup.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_tup.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."

    # as np.ndarray
    data = np.vstack((ax_type, ax_diameters))
    pop_np = axon_population()
    pop_np.set_geometry(ellipse)
    pop_np.create_population_from_data(data)

    assert pop_np.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_np.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_np.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."


    # as dict
    data = {"types":ax_type, "diameters":ax_diameters, "other_key":0}
    pop_dict = axon_population()
    pop_dict.set_geometry(ellipse)
    pop_dict.create_population_from_data(data)

    print(pop_dict.axon_pop["types"], ax_type)
    assert pop_dict.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_dict.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_dict.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."


    # as dataframe
    data = DataFrame({"types":ax_type, "diameters":ax_diameters, "other_key":np.random.rand(len(ax_type))})
    pop_df = axon_population()
    pop_df.set_geometry(ellipse)
    pop_df.create_population_from_data(data)

    assert pop_df.has_pop, "Axon population should contain population after setting."
    assert np.allclose(pop_df.axon_pop["types"], ax_type), "Wrong axon types."
    assert np.allclose(pop_df.axon_pop["diameters"], ax_diameters), "Wrong axon diamters."


def test_axon_pop_set_from_file():
    # 
    center = 1000, 2000
    r = 3000, 2000
    angle = -np.pi/12
    ellipse = geom.Ellipse(center, r, angle)
    
    fname = test_dir + "sources/52_test.pop"
    # as tupple
    pop_tup = axon_population()
    pop_tup.set_geometry(ellipse)
    pop_tup.create_population_from_data(data=fname)


    assert pop_tup.has_pop, "Axon population should contain population after setting."
    assert pop_tup.n_ax == 250, "Wrong number of axons."



if __name__ == "__main__":
    test_axon_pop_set_from_stat()
    test_axon_pop_set_from_data()
    test_axon_pop_set_from_file()
    print("All tests passed successfully.")


