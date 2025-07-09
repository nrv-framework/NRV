import nrv

import matplotlib.pyplot as plt
import numpy as np

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
sfile = "./unitary_tests/sources/200_fascicle_1"
if __name__ == "__main__":
#creating the fascicles are populating them
    m_model = 'MRG'
    um_model = 'Rattay_Aberham'
    u_param = {"model": um_model}
    m_param = {"model": m_model}
    fasc1_d = 200       # in um
    fasc1_y = -100      # in um
    fasc1_z = 0         # in um

    fascicle_1_c = nrv.fascicle(diameter=fasc1_d,ID=1)
    fascicle_2_c = nrv.fascicle(diameter=fasc2_d, ID=2)
    fascicle_2_c.set_geometry(geometry=geom2)

    fascicle_1_c.fill(data=ax_pop[["types", "diameters"]], delta=5, fit_to_size=True)
    fascicle_2_c.fill_with_population(ax_pop[["types", "diameters"]], delta=5, fit_to_size = True)

    #set simulation parameters
    fascicle_1_c.set_axons_parameters(unmyelinated_only=True,**u_param)
    fascicle_1_c.set_axons_parameters(myelinated_only=True,**m_param)
    fascicle_2_c.set_axons_parameters(unmyelinated_only=True,**u_param)
    fascicle_2_c.set_axons_parameters(myelinated_only=True,**m_param)

    #create the nerve and add fascicles
    nerve_cuff = nrv.nerve(length=nerve_l, diameter=nerve_d, Outer_D=outer_d)
    nerve_cuff.add_fascicle(fascicle=fascicle_1_c, y=fasc1_y, z=fasc1_z)
    nerve_cuff.add_fascicle(fascicle=fascicle_2_c, y=fasc2_y, z=fasc2_z)

    #set the simulation flags
    nerve_cuff.save_results = False
    nerve_cuff.return_parameters_only = False
    nerve_cuff.verbose = True
