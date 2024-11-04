#pragma parallel
import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    test_num = "512"

    L=nrv.get_length_from_nodes(10,3)         #um
    ax1 = nrv.myelinated(d=10, L=L, rec="all", t_sim=1)
    res = ax1()
    del ax1

    x_ticks = (res.x_rec[1:] + res.x_rec[:-1])/2

    lab = [res.get_index_myelinated_sequence(x) for x in range(1,len(res.x_rec))]
    xlim = (0.97*L/2, 1.03*L/2)
    plt.xticks(ticks=x_ticks, labels=lab, rotation=90)
    plt.xlim(xlim)
    plt.twiny()

    plt.plot(res.x_rec, [0 for _ in res.x_rec], '|', markersize=300)
    plt.xlim(xlim)

    plt.savefig(f"./unitary_tests/figures/{test_num}_A.png")
    #plt.show()
