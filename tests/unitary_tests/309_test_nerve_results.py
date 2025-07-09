import time

test_dir = "./unitary_tests/"
__fname__ = __file__[__file__.find(test_dir)+len(test_dir):]
test_num = __fname__[:__fname__.find("_")]

figdir = "unitary_tests/figures/" + test_num + "_"
source_file = './unitary_tests/sources/300_fascicle_1.json'


if __name__ == "__main__":
    t_1 = time.time()
    import nrv
    t0 = time.time()

    nerve = nrv.nerve(length= 10000, diameter= 500)
    nerve.set_ID(test_num)
    t1 = time.time()

    t_sim = 10
    nerve.add_fascicle(source_file, ID=0, y=-20, z=-60)#, extracel_context=True)
    nerve.add_fascicle(source_file, ID=1, z=65, extracel_context=True)
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
    print(f"import nrv {t0 - t_1}s")
    print(f"Nerve object creation in {t1 - t0}s")
    print(f"Fascicle added in {t2 - t1}s")
    print(f"I clamp inserted in {t3 - t2}s")
    print(f"Simulation done in {t4 - t3}s")

    print(res.fascicle1.keys())
    print(f"Axons properties:\n  fasc_ID\taxon_ID\t myelinated\tdiameter\tz\tz\n {res.axons}")
    print(res.axons["types"])