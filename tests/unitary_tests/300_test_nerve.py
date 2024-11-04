import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    test_num = 300
    source_file = './unitary_tests/sources/56_fasc.json'
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(test_num)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=1, y=20)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=2, y=-20)
    nerve.add_fascicle('./unitary_tests/sources/56_fasc.json', ID=3, z=17)
    nerve.fit_circular_contour()
    nerve.simulate(t_sim=2, save_path='./unitary_tests/figures/')

    if nrv.MCH.do_master_only_work():
        fig, ax = plt.subplots(figsize=(8,8))
        nerve.plot(ax)
        plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

    #plt.show()