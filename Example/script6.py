import nrv
import matplotlib.pyplot as plt
import numpy as np

sigma = 0.2
## Axon def
y = 0
z = 0
d = 1
L = 5000
model = "Rattay_Aberham"  # Rattay_Aberham if not precised
axon1 = nrv.unmyelinated(y, z, d, L, model=model)

## test pulse
t_start = 1
duration = 0.5
amplitude = 0.4
axon1.insert_I_Clamp(0.05, t_start, duration, amplitude)

# electrode def
x_elec = 2 * L / 4  # electrode x position, in [um]
y_elec = 100  # electrode y position, in [um]
z_elec = 0  # electrode y position, in [um]


## Simulation
t_sim = 20
results = axon1.simulate(t_sim=t_sim, record_I_mem=True)
del axon1

distance = np.zeros(len(results["x_rec"]))
for k in range(len(distance)):
    distance[k] = np.sqrt(
        (results["x_rec"][k] - x_elec) ** 2 + (y - y_elec) ** 2 + (z - z_elec) ** 2
    )  # distance in um

surface_segment = (np.pi * d * nrv.units.cm * L * nrv.units.cm) / (
    len(results["x_rec"]) - 1
)  # surface of one segment in cm**2 as Neuron computes membrane current in mA/cm**2
epineurium = nrv.load_material("endoneurium_bhadra")
sigma = epineurium.sigma
imid = len(results["V_mem"]) // 2
plt.figure()
for i in range(len(results["V_mem"])):
    plt.plot(results["t"], results["I_mem"][i] * surface_segment, color="k")
plt.xlabel("simulation time ($ms$)")
plt.ylabel("axonal current ($mA$)")
plt.savefig("figures/06_Imembrane.png")

Vspike = []
for t in range(len(results["V_mem"][0])):
    Vspike_t = 0
    for k in range(3, len(results["V_mem"]) - 1):
        Vspike_t += (results["I_mem"][k][t] * surface_segment) / (
            4 * np.pi * sigma * distance[k] * nrv.units.m
        )
    Vspike += [Vspike_t]


plt.figure()
plt.plot(results["t"], Vspike)
plt.xlabel("simulation time ($ms$)")
plt.ylabel("electrode voltage($mV$)")
plt.grid()
plt.xlim(2, 10)
plt.tight_layout()
plt.savefig("figures/06_Vexra.png")
plt.show()
