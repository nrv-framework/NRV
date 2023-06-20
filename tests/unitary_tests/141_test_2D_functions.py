import nrv
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

## Results filenames
fig_file1 = "./unitary_tests/figures/141_A.png"
fig_file2 = "./unitary_tests/figures/141_B.png"
fig_file3 = "./unitary_tests/figures/141_C.png"
fig_file4 = "./unitary_tests/figures/141_D.png"



# functions
S = nrv.sphere()


N_x=100
t = np.linspace(-10,10, N_x) 
X,Y,Z = np.meshgrid(t, t, t) # grid of point
#Z = S(X, Y)
V = S(X, Y, Z) + 1
plt.figure()
im = plt.imshow(V[:,:,0],cmap=mpl.cm.viridis)
plt.savefig(fig_file1)


S1 = nrv.sphere(Xc=[3, 2])
S2 = nrv.sphere(Xc=[-1, -4])
S3 = S1 + S2 * 2
X,Y = np.meshgrid(t, t) # grid of point

print(dir(S2))
plt.figure()
im = plt.imshow(S3(X,Y),cmap=mpl.cm.viridis)
plt.savefig(fig_file2)


# Composition
G = nrv.gaussian(mu=5, sigma=0.5)
V = G(S1) + G(S2)

plt.figure()
im = plt.imshow(V(X,Y),cmap=mpl.cm.viridis)
plt.savefig(fig_file3)


#plt.show()
