import nrv
# Note : every print should be true

y = 0
z = 0
d = 10
L = 5000

# test 1:  
axon1 = nrv.myelinated(y,z,d,L,dt=0.001,Nseg_per_sec=1,node_shift = 0.49)
print(len(axon1.node)==4)
print(len(axon1.MYSA)==2*len(axon1.node))
print(len(axon1.FLUT)==2*len(axon1.node))
print(len(axon1.STIN)>6*len(axon1.node))
axon1.topology()
del axon1

# test 2: 
axon2 = nrv.myelinated(y,z,d,L,dt=0.001,Nseg_per_sec=1,node_shift = 0.002)
print(len(axon2.node)==5)
axon2.topology()
del axon2

# test 3:
axon3 = nrv.myelinated(y,z,d,L,dt=0.001,Nseg_per_sec=1,rec='nodes')
print(len(axon3.node)==5)
axon3.topology()
print(len(axon3.node)==axon3.axonnodes)
print(len(axon3.MYSA)==axon3.paranodes1)
print(len(axon3.FLUT)==axon3.paranodes2)
print(len(axon3.STIN)==axon3.axoninter)
print(axon3.Nsec == axon3.axonnodes + axon3.paranodes1 + axon3.paranodes2 + axon3.axoninter)
print(len(axon3.axon_path_type) == len(axon3.axon_path_index))
print(len(axon3.axon_path_type) == axon3.Nsec)
print(axon3.axon_path_type)
print(axon3.axon_path_index)
#print(axon3.x)
#print(axon3.x_nodes)
print(axon3.x_rec == axon3.x_nodes)
print(len(axon3.x_nodes)==axon3.axonnodes)
low_seg = len(axon3.x)
print(len(axon3.x) == axon3.Nsec*2+1)
del axon3

# test 4:
axon4 = nrv.myelinated(y,z,d,L,dt=0.001,rec='all')
print(len(axon4.x)>low_seg)
mid_seg = len(axon4.x)
print(axon4.x_rec == axon4.x)
del axon4

# test 5:
axon5 = nrv.myelinated(y,z,d,L,dt=0.001,freq=1e3,freq_min=1e2)
print(len(axon5.x) > mid_seg)
del axon5