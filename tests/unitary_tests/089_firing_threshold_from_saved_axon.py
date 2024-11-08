import nrv

if __name__ == "__main__":
    try:
        axon1, _ = nrv.load_any_axon('./unitary_tests/sources/89_axon.json', extracel_context=True)
    except:
        axon1, _ = nrv.load_any_axon('./sources/89_axon.json', extracel_context=True)

    threshold = nrv.firing_threshold_from_axon(axon1,cath_time= 100e-3,amp_max=200,amp_tol=5)
    print(threshold)