import nrv
import matplotlib.pyplot as plt
import numpy as np

unmyelinated_diameters = np.linspace(0.5, 1, 10)
myelinated_diameters = np.linspace(6, 16, 16)

unmyelinated_speed = []
myelinated_speed = []

for d in unmyelinated_diameters:
    ## Axon def
    y = 0
    z = 0
    L = 5000
    model = "HH"  # Rattay_Aberham if not precised

    axon1 = nrv.unmyelinated(y, z, d, L, model=model)

    ## test pulse
    t_start = 1
    duration = 0.1
    amplitude = 3
    axon1.insert_I_Clamp(0, t_start, duration, amplitude)

    ## Simulation

    results = axon1.simulate(t_sim=20)
    del axon1

    nrv.rasterize(results, "V_mem")
    unmyelinated_speed += [nrv.speed(results, t_start=0)]

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_speed, "o-", label="unmyelinated")
plt.legend()
plt.grid()
plt.xlabel("diameter ($\mu m$)")
plt.ylabel("speed ($m.s^{-1}$)")
plt.savefig("figures/03_unmyelinatedspeed.png")
print(unmyelinated_speed)


for d in myelinated_diameters:
    ## Axon def
    y = 0
    z = 0
    L = nrv.get_length_from_nodes(d, 21)  # 5000
    model = "MRG"

    axon1 = nrv.myelinated(y, z, d, L, model=model)

    ## test pulse
    t_start = 1
    duration = 0.1
    amplitude = 5
    axon1.insert_I_Clamp(0, t_start, duration, amplitude)

    ## Simulation

    results = axon1.simulate(t_sim=20)
    del axon1

    nrv.rasterize(results, "V_mem")
    myelinated_speed += [nrv.speed(results, t_start=0)]

plt.figure()
plt.plot(myelinated_diameters, myelinated_speed, "o-", label="myelinated")
plt.legend()
plt.grid()
plt.xlabel("diameter ($\mu m$)")
plt.ylabel("speed ($m.s^{-1}$)")
plt.savefig("figures/03_myelinatedspeed.png")
print(unmyelinated_speed)
print(myelinated_speed)


plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_speed, "o-", label="unmyelinated")
plt.plot(myelinated_diameters, myelinated_speed, "o-", label="myelinated")
plt.legend()
plt.grid()
plt.xlabel("diameter ($\mu m$)")
plt.ylabel("speed ($m.s^{-1}$)")
plt.savefig("figures/03_speed.png")

plt.figure()
plt.plot(unmyelinated_diameters, unmyelinated_speed, "o-", label="unmyelinated")
plt.plot(myelinated_diameters, myelinated_speed, "o-", label="myelinated")
plt.legend()
plt.xscale("log")
plt.yscale("log")
plt.grid()
plt.xlabel("diameter ($\mu m$)")
plt.ylabel("speed ($m.s^{-1}$)")
plt.savefig("figures/03_speed_log.png")
