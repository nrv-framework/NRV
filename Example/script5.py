import nrv
import numpy as np
import matplotlib.pyplot as plt

unmyelinated_diameters = np.linspace(0.5,2,8)
myelinated_diameters = np.linspace(6,20,num=16)

unmyelinated_threshold = []
myelinated_threshold = []

material = 'endoneurium_bhadra'
dist_elec = 500
dt=0.005

# unmyelinated 
print('----| Unmyelinated |----')

model = 'HH'
L = 5000
amp_max = 18000

for d in unmyelinated_diameters:
    threshold = nrv.firing_threshold(d,L,material,dist_elec,amp_tol=1,model=model,\
        amp_max=amp_max, dt=dt, verbose=False)
    unmyelinated_threshold += [threshold]
    print("diam =", d,'um : thres= ', threshold, "uA")

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold,  'o-', label='unmyelinated')
plt.xlabel('diameter ($\mu m$)')
plt.ylabel('firing thershold ($\mu A$)')
plt.legend()
plt.grid()
plt.savefig('figures/05_unmyelinated_threshold.png')

# myelinated
print('----| Myelinated |----')

model = 'MRG'
amp_max=500

for d in myelinated_diameters:
    L = nrv.get_length_from_nodes(d,21)
    x_elec = nrv.get_length_from_nodes(d,10)
    position = x_elec/L

    threshold = nrv.firing_threshold(d,L,material,dist_elec,position_elec=position,\
        amp_tol=1, amp_max=amp_max, model=model, dt=dt, verbose=False)
    myelinated_threshold += [threshold]
    print("diam =", d,'um : thres= ', threshold, "uA")


plt.figure()
plt.plot(myelinated_diameters, myelinated_threshold, 'o-r', label='myelinated')
plt.xlabel('diameter ($\mu m$)')
plt.ylabel('firing thershold ($\mu A$)')
plt.legend()
plt.grid()
plt.savefig('figures/05_myelinated_threshold.png')

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold,  'o-', label='unmyelinated')
plt.plot(myelinated_diameters, myelinated_threshold, 'o-', label='myelinated')
plt.xlabel('diameter ($\mu m$)')
plt.ylabel('firing thershold ($\mu A$)')
plt.legend()
plt.grid()
plt.savefig('figures/05_threshold.png')

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_threshold, 'o-', label='unmyelinated')
plt.plot(myelinated_diameters, myelinated_threshold, 'o-', label='myelinated')
plt.xlabel('diameter ($\mu m$)')
plt.ylabel('firing thershold ($\mu A$)')
plt.legend()
plt.xscale('log')
plt.yscale('log')
plt.grid()
plt.savefig('figures/05_threshold_log.png')
