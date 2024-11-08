import nrv
import numpy as np
import matplotlib.pyplot as plt
import time

if __name__ == "__main__":
    myelinated_stats = [
        "Schellens_1",
        "Schellens_2",
        "Ochoa_M",
        "Jacobs_9_A",
        "Jacobs_9_B",
        "./unitary_tests/sources/Fugleholm"
    ]
    unmyelinated_stats = [
        "Ochoa_U",
        "Jacobs_11_A",
        "Jacobs_11_B",
        "Jacobs_11_C",
        "Jacobs_11_D",
        "Jacobs_11_D",
    ]

    N = 500


    for k in range(len(myelinated_stats)):
        start = time.time()
        m_stat = myelinated_stats[k]
        u_stat = unmyelinated_stats[k]

        axons_diameters, axons_type, M_diam_list, U_diam_list = nrv.create_axon_population(N,M_stat=m_stat,U_stat=u_stat)
        t = time.time() - start

        print('Population of '+str(N)+' axons generated in '+str(t)+' s')


        plt.figure()
        y_M, x, _ =plt.hist(M_diam_list,bins = 50,color = 'blue',label='Myelinated')
        y_U, x, _ =plt.hist(U_diam_list,bins = 50,color = 'red',label='Unmyelinated')


        gen, popt1, pcov1 = nrv.create_generator_from_stat(m_stat,dmin = 1,dmax = 20)
        diam, pres = nrv.load_stat(m_stat)
        xspace1 = np.linspace(1,20,num=500)
        if (len(popt1)>4):
            data = (nrv.two_Gamma(xspace1, *popt1))
        else:
            data = (nrv.one_Gamma(xspace1, *popt1))
        scale_factor= np.max(y_M)
        data = data*scale_factor/np.max(data)
        pres = pres*scale_factor/np.max(pres)
        plt.plot(xspace1,data)
        plt.plot(diam,pres)

        gen, popt1, pcov1 = nrv.create_generator_from_stat(u_stat,dmin = 0.1,dmax = 3)
        diam, pres = nrv.load_stat(u_stat)
        xspace1 = np.linspace(0.1,3,num=500)
        data = (nrv.one_Gamma(xspace1, *popt1))
        scale_factor= np.max(y_U)
        data = data*scale_factor/np.max(data)
        pres = pres*scale_factor/np.max(pres)
        plt.plot(xspace1,data)
        plt.plot(diam,pres)

        if ("Fugleholm" in m_stat):
            m_stat = 'Fugleholm'

        fig_name = '52_mpop_'+m_stat+'_upop_'+u_stat+'.png'
        pop_name = '52_mpop_'+m_stat+'_upop_'+u_stat+'.pop'

        nrv.save_axon_population('./unitary_tests/results/'+pop_name,axons_diameters, axons_type)
        axons_diameters_2, axons_type_2, M_diam_list_2, U_diam_list_2, _, _ = nrv.load_axon_population('./unitary_tests/results/'+pop_name)
        #print(fig_name)
        plt.savefig('./unitary_tests/figures/'+fig_name)
        plt.close('all')
        #plt.show()
