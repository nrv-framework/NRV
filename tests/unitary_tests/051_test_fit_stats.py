import nrv
import numpy as np
import matplotlib.pyplot as plt


# test fit myelinated with 2 lobes Gamma distribution
myelinated_stats = ['Schellens_1','Schellens_2','Ochoa_M','Jacobs_9_A','Jacobs_9_B','Jacobs_9_C','Jacobs_9_D']
for stat in myelinated_stats:
	#print(stat)
	gen, popt1, pcov1 = nrv.create_generator_from_stat(stat)
	diam, pres = nrv.load_stat(stat)
	#print(popt1)
	xspace1 = np.linspace(2,14,num=100)
	plt.figure()
	plt.step(diam,pres,where='post',label=stat)
	if (len(popt1)>3):
		plt.plot(xspace1, nrv.two_Gamma(xspace1, *popt1),label='identified')
	else:
		plt.plot(xspace1, nrv.one_Gamma(xspace1, *popt1),label='identified')
	plt.legend()
	plt.savefig('./unitary_tests/figures/51_'+stat+'.png')

# test fit unmyelinated with 1 lobe Gamma distribution
unmyelinated_stats = ['Ochoa_U','Jacobs_11_A','Jacobs_11_B','Jacobs_11_C','Jacobs_11_D']
for stat in unmyelinated_stats:
	#print(stat)
	gen, popt1, pcov1 = nrv.create_generator_from_stat(stat)
	diam, pres = nrv.load_stat(stat)
	xspace1 = np.linspace(0.2,2,num=100)
	plt.figure()
	plt.step(diam,pres,where='post',label=stat)
	plt.plot(xspace1, nrv.one_Gamma(xspace1, *popt1),label='identified')
	plt.legend()
	plt.savefig('./unitary_tests/figures/51_'+stat+'.png')
#plt.show()
