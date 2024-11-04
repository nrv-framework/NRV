import nrv
# Note : every print should be true

if __name__ == "__main__":
    y = 0
    z = 0
    d = 1
    L = 5000

    # test 1: 3 sections of 5 segments 
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.001,Nsec=3,Nseg_per_sec=5)
    print(len(axon1.x) == axon1.Nsec + axon1.Nseg + 1)