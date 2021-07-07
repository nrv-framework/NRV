import nrv
# Note : every print should be true

y = 0
z = 0
d = 3
L = 1000

# test 1:  
axon1 = nrv.thin_myelinated(y,z,d,L,dt=0.001,Nseg_per_sec=1,node_shift = 0)
print(len(axon1.node) == 7)
print(len(axon1.MYSA) == 13)
#print(len(axon1.FLUT)==2*len(axon1.node))
print(len(axon1.STIN)> 6*(len(axon1.node)-1))
axon1.topology()
del axon1

# test 2: 
axon2 = nrv.thin_myelinated(y,z,d,L,dt=0.001,Nseg_per_sec=1,node_shift = 0.5,rec = 'nodes')
axon2.topology()
print(axon2.Nsec == axon2.axonnodes + axon2.paranodes + axon2.axoninter)
print(len(axon2.node)==axon2.axonnodes)
print(len(axon2.MYSA)==axon2.paranodes)
print(len(axon2.STIN)==axon2.axoninter)
print(axon2.x_rec == axon2.x_nodes)
print(len(axon2.x_nodes)==axon2.axonnodes)
print(len(axon2.x) == axon2.Nsec*2+1)
del axon2
