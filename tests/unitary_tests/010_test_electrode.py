import nrv
import numpy as np
import matplotlib.pyplot as plt

# mimicing axon coordinates
L = 10000 # in um
x = np.linspace(0,1,num=500)*L
y = 0
z = 0

# I stim, in uA
Icath = -100
I0 = 0
Ian = 10

epineurium = nrv.load_material('endoneurium_ranck')

# electrode position, in um
x_elec = L/2
y_elec = 100
z_elec = 0

E1 = nrv.point_source_electrode(x_elec,y_elec,z_elec)
E1.compute_footprint(x,y,z,epineurium)
v_ext_cath = E1.compute_field(Icath)
v_ext_0 = E1.compute_field(I0)
v_ext_an = E1.compute_field(Ian)

plt.figure()
plt.plot(x,v_ext_cath)
plt.plot(x,v_ext_0)
plt.plot(x,v_ext_an)
plt.savefig('./unitary_tests/figures/10_A.png')

epi_Bhadra = nrv.load_material('endoneurium_bhadra')
E1.compute_footprint(x,y,z,epi_Bhadra)
v_ext_cath2 = E1.compute_field(Icath)

plt.figure()
plt.plot(x,v_ext_cath2)
plt.savefig('./unitary_tests/figures/10_B.png')

#plt.show()