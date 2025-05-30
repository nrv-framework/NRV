import nrv
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    schellens_1_diam, schellens_1_pres = nrv.load_stat('Schellens_1')
    schellens_2_diam, schellens_2_pres = nrv.load_stat('Schellens_2')
    ochoa_M_diam, ochoa_M_pres = nrv.load_stat('Ochoa_M')
    ochoa_U_diam, ochoa_U_pres = nrv.load_stat('Ochoa_U')
    Jacobs_9_A_diam, Jacobs_9_A_pres = nrv.load_stat('Jacobs_9_A')
    Jacobs_9_B_diam, Jacobs_9_B_pres = nrv.load_stat('Jacobs_9_B')
    Jacobs_9_C_diam, Jacobs_9_C_pres = nrv.load_stat('Jacobs_9_C')
    Jacobs_9_D_diam, Jacobs_9_D_pres = nrv.load_stat('Jacobs_9_D')


    Jacobs_11_A_diam, Jacobs_11_A_pres = nrv.load_stat('Jacobs_11_A')
    Jacobs_11_B_diam, Jacobs_11_B_pres = nrv.load_stat('Jacobs_11_B')
    Jacobs_11_C_diam, Jacobs_11_C_pres = nrv.load_stat('Jacobs_11_C')
    Jacobs_11_D_diam, Jacobs_11_D_pres = nrv.load_stat('Jacobs_11_D')

    plt.figure()
    plt.step(schellens_1_diam,schellens_1_pres,where='post',label='Schellens 1')
    plt.step(schellens_2_diam,schellens_2_pres,where='post',label='Schellens 2')
    plt.legend()
    plt.savefig('./unitary_tests/figures/50_A.png')

    plt.figure()
    plt.step(ochoa_M_diam,ochoa_M_pres,where='post',label='Ochoa M')
    plt.legend()
    plt.savefig('./unitary_tests/figures/50_B.png')

    plt.figure()
    plt.step(Jacobs_9_A_diam,Jacobs_9_A_pres,where='post',label='Jacobs 9A')
    plt.step(Jacobs_9_B_diam,Jacobs_9_B_pres,where='post',label='Jacobs 9B')
    plt.step(Jacobs_9_C_diam,Jacobs_9_C_pres,where='post',label='Jacobs 9C')
    plt.step(Jacobs_9_D_diam,Jacobs_9_D_pres,where='post',label='Jacobs 9D')
    plt.legend()
    plt.savefig('./unitary_tests/figures/50_C.png')

    plt.figure()
    plt.step(ochoa_U_diam,ochoa_U_pres,where='post',label='Ochoa U')
    plt.legend()
    plt.savefig('./unitary_tests/figures/50_D.png')

    plt.figure()
    plt.step(Jacobs_11_A_diam,Jacobs_11_A_pres,where='post',label='Jacobs 11A')
    plt.step(Jacobs_11_B_diam,Jacobs_11_B_pres,where='post',label='Jacobs 11B')
    plt.step(Jacobs_11_C_diam,Jacobs_11_C_pres,where='post',label='Jacobs 11C')
    plt.step(Jacobs_11_D_diam,Jacobs_11_D_pres,where='post',label='Jacobs 11D')
    plt.legend()
    plt.savefig('./unitary_tests/figures/50_E.png')

    #plt.show()