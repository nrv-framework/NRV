import nrv
import numpy as np

nrv.print_default_nrv_unit()

# Three way to convert 4530 (default unit) to 4.53mm
val_default = 4530 # um
val_mm1 = val_default / nrv.mm
val_mm2 = nrv.from_nrv_unit(val_default, nrv.mm)
val_mm3 = nrv.from_nrv_unit(val_default, "mm")

print(np.isclose(val_mm1, 4.53))
print(np.isclose(val_mm2, 4.53))
print(np.isclose(val_mm3, 4.53))

# Three way to convert 0.12 MHz to the corresponding nrv unit (kHz)
val_MHz = 0.12 # um
val_default1 = val_MHz * nrv.MHz
val_default2 = nrv.to_nrv_unit(val_MHz, nrv.MHz)
val_default3 = nrv.to_nrv_unit(val_MHz, "MHz")

print(np.isclose(val_default1, 120))
print(np.isclose(val_default2, 120))
print(np.isclose(val_default3, 120))

# Iterable can also be converted from and to rv units
vals_s = [[3*i+j for j in range(3)] for i in range(2)]
val_np_s = np.array(vals_s)
vals_default = [[(3 * i + j) * nrv.s for j in range(3)] for i in range(2)]
print(np.allclose(nrv.to_nrv_unit(vals_s, nrv.s), vals_default))
print(np.allclose(nrv.to_nrv_unit(val_np_s, nrv.s), vals_default))

# Finally you can also use nrv.sci_round to round numbers keeping a specifyed number of significant digits
A = 1+np.random.rand(2, 2)
print(A)
print("  || (3 sig figs)")
print("  \\/ ")
print(nrv.sci_round(A, 3))