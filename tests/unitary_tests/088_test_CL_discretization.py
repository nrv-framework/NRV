import nrv

####Find time/spatial discretization parameters for a spike threshold search with 100us pulse and MRG model. Tolerance is 5%
tol = 5
model='MRG'
simulation_category = 'Spike_threshold'
pw = 100e-3

dt = nrv.Get_dt(tol,model,simulation_category,stim_pw = pw)

nrv.pass_info("Suggested dt is " + str(round(dt,3)) + "ms")

nseg = nrv.Get_nseg(tol,model,simulation_category)

nrv.pass_info("Suggested nseg is " + str(nseg) + " segments per section")
