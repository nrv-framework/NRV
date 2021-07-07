import nrv

y = 0
z = 0
d = 1
L = 5000

# test 1: 1 section 10 segments
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nsec=1,Nseg_per_sec=10)
print(axon1.Nseg == 10)
del axon1
# test 2: 1 section dlambda rule
axon2 = nrv.unmyelinated(y,z,d,L,dt=0.001)
print(axon2.Nsec == 1)
Nseg_ref = axon2.Nseg # should be 251
print(axon2.Nseg == 179)
del axon2
# test 3: 4 sections dlambda rule
axon3 = nrv.unmyelinated(y,z,d,L,Nsec=4)
print(L == axon3.unmyelinated_sections[0].L+axon3.unmyelinated_sections[1].L+axon3.unmyelinated_sections[2].L+axon3.unmyelinated_sections[3].L)
print(axon3.Nseg == 180)
del axon3
# test 4: 3 sections 10 segments per section
axon4 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nsec=3,Nseg_per_sec=10)
print(L == axon4.unmyelinated_sections[0].L+axon4.unmyelinated_sections[1].L+axon4.unmyelinated_sections[2].L)
print(axon4.Nseg == 30)
del axon4
# test 5: 100 sections, adaptive dlambda rule
axon5 = nrv.unmyelinated(y,z,d,L,Nsec=100,freq=1e3,freq_min=1e2)
print(axon5.Nseg > Nseg_ref)
del axon5