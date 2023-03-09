import nrv
import numpy as np
import matplotlib.pyplot as plt

# parameters
l = 5000
fname0 = './unitary_tests/sources/131_0.csv'
fname1 = './unitary_tests/sources/131_1.csv'

data0 = np.loadtxt(fname0, delimiter=',')
data1 = np.loadtxt(fname1, delimiter=',')

X0 = data0[0]
Y0 = data0[1]
print(X0, Y0)
X1 = data1[0]
Y1 = data1[1]

dx = 0.0001
N_pts = 100


Y = np.linspace(0, l , N_pts)
X = np.transpose([[0, y] for y in Y])


nrv_eval0 = nrv.nrv_interp(X0, Y0, 'linear', dx=dx, columns=1)
nF_0 = nrv_eval0(X)

nrv_eval1 = nrv.nrv_interp(X1, Y1, 'linear', dx=dx, columns=1)
nF_1 = nrv_eval1(X)


plt.plot(Y, nF_0)
plt.plot(Y, nF_1)
plt.legend()
plt.savefig('./unitary_tests/figures/131_A.png')
#plt.show()
