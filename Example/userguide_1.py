import nrv

y = 0                       # axon y position, in [um]
z = 0                       # axon z position, in [um]
d = 1                       # axon diameter, in [um]
L = 1250                   # axon length, along x axis, in [um]
axon1 = nrv.unmyelinated(y,z,d,L)

ax_dict = axon1.save()

filename = "ax_file.json"
ax_dict = axon1.save(save=True, fname=filename)


del axon1

axon2 = nrv.unmyelinated()
axon2.load(ax_dict)
print(axon2.L == L)

del axon2


axon3 = nrv.unmyelinated()
axon3.load(filename)
print(axon3.L == L)