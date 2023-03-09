import nrv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, CubicSpline, CubicHermiteSpline

# parameters
l = 20



dx = 0.0001
N_pts = 10
X_value = np.sort(np.concatenate((l*np.random.rand(N_pts-2),[0, l])))
print(X_value)
for i, x in enumerate(X_value):
    if i >0:
        while x<X_value[i-1]:
            x += dx
        X_value[i] = x

print(X_value)
Y_value = np.random.randint(-50, high=50, size=N_pts)
dxdy = np.array([(Y_value[1]-Y_value[0])/X_value[1]-X_value[0]]+[(Y_value[k+2]-Y_value[k])/(X_value[k+2]-X_value[k]) for k in range(N_pts-2)]+[(Y_value[-1]-Y_value[-2])/(X_value[-1]-X_value[-2])])

#X_value = np.array([0, 1-dx, 1+dx, 3, l])
#Y_value = np.array([1, 10, 5, 5, 3])
#dxdy = np.array([0, 4, -5, -2, 0])


def eval_sigmid2(X):
    li = interp1d(X_value, Y_value, kind='linear', bounds_error=False,fill_value=1)
    return(li(X[1]))

def eval_sigmid3(X, alpha):
    chs = CubicHermiteSpline(X_value, Y_value, alpha*dxdy)
    return(chs(X[1]))

N_p = 1001
Y = [l * k/N_p for k in range(N_p)]
X = np.transpose([[0, y] for y in Y])

F_1 = eval_sigmid2(X)
F_2 = eval_sigmid3(X, 0)
F_3 = eval_sigmid3(X, 0.5)
F_4 = eval_sigmid3(X, 1)

nrv_eval1 = nrv.nrv_interp(X_value, Y_value, 'linear', dx=dx, columns=1)
nF_1 = nrv_eval1(X)

nrv_eval2 = nrv.nrv_interp(X_value, Y_value, 'cardinal', dx=dx, scale=0, columns=1)
nF_2 = nrv_eval2(X)

nrv_eval2.update_interpolator(kind='catmull-rom')
nF_3 = nrv_eval2(X)

nrv_eval2.update_interpolator(kind='cardinal', scale=1)
nF_4 = nrv_eval2(X)

print(np.allclose(F_1, nF_1))
print(np.allclose(F_2, nF_2))
print(np.allclose(F_3, nF_3))
print(np.allclose(F_4, nF_4))

plt.figure()
plt.plot(Y, nF_1, label='F_1')
plt.plot(Y, nF_2, label='F_2')

plt.plot(Y, nF_3, label='F_3')
plt.plot(Y, nF_4, label='F_4')
plt.plot(X_value, Y_value, 'o', label='points')
plt.plot([0], [0], 'k', label='derivatives')
for i in range(N_pts):
    plt.plot([X_value[i], X_value[i]+1], [Y_value[i], Y_value[i]+dxdy[i]], 'k')
plt.legend()
plt.savefig('./unitary_tests/figures/130_A.png')

#plt.show()
