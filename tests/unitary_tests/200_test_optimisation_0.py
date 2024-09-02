import nrv.utils._nrv_function as oobj
import numpy as np
import matplotlib.pyplot as plt

############################################################
# test identity
print('\t ... testing identity function')
print(oobj.Id()(1,2,3) == (1,2,3))
############################################################
# test Rosenbock
print('\t ... testing Rosenbock function')
N_points = 500
x = np.linspace(-2,2,N_points)
y = np.linspace(-2,2,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.rosenbock()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, np.log10(z) ,shading='auto')
plt.contour(x, y, np.log10(z), 5, colors='w')
plt.title('Rosenbock in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_A.png')

############################################################
# test Rastrigin
print('\t ... testing Rastrigin function')
N_points = 500
x = np.linspace(-5.12,5.12,N_points)
y = np.linspace(-5.12,5.12,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.rastrigin()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, z ,shading='auto')
plt.contour(x, y, z, 5, colors='w')
plt.title('Rastrigin in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_B.png')

############################################################
# test Sphere
print('\t ... testing Sphere function')
N_points = 500
x = np.linspace(-5,5,N_points)
y = np.linspace(-5,5,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.sphere()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, z ,shading='auto')
plt.contour(x, y, z, 5, colors='w')
plt.title('Sphere in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_C.png')


############################################################
# test Ackley
print('\t ... testing Ackley function')
N_points = 500
x = np.linspace(-5.,5.,N_points)
y = np.linspace(-5.,5.,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.ackley()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, z ,shading='auto')
plt.contour(x, y, z, 5, colors='w')
plt.title('Ackley in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_D.png')

############################################################
# test Beale
print('\t ... testing Beale function')
N_points = 500
x = np.linspace(-4.5,4.5,N_points)
y = np.linspace(-4.5,4.5,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.beale()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, np.log10(z) ,shading='auto')
plt.contour(x, y, np.log10(z), 5, colors='w')
plt.title('Beale in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_E.png')

############################################################
# test Goldstein-price
print('\t ... testing Goldstein-price function')
N_points = 500
x = np.linspace(-2.,2.,N_points)
y = np.linspace(-3.,1.,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.goldstein_price()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, np.log10(z) ,shading='auto')
plt.contour(x, y, np.log10(z), 5, colors='w')
plt.title('Goldstein-price in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_F.png')

############################################################
# test Booth
print('\t ... testing Booth function')
N_points = 500
x = np.linspace(-10.,10.,N_points)
y = np.linspace(-10.,10.,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.booth()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, np.log10(z) ,shading='auto')
plt.contour(x, y, np.log10(z), 5, colors='w')
plt.title('Booth in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_G.png')

############################################################
# test Bukin6
print('\t ... testing Bukin6 function')
N_points = 500
x = np.linspace(-15.,-5,N_points)
y = np.linspace(-4,6.,N_points)

z = np.zeros((N_points, N_points))
for i in range(N_points):
    for j in range(N_points):
        z[i, j] = oobj.bukin6()(x[i], y[j])

plt.figure()
map = plt.pcolormesh(x, y, np.log10(z) ,shading='auto')
plt.contour(x, y, np.log10(z), 5, colors='w')
plt.title('Booth in 2D')
plt.xlabel('x')
plt.ylabel('y')
cbar = plt.colorbar(map)
cbar.set_label('z')
plt.tight_layout()
plt.savefig('./unitary_tests/figures/200_G.png')
