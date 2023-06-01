import nrv
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf

## Results filenames
fig_file1 = "./unitary_tests/figures/138_A.png"
fig_file2 = "./unitary_tests/figures/138_B.png"
fig_file3 = "./unitary_tests/figures/138_C.png"
fig_file4 = "./unitary_tests/figures/138_D.png"

## Mesh generation
L = 2000
X = np.linspace(0,L,10000)
mu = L/2
sigma = L/20
N = 20


g1 = nrv.gaussian(mu, sigma)
g2 = nrv.gaussian(mu, sigma*5)
g3 = nrv.gaussian(mu/2, sigma)
g4 = nrv.gaussian(mu, sigma/2)

plt.figure()
plt.plot(X, g1(X), label="$\mu =$" + str(int((mu))) + ", $\sigma =$" + str(int((sigma))))
plt.plot(X, g2(X), label="$\mu =$" + str(int((mu))) + ", $\sigma =$" + str(int((sigma*5))))
plt.plot(X, g3(X), label="$\mu =$" + str(int((mu/2))) + ", $\sigma =$" + str(int((sigma))))
plt.plot(X, g4(X), label="$\mu =$" + str(int((mu))) + ", $\sigma =$" + str(int((sigma/2))))
plt.grid()
plt.legend()
plt.savefig(fig_file1)


sigma = L/3
g = nrv.gate(mu, sigma)
g = 1 - g

plt.figure()
X_eff = (X-mu)/sigma

for i in range(1,20):
    gi = nrv.gate(mu, sigma, N=i)
    plt.plot(X, 1/((2*X_eff)**(2*i)+1))
    plt.plot(X, gi(X), 'k:')

plt.plot(X, g(X), 'k')
plt.grid()

plt.figure()
for i in range(1,20):
    gi = 1 - nrv.gate(mu, sigma, kind='erf',N=1/i)
    plt.plot(X, gi(X))
plt.plot(X, g(X), 'k')
plt.grid()


plt.figure()

g = nrv.gate(mu, sigma)
g1 = nrv.gaussian(mu, sigma)
g2 = 1 - nrv.gate(mu/2, sigma,N=10)
g3 = 1 - nrv.gate(3*mu/2, sigma,N=3)
G =  g * g1 + g2 - g3

plt.plot(X, g(X), ':')
plt.plot(X, g1(X), ':')
plt.plot(X, g2(X), ':')
plt.plot(X, -g3(X), ':')
plt.plot(X, G(X), 'k')
plt.grid()
plt.show()
