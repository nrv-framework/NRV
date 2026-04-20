import nrv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    y = 0
    z = 0
    d = 10
    L = 20000

    #No APs
    axon0 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')
    results = axon0.simulate(t_sim=8)
    results.rasterize()
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")


    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)


    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_A.png')

    #No collision
    axon1 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp(0.5, 1, duration, amplitude)
    axon1.insert_I_Clamp(0.5,  2.5, duration, amplitude)
    axon1.insert_I_Clamp(0.05, 4, duration, amplitude)


    results = axon1.simulate(t_sim=8)
    results.rasterize()

    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_B.png')


    #with AP collision
    axon2 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2

    axon2.insert_I_Clamp(0.5, 2.01, duration, amplitude)
    axon2.insert_I_Clamp(0.75, 6.01, duration, amplitude)
    axon2.insert_I_Clamp(0.25, 6.0, duration, amplitude)
    axon2.insert_I_Clamp(0.75, 8.01, duration, amplitude)
    axon2.insert_I_Clamp(0.25, 8.0, duration, amplitude)
    results = axon2.simulate(t_sim=10)

    results.rasterize()
    x_APs,_,t_APs,_ = results.split_APs()

    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_C.png')


    axon3 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon3.insert_I_Clamp(0.5, 2.01, duration, amplitude)
    axon3.insert_I_Clamp(0.75, 6.0, duration, amplitude)
    axon3.insert_I_Clamp(0.25, 6.01, duration, amplitude)
    results = axon3.simulate(t_sim=6.5)
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_D.png')


    axon4 = nrv.myelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon4.insert_I_Clamp(0.75, 6.0, duration, amplitude)
    axon4.insert_I_Clamp(0.25, 6.0, duration, amplitude)
    results = axon4.simulate(t_sim=8)
    results.rasterize(clear_artifacts=False)
    x_APs,_,t_APs,_ = results.split_APs()


    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_E.png')

    d = 0.5
    L = 2000

    #No APs
    axon0 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')
    results = axon0.simulate(t_sim=8)
    results.rasterize()
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_F.png')

    #No collision
    axon1 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon1.insert_I_Clamp(0.5, 1, duration, amplitude)
    axon1.insert_I_Clamp(0.5,  2.5, duration, amplitude)
    axon1.insert_I_Clamp(0.05, 6, duration, amplitude)


    results = axon1.simulate(t_sim=8)
    results.rasterize()
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_G.png')


    #with AP collision
    axon2 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2

    axon2.insert_I_Clamp(0.5, 2.01, duration, amplitude)
    axon2.insert_I_Clamp(0.75, 6.01, duration, amplitude)
    axon2.insert_I_Clamp(0.25, 6.0, duration, amplitude)
    results = axon2.simulate(t_sim=8)

    results.rasterize()
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_H.png')


    axon3 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon3.insert_I_Clamp(0.5, 2.01, duration, amplitude)
    axon3.insert_I_Clamp(0.75, 6.0, duration, amplitude)
    axon3.insert_I_Clamp(0.25, 6.01, duration, amplitude)
    results = axon3.simulate(t_sim=8)
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_I.png')


    axon4 = nrv.unmyelinated(y,z,d,L,dt=0.005,rec='all')
    t_start = 2
    duration = 0.1
    amplitude = 2
    axon4.insert_I_Clamp(0.75, 6.0, duration, amplitude)
    axon4.insert_I_Clamp(0.25, 6.0, duration, amplitude)
    results = axon4.simulate(t_sim=8)
    x_APs,_,t_APs,_ = results.split_APs()
    print(f"Number of APs detected: {results.count_APs()}")
    print(f"APs reached end: {results.APs_reached_end()}")
    print(f"APs reached end within the timeframe: {results.APs_in_timeframe()}")
    print(f"InterAP collision detected: {results.detect_AP_collisions()}")
    if (results.count_APs()):
        print(f"AP propagation velocity: {results.getAPspeed()[0]}m/s")

    fig, ax = plt.subplots(1)
    results.plot_x_t(ax)

    fig, ax = plt.subplots(1)
    results.raster_plot(ax,s=80)

    for x_AP,t_AP in zip(x_APs,t_APs):
        ax.scatter(t_AP,x_AP)
        x_start,t_start = results.get_start_AP(x_AP,t_AP)
        x_max,t_xmax = results.get_xmax_AP(x_AP,t_AP)
        x_min,t_xmin = results.get_xmin_AP(x_AP,t_AP)
        ax.scatter(t_start,x_start,s=10,c = 'k')
        ax.scatter(t_xmax,x_max,s=10,c = 'g')
        ax.scatter(t_xmin,x_min,s=10,c = 'b')

    if results.detect_AP_collisions():
        x_coll,t_coll,_ = results.get_collision_pts()
        ax.scatter(t_coll,x_coll,s=50,c = 'r')

    ax.set_xlabel('time (ms)')
    ax.set_ylabel(r'position along the axon($\mu m$)')
    ax.set_xlim(0,results['tstop'])
    fig.savefig('./unitary_tests/figures/524_J.png')



# plt.show()