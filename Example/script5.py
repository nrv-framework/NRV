import nrv
import numpy as np
import matplotlib.pyplot as plt

unmyelinated_diameters = np.linspace(0.1,1,5)
myelinated_diameters = np.linspace(6,14,8)

unmyelinated_threshold = []
myelinated_threshold = []

for d in unmyelinated_diameters:
    model = 'HH'
    L = 50000
    material = 'endoneurium_bhadra'
    dist_elec = 500

    unmyelinated_threshold += [nrv.firing_threshold(d,L,material,dist_elec,amp_tol=1,model=model)]

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold,  'o-', label='unmyelinated')
plt.legend()
plt.grid()
plt.savefig('figures/05_unmyelinated_threshold.png')

for d in myelinated_diameters:
    model = 'MRG'
    L = 50000
    material = 'endoneurium_bhadra'
    dist_elec = 500

    myelinated_threshold += [nrv.firing_threshold(d,L,material,dist_elec,amp_tol=1,model=model)]


plt.figure()
plt.plot(myelinated_diameters, myelinated_threshold, 'o-r', label='myelinated')
plt.legend()
plt.grid()
plt.savefig('figures/05_myelinated_threshold.png')

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold,  'o-', label='unmyelinated')
plt.plot(myelinated_diameters, myelinated_threshold, 'o-', label='myelinated')
plt.legend()
plt.grid()
plt.savefig('figures/05_threshold.png')

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold, 'o-', label='unmyelinated')
plt.plot(myelinated_diameters, myelinated_threshold, 'o-', label='myelinated')
plt.legend()
plt.xscale('log')
plt.yscale('log')
plt.grid()
plt.savefig('figures/05_threshold_log.png')
