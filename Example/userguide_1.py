import nrv

# Axon definition
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
assert axon2.L == L

del axon2


axon3 = nrv.unmyelinated()
axon3.load(filename)
assert axon3.L == L


## Instantiate an nrv object

# From the class (the python way):
axon1 = nrv.unmyelinated(y,z,d,L)
assert axon1.L == L
del axon1

# From the class (the dictionary way):
axon1 = nrv.unmyelinated(**ax_dict)
assert axon1.L == L
del axon1

# From a file (the json way):
axon1 = nrv.unmyelinated()
axon1.load(filename)
assert axon1.L == L
del axon1

# From anything (the easy way):
axon1 = nrv.load_any(ax_dict)
assert axon1.L == L
del axon1

axon1 = nrv.load_any(filename)
assert axon1.L == L
del axon1



