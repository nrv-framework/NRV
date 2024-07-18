import nrv

y = 0
z = 0
d = 1
L = 50
 
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.01)
results = axon1.simulate(t_sim=1)
del axon1

results.remove_key('ID')
results.save(save=True, fname='./unitary_tests/sources/26_test_svg.json')

