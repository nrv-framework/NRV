import nrv
import numpy as np
import matplotlib.pyplot as plt

diameter = np.linspace(1.5,6, num=100)
axonD = []
nodeD = []
paraD = []
deltax = []
nl = []
for d in diameter:
	axonD_v, nodeD_v, paraD_v, deltax_v, nl_v  = nrv.get_Adelta_parameters(d)
	axonD.append(axonD_v)
	nodeD.append(nodeD_v)
	paraD.append(paraD_v)
	deltax.append(deltax_v)
	nl.append(nl_v)

plt.figure()
plt.plot(diameter,axonD)
plt.xlabel('Axon Diameter (um)')
plt.ylabel('Internode diameter under myelin (um)')
plt.grid()
plt.savefig('./unitary_tests/figures/42_A.png')

plt.figure()
plt.plot(diameter,nodeD)
plt.xlabel('Axon Diameter (um)')
plt.ylabel('Node diameter (um)')
plt.grid()
plt.savefig('./unitary_tests/figures/42_B.png')

plt.figure()
plt.plot(diameter,paraD)
plt.xlabel('Axon Diameter (um)')
plt.ylabel('Juxtaparanode diameter under myelin (um)')
plt.grid()
plt.savefig('./unitary_tests/figures/42_C.png')

plt.figure()
plt.plot(diameter,deltax)
plt.xlabel('Axon Diameter (um)')
plt.ylabel('Node to node distance (um)')
plt.grid()
plt.savefig('./unitary_tests/figures/42_D.png')

plt.figure()
plt.plot(diameter,nl)
plt.xlabel('Axon Diameter (um)')
plt.ylabel('Number of mylin layer')
plt.grid()
plt.savefig('./unitary_tests/figures/42_E.png')

#plt.show()