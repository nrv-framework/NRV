import time
t_1 = time.time()
import nrv


t0 = time.time()
test_num = 308
nerve = nrv.nerve(length= 10000, d= 250)
nerve.set_ID(test_num)
t1 = time.time()

t_sim = 2

nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=0, y=-20, z=-60)#, extracel_context=True)
nerve.add_fascicle('./unitary_tests/sources/300_fascicle_1.json', ID=1, z=65, extracel_context=True)
nerve.fit_circular_contour()
t2= time.time()




position = 0.05
t_start = 5
duration = 0.1
amplitude = 5
nerve.insert_I_Clamp(position, t_start, duration, amplitude)
t3= time.time()
res = nerve.simulate(t_sim=t_sim, save_path='./unitary_tests/figures/')
t4= time.time()
if nrv.MCH.do_master_only_work():
    print(f"import nrv {t0 - t_1}s")
    print(f"Nerve object creation in {t1 - t0}s")
    print(f"Fascicle added in {t2 - t1}s")
    print(f"I clamp inserted in {t3 - t2}s")
    print(f"Simulation done in {t4 - t3}s")

    print(res.fascicle0.keys())
    print(f"Axons properties:\n  fasc_ID\taxon_ID\t myelinated\tdiameter\tz\tz\n {res.axons_pop_properties}")
    print(res.axons_type)