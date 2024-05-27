import nrv 
import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter
import sys

nrv.parameters.set_gmsh_ncore(4)

nerve = nrv.load_any("nerve_benchmark.json",intracel_context=True, extracel_context=True, rec_context=True)

nerve.save_results = False
nerve.return_parameters_only = False
nerve.verbose = True


t1_start = perf_counter() 
nerve_results = nerve(t_sim=5,postproc_script = "AP_detection")         #Run the simulation

t1_stop = perf_counter()



if nrv.MCH.do_master_only_work():
    nerve.extra_stim.model.get_timers()
    mesh_t = nerve.extra_stim.model.meshing_timer
    setup_t = nerve.extra_stim.model.setup_timer
    solve_t = nerve.extra_stim.model.solving_timer
    dispatch_t = nerve.extra_stim.model.access_res_timer
    total = t1_stop-t1_start
    neuron_t = total-(mesh_t+setup_t+solve_t+dispatch_t)
    fig, ax = plt.subplots(1, 1, figsize=(6,6))
    nerve_results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    print(f"total: {np.round(total,3)}s")
    print(f"mesh_t: {np.round(mesh_t,3)}s")
    print(f"setup_t: {np.round(setup_t,3)}s")
    print(f"solve_t: {np.round(solve_t,3)}s")
    print(f"dispatch_t: {np.round(dispatch_t,3)}s")
    print(f"neuron_t: {np.round(neuron_t,3)}s")
    sys.stdout.flush()



    #plt.show()
