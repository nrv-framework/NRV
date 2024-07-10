import nrv
import matplotlib.pyplot as plt

y = 0
z = 0
d = 10
L = 20000

########## test A : myelinated record all #############
axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='nodes')
print(axon1.node_index)
