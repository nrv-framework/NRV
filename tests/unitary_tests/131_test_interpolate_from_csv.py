import nrv
import numpy as np
import matplotlib.pyplot as plt

# parameters
l = 5000
fname0 = './unitary_tests/sources/131_0.csv'
fname1 = './unitary_tests/sources/131_1.csv'

data0 = np.loadtxt(fname0, delimiter=',')
data1 = np.loadtxt(fname1, delimiter=',')
N = len(data0[0])
dx = 0.0001
N_pts = 10


X0 = data0[0]
print(N)
X0 = np.array([X0[k*N//N_pts] for k in range(N_pts)])
Y0 = data0[1]
Y0 = np.array([Y0[k*N//N_pts] for k in range(N_pts)])
print(X0, Y0)

X1 = data1[0]
X1 = np.array([X1[k*N//N_pts] for k in range(N_pts)])
Y1 = data1[1]
Y1 = np.array([Y1[k*N//N_pts] for k in range(N_pts)])

Y = np.linspace(0, l , 1000)
X = np.transpose([[0, y] for y in Y])


nrv_eval0 = nrv.nrv_interp(X0, Y0, 'cardinal',scale=0.5, dx=dx, columns=1)
nF_0 = nrv_eval0(X)

nrv_eval1 = nrv.nrv_interp(X1, Y1, 'cardinal',scale=0.5, dx=dx, columns=1)
nF_1 = nrv_eval1(X)


plt.plot(Y, nF_0)
plt.plot(Y, nF_1)
plt.legend()
plt.savefig('./unitary_tests/figures/131_A.png')
#plt.show()
