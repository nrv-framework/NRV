import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    test_num = 302
    source_file = './unitary_tests/sources/56_fasc.json'
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(test_num)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=1, y=20, z=-20)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=2, y=-20, z=-20)
    nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=3, z=35, intracel_context=True)
    nerve.fit_circular_contour()



    position = 0.5
    t_start = 1
    duration = 0.5
    amplitude = 4
    nerve.insert_I_Clamp(position, t_start, duration, amplitude)



    nerve.simulate(t_sim=5, save_path='./unitary_tests/figures/', postproc_script='raster_plot')

    fig, ax = plt.subplots(figsize=(8,8))
    nerve.plot(ax)
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

    #plt.show()