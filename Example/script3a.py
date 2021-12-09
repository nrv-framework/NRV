import nrv
import matplotlib.pyplot as plt


## Axon def
y = 0
z = 0
d = 1
L = 5000
model = "HH" # Rattay_Aberham if not precised

axon1 = nrv.unmyelinated(y, z, d, L, model=model)

## test pulse
t_start = 1
duration = 0.1
amplitude = 5
axon1.insert_I_Clamp(0, t_start, duration, amplitude)

## Simulation

results = axon1.simulate(t_sim=20)
del axon1

nrv.rasterize(results,'V_mem')
unmyelinated_speed = nrv.speed(results, t_start=0)
print(unmyelinated_speed)


## Axon creation
y = 0
z = 0
d = 10
L = nrv.get_length_from_nodes(d,21) # 5000
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

nrv.rasterize(results,'V_mem')
myelinated_speed=nrv.speed(results, t_start=0)
print(myelinated_speed)