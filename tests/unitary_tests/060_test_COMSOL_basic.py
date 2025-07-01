import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    my_model = nrv.COMSOL_model('Nerve_1_Fascicle_2_LIFE')
    params = my_model.get_parameters()

    #print(type(params[0]))
    #print(params[0])

    before = my_model.get_parameter('Outer_D')

    my_model.set_parameter('Outer_D', '5.5[mm]')
    after = my_model.get_parameter('Outer_D')
    print(before != after)
    my_model.build_and_mesh()
    my_model.solve()
    x = np.linspace(0,5000,num = 1000)
    y = 0
    z = 0
    V = my_model.get_potentials(x, y, z)

    #print(V[:, 0])

    my_model.export(path='./unitary_tests/figures/60_')

    del my_model

    plt.figure()
    plt.plot(x, V[:,0])
    plt.plot(x, V[:,1])
    plt.xlabel('position (um)')
    plt.ylabel('extracellular potential (mV)')
    plt.savefig('./unitary_tests/figures/60_A.png')


    # plt.show()