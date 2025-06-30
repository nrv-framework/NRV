import nrv
import matplotlib.pyplot as plt


test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
source_file = './unitary_tests/sources/56_fasc.json'

L = 10000             # length, in um

if __name__ == "__main__":
    nerve = nrv.nerve(Length=10000)
    nerve.set_ID(test_num)
    nerve.add_fascicle(source_file, ID=1, y=20)
    nerve.add_fascicle(source_file, ID=2, y=-20)
    nerve.add_fascicle(source_file, ID=3, z=17)
    nerve.fit_circular_contour()
    nerve.simulate(t_sim=2, save_path='./unitary_tests/figures/')

    fig, ax = plt.subplots(figsize=(8,8))
    nerve.plot(ax)
    plt.savefig('./unitary_tests/figures/'+str(test_num)+'_A.png')

    # plt.show()