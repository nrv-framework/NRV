import nrv

y = 0
z = 0
d = 1
L = 50
 
axon1 = nrv.unmyelinated(y,z,d,L,dt=0.01)
results = axon1.simulate(t_sim=1)
del axon1

nrv.remove_key(results,'ID')
nrv.save_axon_results_as_json(results,'./unitary_tests/figures/test_svg.json')
