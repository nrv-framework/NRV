import nrv

if __name__ == "__main__":
    y = 0
    z = 0
    d = 1
    L = 5000
    
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001)
    results = axon1.simulate()
    del axon1
    print(results['y'] == y)
    print(results['z'] == z)
    print(results['diameter'] == d)
    print(results['L'] == L)