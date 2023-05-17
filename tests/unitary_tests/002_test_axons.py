'''
test the axon object
'''
import nrv

x = 1
y = 2
d = 3
L = 5000
try:
    ax1 = nrv.axon(x,y,d,L)
    print(False)
except:
    ax1 = nrv.axon_test(x,y,d,L)
    print(True)

del ax1