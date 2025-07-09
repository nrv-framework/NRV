import nrv
import matplotlib.pyplot as plt
import time
import numpy as np
import os

#nrv.parameters.set_nrv_verbosity(4)

def test__mesh_geom_dbg_creation():
    test_num = 303
    source_file = './unitary_tests/sources/56_fasc.json'
    nerve = nrv.nerve(diameter=200)
    nerve.set_ID(test_num)
    
    fasc = nrv.fascicle(diameter=100)
    fasc.fill(n_ax=100)
    nerve.add_fascicle(fasc, ID=0, y=-20, z=-60)#, extracel_context=True)



    LIFE_stim = nrv.FEM_stimulation()
    ##### electrode and stimulus definition
    D_1 = 25
    length_1 = 1000
    x_1_offset = (length_1)/2
    elec_1 = nrv.LIFE_electrode('LIFE_1', D_1, length_1, x_1_offset)
    # stimulus def
    freq = 10
    amp = 10
    start = 0
    duration = 10
    stim1 = nrv.stimulus()
    LIFE_stim.add_electrode(elec_1, stim1)

    nerve.attach_extracellular_stimulation(LIFE_stim)
    #nerve.compute_electrodes_footprints()
    try:
        nerve.simulate(t_sim=5)
        assert 1==0, "should complete the simulation"
    except TypeError:
        print("...Expected error")
        fname = "./__mesh_geom_dbg.brep"
        assert os.path.isfile("./__mesh_geom_dbg.brep"), fname + "should have been created when meshin crased"
        os.remove("./__mesh_geom_dbg.brep")

    except Exception as e:
        nrv.rise_error(e)

if __name__ == "__main__":
    test__mesh_geom_dbg_creation()
    print("all tests are ok")

    # plt.show()
