import nrv
import matplotlib.pyplot as plt
import numpy as np

sigma = 0.2
## Axon def
y = 0
z = 0
d = 1
L = 5000
model = "Rattay_Aberham" # Rattay_Aberham if not precised

axon1 = nrv.unmyelinated(y, z, d, L, model=model)

## test pulse
t_start = 1
duration = 0.1
amplitude = 3
axon1.insert_I_Clamp(0.01, t_start, duration, amplitude)

# electrode def
x_elec = L/2				# electrode x position, in [um]
y_elec = 100				# electrode y position, in [um]
z_elec = 0					# electrode y position, in [um]


## Simulation
t_sim = 20
results = axon1.simulate(t_sim=t_sim,record_I_mem=True)
del axon1


imid = len(results['V_mem'])//2
plt.figure()
for i in range(len(results['V_mem'])):
    plt.plot(results['t'],results['I_mem'][i],color='k')
plt.xlabel('simulation time ($ms$)')
plt.ylabel('axonal voltage($mV$)')
plt.savefig('figures/06_Imem_axon.png')
plt.figure()

for i in range(len(results['V_mem'])):
    plt.plot(results['t'],results['V_mem'][i],color='k')
plt.xlabel('simulation time ($ms$)')
plt.ylabel('axonal current ($mA/cm^2$)')
plt.savefig('figures/06_Vmem_axon.png')


Vspike = []
for t in range(len(results['V_mem'][0])):
    Vspike_t = 0
    for k in range(3,len(results['V_mem'])-1):
        x = results['x_rec'][k]
        dist = ((x_elec - x)**2 + (y_elec - y)**2)**0.5
        surface = np.pi * (d/2) ** 2
        Imem = results['I_mem'][k][t] * surface
        Vspike_t += Imem/(4*np.pi*dist)
    Vspike += [Vspike_t]


plt.figure()
plt.plot(results['t'], Vspike)
plt.xlabel('simulation time ($ms$)')
plt.ylabel('electrod voltage($\mu V$)')
plt.savefig('figures/06_Velectrod.png')
plt.show()
