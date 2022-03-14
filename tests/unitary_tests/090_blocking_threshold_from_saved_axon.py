import nrv

try:
    axon1, _ = nrv.load_any_axon('./unitary_tests/sources/89_axon.json', extracel_context=True)
except:
    axon1, _ = nrv.load_any_axon('./sources/89_axon.json', extracel_context=True)

threshold = nrv.blocking_threshold_from_axon(axon1,block_freq=10,amp_max=500,amp_tol=5)
print(threshold)
