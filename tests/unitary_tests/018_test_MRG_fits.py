import nrv
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
	fiberD = np.asarray([5.7,7.3,8.7,10.0,11.5,12.8,14.0,15.0,16.0])

	# originial parameters
	g_1 = []
	axonD_1 = []
	nodeD_1 = []
	paraD1_1 = []
	paraD2_1 = []
	deltax_1 = []
	paralength2_1 = []
	nl_1 = []

	for diam in fiberD:
		g, axonD, nodeD, paraD1, paraD2, deltax, paralength2, nl = nrv.get_MRG_parameters(diam)
		g_1.append(g)
		axonD_1.append(axonD)
		nodeD_1.append(nodeD)
		paraD1_1.append(paraD1)
		paraD2_1.append(paraD2)
		deltax_1.append(deltax)
		paralength2_1.append(paralength2)
		nl_1.append(nl)

	# fig1, axs1 = plt.subplots(2, 2)
	# axs1[0,0].scatter(fiberD,g_1)
	# axs1[0,0].set_xlabel('diameter (um)')
	# axs1[0,0].set_ylabel('g')
	# axs1[0,0].grid()
	# axs1[0,1].scatter(fiberD,axonD_1)
	# axs1[0,1].set_xlabel('diameter (um)')
	# axs1[0,1].set_ylabel('axonD')
	# axs1[0,1].grid()
	# axs1[1,0].scatter(fiberD,nodeD_1)
	# axs1[1,0].set_xlabel('diameter (um)')
	# axs1[1,0].set_ylabel('nodeD')
	# axs1[1,0].grid()
	# axs1[1,1].scatter(fiberD,paraD1_1)
	# axs1[1,1].set_xlabel('diameter (um)')
	# axs1[1,1].set_ylabel('paraD1')
	# axs1[1,1].grid()

	# fig2, axs2 = plt.subplots(2, 2)
	# axs2[0,0].scatter(fiberD,paraD2_1)
	# axs2[0,0].set_xlabel('diameter (um)')
	# axs2[0,0].set_ylabel('paraD2')
	# axs2[0,0].grid()
	# axs2[0,1].scatter(fiberD,deltax_1)
	# axs2[0,1].set_xlabel('diameter (um)')
	# axs2[0,1].set_ylabel('deltax')
	# axs2[0,1].grid()
	# axs2[1,0].scatter(fiberD,paralength2_1)
	# axs2[1,0].set_xlabel('diameter (um)')
	# axs2[1,0].set_ylabel('paralength2')
	# axs2[1,0].grid()
	# axs2[1,1].scatter(fiberD,nl_1)
	# axs2[1,1].set_xlabel('diameter (um)')
	# axs2[1,1].set_ylabel('nl')
	# axs2[1,1].grid()

	# test interpolation
	diameters = np.linspace(2.5,20)
	g_2 = []
	axonD_2 = []
	nodeD_2 = []
	paraD1_2 = []
	paraD2_2 = []
	deltax_2 = []
	paralength2_2 = []
	nl_2 = []

	for diam in diameters:
		g, axonD, nodeD, paraD1, paraD2, deltax, paralength2, nl = nrv.get_MRG_parameters(diam)
		g_2.append(g)
		axonD_2.append(axonD)
		nodeD_2.append(nodeD)
		paraD1_2.append(paraD1)
		paraD2_2.append(paraD2)
		deltax_2.append(deltax)
		paralength2_2.append(paralength2)
		nl_2.append(nl)

	fig3, axs3 = plt.subplots(2, 2)
	axs3[0,0].scatter(fiberD,g_1)
	axs3[0,0].plot(diameters,g_2,color='r')
	axs3[0,0].set_xlabel('diameter (um)')
	axs3[0,0].set_ylabel('g')
	axs3[0,0].grid()
	axs3[0,1].scatter(fiberD,axonD_1)
	axs3[0,1].plot(diameters,axonD_2,color='r')
	axs3[0,1].set_xlabel('diameter (um)')
	axs3[0,1].set_ylabel('axonD')
	axs3[0,1].grid()
	axs3[1,0].scatter(fiberD,nodeD_1)
	axs3[1,0].plot(diameters,nodeD_2,color='r')
	axs3[1,0].set_xlabel('diameter (um)')
	axs3[1,0].set_ylabel('nodeD')
	axs3[1,0].grid()
	axs3[1,1].scatter(fiberD,paraD1_1)
	axs3[1,1].plot(diameters,paraD1_2,color='r')
	axs3[1,1].set_xlabel('diameter (um)')
	axs3[1,1].set_ylabel('paraD1')
	axs3[1,1].grid()
	plt.savefig('./unitary_tests/figures/18_A.png')

	fig4, axs4 = plt.subplots(2, 2)
	axs4[0,0].scatter(fiberD,paraD2_1)
	axs4[0,0].plot(diameters,paraD2_2,color='r')
	axs4[0,0].set_xlabel('diameter (um)')
	axs4[0,0].set_ylabel('paraD2')
	axs4[0,0].grid()
	axs4[0,1].scatter(fiberD,deltax_1)
	axs4[0,1].plot(diameters,deltax_2,color='r')
	axs4[0,1].set_xlabel('diameter (um)')
	axs4[0,1].set_ylabel('deltax')
	axs4[0,1].grid()
	axs4[1,0].scatter(fiberD,paralength2_1)
	axs4[1,0].plot(diameters,paralength2_2,color='r')
	axs4[1,0].set_xlabel('diameter (um)')
	axs4[1,0].set_ylabel('paralength2')
	axs4[1,0].grid()
	axs4[1,1].scatter(fiberD,nl_1)
	axs4[1,1].plot(diameters,nl_2,color='r')
	axs4[1,1].set_xlabel('diameter (um)')
	axs4[1,1].set_ylabel('nl')
	axs4[1,1].grid()
	plt.savefig('./unitary_tests/figures/18_B.png')

	#plt.show()