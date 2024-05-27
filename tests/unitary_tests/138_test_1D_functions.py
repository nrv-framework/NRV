import nrv
import time
import numpy as np
import matplotlib.pyplot as plt

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

print(g1(mu)==1)

plt.figure()
plt.plot(X, g1(X), label=r"$\mu =$" + str(int((mu))) + r", $\sigma =$" + str(int((sigma))))
plt.plot(X, g2(X), label=r"$\mu =$" + str(int((mu))) + r", $\sigma =$" + str(int((sigma*5))))
plt.plot(X, g3(X), label=r"$\mu =$" + str(int((mu/2))) + r", $\sigma =$" + str(int((sigma))))
plt.plot(X, g4(X), label=r"$\mu =$" + str(int((mu))) + r", $\sigma =$" + str(int((sigma/2))))
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
plt.savefig(fig_file2)

plt.figure()
for i in range(1,20):
    gi = 1 - nrv.gate(mu, sigma, kind='erf',N=1/i)
    plt.plot(X, gi(X))
plt.plot(X, g(X), 'k')
plt.grid()
plt.savefig(fig_file3)


g = nrv.gate(mu, sigma)
g1 = nrv.gaussian(mu, sigma)
g2 = 1 - nrv.gate(mu/2, sigma,N=10)
g3 = 1 - nrv.gate(3*mu/2, sigma,N=3)
G =  g * g1 + g2 - g3
print(type(G))

fig, axs = plt.subplots(2)
axs[0].plot(X, g(X), ':')
axs[0].plot(X, g1(X), ':')
axs[0].plot(X, g2(X), ':')
axs[0].plot(X, -g3(X), ':')
axs[0].plot(X, G(X), 'k')
axs[0].set_xticks([])
axs[0].grid()


p = -nrv.gate()
P_G = -(p(G) + 2)

axs[1].plot(X, G(X), ':')
axs[1].axhspan(-0.5, 0.5, alpha=0.2, color='gray')
axs[1].set_xlim((X[0], X[-1]))
axs[1].plot(X, P_G(X))
plt.savefig(fig_file4)
#plt.show()
