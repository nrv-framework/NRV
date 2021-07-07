import nrv
import numpy as np

y = 0
z = 0
d = 1
L = 5000

#print('axon 1')
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nsec=1)
x_s1, y_s1, z_s1 = axon1._axon__get_allseg_positions()
print(y_s1 == y)
print(z_s1 == z)
vext = np.zeros(len(x_s1)) + 10
axon1._axon__set_allseg_vext(vext)
del axon1


#print('axon 2')
axon2 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nsec=10)
x_s2, y_s2, z_s2 = axon2._axon__get_allseg_positions()
print(y_s2 == y)
print(z_s2 == z)
del axon2